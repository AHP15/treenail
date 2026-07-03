#!/usr/bin/env python3
"""reconcile.py — compute the implementation view per decision and resolve
Evidence anchors against the working tree (deterministic, read-only).

This is the mechanical half of the `reconcile-status` skill. The view
derivation (mapping each accepted decision to implemented / partial /
in_progress / not_started / reversed / uncovered from current task
statuses) and the Evidence-anchor resolution (does the code a `done` task
points at actually exist in the tree?) are PURELY mechanical, and
plan↔code drift is the highest-signal output the pipeline produces — so,
exactly like `audit.py` for structural invariants, it belongs in a script
rather than in LLM prose, where a model could "believe" an anchor resolves
without running the search and where two runs could disagree.

The skill keeps the judgment layer on top: what to DO about an anomaly,
and the quality smells in `reconcile_smells.py`. This script writes
nothing — implementation status is never stored, it is derived on read.

Anchors are resolved with ripgrep when available, falling back to a pure
Python walk, so a missing `rg` degrades but never crashes.

Usage:
    reconcile.py <scope-dir> [--root <repo-root>]

  <scope-dir>  docs root for the scope, e.g. `docs` or
               `docs/features/<feature>`.
  --root       repo root that Evidence paths are relative to (default: the
               current directory, which is where the skills are run from).

Exit codes:
  0  computed cleanly (no implementation drift)
  1  implementation drift — a `done` task's Evidence anchor no longer
     resolves in the tree (the decision is marked implemented but the code
     says otherwise). CI-gateable.
  2  usage error
"""

import os
import re
import subprocess
import sys

import anchors
import reindex  # same dir; reuses parse_record / record_files / PREFIX / ids_in

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             "dist", "build", ".mypy_cache", ".pytest_cache"}


# --------------------------------------------------------------------------
# record loading
# --------------------------------------------------------------------------

def load(scope, artifact):
    """id -> (title, fields, is_active), unioning active + archive. The
    archive union is not optional: `done` tasks are reaped continuously, so
    omitting it would make every shipped decision look uncovered."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope, artifact)
    out = {}
    for active, d in ((True, base), (False, os.path.join(base, "archive"))):
        for path in reindex.record_files(d, prefix):
            rid, title, fields = reindex.parse_record(path)
            if rid:
                out[rid] = (title, fields, active)
    return out


# --------------------------------------------------------------------------
# implementation view (mirrors the reconcile-status SKILL rule exactly)
# --------------------------------------------------------------------------

def view_for(impl):
    """impl: list of (task_id, status). Returns (view, why)."""
    if not impl:
        return "uncovered", "no implementing tasks"
    dropped = [t for t in impl if t[1] == "dropped"]
    live = [t for t in impl if t[1] != "dropped"]
    if not live:
        return "reversed", "all implementing tasks dropped"
    statuses = {s for _, s in live}
    if statuses == {"done"}:
        if dropped:
            return "partial", "live tasks all done; some coverage dropped"
        return "implemented", "all implementing tasks done"
    if statuses == {"todo"}:
        return "not_started", "all live tasks todo"
    return "in_progress", "work underway"


# --------------------------------------------------------------------------
# Evidence anchor resolution
# --------------------------------------------------------------------------

def extract_anchors(ev):
    return anchors.extract_anchor_texts(ev)


def _search(pattern, root, scope):
    """True if `pattern` (a regex) is found in any file under root, optionally
    narrowed by `scope` (a directory, a glob, or a single file). ripgrep
    first, Python fallback if rg is absent."""
    if not pattern:
        return False
    args = ["rg", "-l", "--no-messages", "-e", pattern]
    search_path = "."
    if scope:
        full = os.path.join(root, scope)
        if os.path.isdir(full):
            search_path = scope                       # within the directory
        elif any(c in scope for c in "*?[]"):
            args += ["-g", scope]                     # treat as a glob
        else:
            search_path = scope                       # a single file path
    args.append(search_path)
    try:
        r = subprocess.run(args, cwd=root, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except FileNotFoundError:
        return _py_search(pattern, root, scope)


def _py_search(pattern, root, scope):
    try:
        rx = re.compile(pattern)
    except re.error:
        rx = re.compile(re.escape(pattern))
    import fnmatch

    def files():
        base = root
        if scope and os.path.isdir(os.path.join(root, scope)):
            base = os.path.join(root, scope)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                full = os.path.join(dirpath, name)
                # forward slashes so "/"-authored globs and paths match on Windows
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                if scope and not os.path.isdir(os.path.join(root, scope)):
                    if any(c in scope for c in "*?[]"):
                        if not fnmatch.fnmatch(rel, scope):
                            continue
                    elif rel != scope:
                        continue
                yield full

    for full in files():
        try:
            with open(full, encoding="utf-8", errors="ignore") as fh:
                if rx.search(fh.read()):
                    return True
        except OSError:
            continue
    return False


def resolve_anchor(anchor, root):
    """True if the anchor's target is present in the tree (presence, not
    passing — matches reconcile-status's read-only resolution)."""
    kind, parts, err = anchors.parse_anchor(anchor)
    if err:
        return False
    if kind == "file":
        return os.path.exists(os.path.join(root, parts["path"]))
    if kind == "grep":
        return _search(parts["pattern"], root, parts.get("scope"))
    if kind == "symbol":
        path = parts["path"]
        if not os.path.exists(os.path.join(root, path)):
            return False
        return _search(parts["pattern"], root, path)
    if kind == "test":
        t = parts["target"]
        if os.path.exists(os.path.join(root, t)):
            return True
        return _search(re.escape(t), root, None)
    return False


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = "."
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
    if not args:
        print("usage: reconcile.py <scope-dir> [--root <repo-root>]",
              file=sys.stderr)
        return 2
    scope = os.path.expanduser(args[0])
    if not os.path.isdir(scope):
        print(f"reconcile.py: no such scope dir: {scope}", file=sys.stderr)
        return 2

    decs = load(scope, "decisions")
    risks = load(scope, "risks")
    tasks = load(scope, "tasks")

    # tasks grouped by the decision they implement
    by_impl = {}
    for tid, (_t, fields, _a) in tasks.items():
        status = fields.get("Status", "").strip()
        for did in reindex.ids_in(fields.get("Implements", ""), "D"):
            by_impl.setdefault(did, []).append((tid, status))

    # resolve every done task's anchors once (dedup), record failures
    drift = {}        # tid -> [failed anchors]
    no_anchor = set()  # done tasks with no Evidence anchor at all
    for tid, (_t, fields, _a) in tasks.items():
        if fields.get("Status", "").strip() != "done":
            continue
        anchors = extract_anchors(fields.get("Evidence", ""))
        if not anchors:
            no_anchor.add(tid)
            continue
        failed = [a for a in anchors if not resolve_anchor(a, root)]
        if failed:
            drift[tid] = failed

    # per accepted decision view
    views = {}        # did -> (view, why, contributing)
    for did, (title, fields, active) in decs.items():
        if not active or fields.get("Status", "").strip() != "accepted":
            continue
        impl = by_impl.get(did, [])
        view, why = view_for(impl)
        views[did] = (view, why, impl, "Promoted from" in fields and
                      fields.get("Promoted from", "").strip() != "")

    # ---- report -----------------------------------------------------------
    print(f"reconcile {scope}: {len(views)} accepted decision(s)\n")

    order = ["implemented", "partial", "in_progress", "not_started",
             "reversed", "uncovered"]
    by_view = {}
    for did, (view, why, impl, promoted) in views.items():
        by_view.setdefault(view, []).append((did, why, impl, promoted))

    for view in order:
        rows = by_view.get(view)
        if not rows:
            continue
        print(f"== {view.upper()} ==")
        for did, why, impl, promoted in sorted(rows):
            tag = ""
            contributing_done = [t for t, s in impl if s == "done"]
            if view in ("implemented", "partial"):
                if any(t in drift for t in contributing_done):
                    tag = "  [UNVERIFIED: drift]"
                elif any(t in no_anchor for t in contributing_done):
                    tag = "  (unverified: no anchor)"
                else:
                    tag = "  (verified)" if contributing_done else ""
            tlist = ",".join(f"{t}:{s}" for t, s in sorted(impl)) or "—"
            promo = "  [promoted-from; project tasks accrue over time]" if (
                promoted and view == "uncovered") else ""
            print(f"  {decs[did][0]}")
            print(f"    {did}: {view}{tag} — {why} [{tlist}]{promo}")
        print()

    # ---- anomalies --------------------------------------------------------
    anomalies = []

    if drift:
        for tid in sorted(drift):
            impl_ds = reindex.ids_in(tasks[tid][1].get("Implements", ""), "D")
            anomalies.append(
                f"IMPLEMENTATION DRIFT: {tid} (implements {','.join(impl_ds) or '—'}) "
                f"done but anchor(s) do not resolve: {', '.join(drift[tid])}. "
                f"Re-open the task or update its Evidence if the code moved.")

    reversed_ds = [d for d, (v, *_ ) in views.items() if v == "reversed"]
    for d in sorted(reversed_ds):
        anomalies.append(
            f"SILENT REVERSAL: {d} is accepted but every implementing task is "
            f"dropped — it likely wants superseded/deprecated (via /challenge-me).")

    uncovered = [d for d, (v, _w, _i, promo) in views.items()
                 if v == "uncovered" and not promo]
    for d in sorted(uncovered):
        anomalies.append(
            f"UNCOVERED: {d} is accepted with zero implementing tasks — already "
            f"built? environmental? planning gap?")

    orphans = []
    for tid, (_t, fields, _a) in sorted(tasks.items()):
        impl = reindex.ids_in(fields.get("Implements", ""), "D")
        mit = reindex.ids_in(fields.get("Mitigates", ""), "R")
        if not impl and not mit:
            orphans.append(tid)
    for tid in orphans:
        anomalies.append(
            f"ORPHAN TASK: {tid} has neither Implements nor Mitigates.")

    # mitigation coverage: a mitigate risk whose tasks are all dropped/missing
    for rid, (title, fields, active) in sorted(risks.items()):
        if not active or fields.get("Disposition", "").strip() != "mitigate":
            continue
        tids = reindex.ids_in(fields.get("Action", ""), "T")
        if not tids:
            continue
        present = [t for t in tids if t in tasks]
        if present and all(tasks[t][1].get("Status", "").strip() == "dropped"
                           for t in present):
            anomalies.append(
                f"MITIGATION NOTIONAL: {rid} is mitigate but all its tasks "
                f"({','.join(tids)}) are dropped — no longer mitigated in practice.")

    if anomalies:
        print("== ANOMALIES (surface to the owner; this script fixes nothing) ==")
        for a in anomalies:
            print(f"  {a}")
    else:
        print("== ANOMALIES ==\n  none")

    print("\nNote: structural validity is audit.py's; quality smells "
          "(un-red-teamed decision, thin defer, mitigation complete) are "
          "reconcile_smells.py's. This script stores nothing.")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
