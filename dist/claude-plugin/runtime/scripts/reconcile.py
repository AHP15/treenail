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


def _git_ok(args, root):
    """True if `git <args>` exits 0 in `root`; False on any failure,
    including git being absent."""
    try:
        r = subprocess.run(["git", *args], cwd=root,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _resolve_pinned(sha, kind, parts, root):
    """Resolve a git:-pinned anchor at the named commit (D-025): the
    evidenced fact was abolished from the working tree, so presence is
    checked via git cat-file / git grep against `sha` instead."""
    if kind == "file":
        return _git_ok(["cat-file", "-e", f"{sha}:{parts['path']}"], root)
    if kind == "grep":
        args = ["grep", "-I", "-l", "-E", parts["pattern"], sha]
        if parts.get("scope"):
            args += ["--", parts["scope"]]
        return _git_ok(args, root)
    if kind == "symbol":
        return _git_ok(["grep", "-I", "-l", "-E", parts["pattern"], sha,
                        "--", parts["path"]], root)
    if kind == "test":
        t = parts["target"]
        if _git_ok(["cat-file", "-e", f"{sha}:{t}"], root):
            return True
        return _git_ok(["grep", "-I", "-l", "-F", t, sha], root)
    return False


def resolve_anchor(anchor, root):
    """True if the anchor's target is present in the tree (presence, not
    passing — matches reconcile-status's read-only resolution). `git:`
    pins resolve against their named commit, not the working tree."""
    kind, parts, err = anchors.parse_anchor(anchor)
    if err:
        return False
    if kind == "git":
        return _resolve_pinned(parts["sha"], parts["kind"], parts["parts"],
                               root)
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

# --------------------------------------------------------------------------
# derivation (shared with archive_cycle.py's settle/unsettle pass)
# --------------------------------------------------------------------------

# Dispositions that mean a risk is still an open concern about a decision.
# `accept` is a closed concern: the residual was judged acceptable.
OPEN_RISK = {"pending", "fix", "mitigate", "defer"}


def derive(scope, root):
    """Load the scope and derive everything the view needs. Returns
    (decs, risks, tasks, drift, no_anchor, views) where views maps every
    accepted decision — active AND settled (archived while accepted) — to
    (view, why, impl, promoted, active)."""
    decs = load(scope, "decisions")
    risks = load(scope, "risks")
    tasks = load(scope, "tasks")

    by_impl = {}
    for tid, (_t, fields, _a) in tasks.items():
        status = fields.get("Status", "").strip()
        for did in reindex.ids_in(fields.get("Implements", ""), "D"):
            by_impl.setdefault(did, []).append((tid, status))

    # resolve every done task's anchors once (dedup), record failures
    drift = {}         # tid -> [failed anchors]
    no_anchor = set()  # done tasks with no Evidence anchor at all
    for tid, (_t, fields, _a) in tasks.items():
        if fields.get("Status", "").strip() != "done":
            continue
        found = extract_anchors(fields.get("Evidence", ""))
        if not found:
            no_anchor.add(tid)
            continue
        failed = [a for a in found if not resolve_anchor(a, root)]
        if failed:
            drift[tid] = failed

    views = {}
    for did, (title, fields, active) in decs.items():
        if fields.get("Status", "").strip() != "accepted":
            continue
        impl = by_impl.get(did, [])
        view, why = view_for(impl)
        promoted = fields.get("Promoted from", "").strip() != ""
        views[did] = (view, why, impl, promoted, active)
    return decs, risks, tasks, drift, no_anchor, views


def verification(impl, drift, no_anchor):
    """'verified' | 'drift' | 'no anchor' | None for a decision's tasks."""
    done = [t for t, s in impl if s == "done"]
    if not done:
        return None
    if any(t in drift for t in done):
        return "drift"
    if any(t in no_anchor for t in done):
        return "no anchor"
    return "verified"


def settle_check(did, views, risks, tasks, drift, no_anchor):
    """Is an accepted decision *settled* — out of the working set? Returns
    (True, last_done_date) or (False, reason). Settled means: implemented
    (or partial), every contributing done task's anchors verified, and no
    open risk about it in the active set. The retrospective-boundary gate
    on settling is archive_cycle's (it does not apply to staying settled)."""
    view, _why, impl, _promoted, _active = views[did]
    if view not in ("implemented", "partial"):
        return False, view
    ver = verification(impl, drift, no_anchor)
    if ver != "verified":
        return False, f"unverified: {ver or 'no done task'}"
    open_risks = sorted(
        rid for rid, (_t, f, active) in risks.items()
        if active and f.get("Disposition", "").strip() in OPEN_RISK
        and did in reindex.ids_in(f.get("Related decisions", ""), "D"))
    if open_risks:
        return False, f"open risk(s) {','.join(open_risks)}"
    dates = [tasks[t][1].get("Date done", "").strip()
             for t, s in impl if s == "done" and t in tasks]
    return True, max(dates) if all(dates) else None


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

    decs, risks, tasks, drift, no_anchor, views = derive(scope, root)

    # A settled decision that still passes settle_check is reported as one
    # ID in a summary line — it is out of the working set, and listing it
    # in full every run is exactly the O(history) cost settling removes.
    # One that no longer passes is reported in full, like an active one.
    quiet_settled = []
    reopened = {}
    for did, (_v, _w, _i, _p, active) in views.items():
        if active:
            continue
        ok, why = settle_check(did, views, risks, tasks, drift, no_anchor)
        if ok:
            quiet_settled.append(did)
        else:
            reopened[did] = why

    # ---- report -----------------------------------------------------------
    n_settled = sum(1 for v in views.values() if not v[4])
    print(f"reconcile {scope}: {len(views)} accepted decision(s) "
          f"({len(views) - n_settled} active, {n_settled} settled)\n")

    order = ["implemented", "partial", "in_progress", "not_started",
             "reversed", "uncovered"]
    by_view = {}
    for did, (view, why, impl, promoted, _active) in views.items():
        if did in quiet_settled:
            continue
        by_view.setdefault(view, []).append((did, why, impl, promoted))

    for view in order:
        rows = by_view.get(view)
        if not rows:
            continue
        print(f"== {view.upper()} ==")
        for did, why, impl, promoted in sorted(rows):
            tag = ""
            if view in ("implemented", "partial"):
                tag = {"drift": "  [UNVERIFIED: drift]",
                       "no anchor": "  (unverified: no anchor)",
                       "verified": "  (verified)",
                       None: ""}[verification(impl, drift, no_anchor)]
            if did in reopened:
                tag += "  [SETTLED — reopens on next archive-cycle]"
            tlist = ",".join(f"{t}:{s}" for t, s in sorted(impl)) or "—"
            promo = "  [promoted-from; project tasks accrue over time]" if (
                promoted and view == "uncovered") else ""
            print(f"  {decs[did][0]}")
            print(f"    {did}: {view}{tag} — {why} [{tlist}]{promo}")
        print()
    if quiet_settled:
        print(f"== SETTLED (still verified; not listed) ==\n  "
              f"{len(quiet_settled)}: {', '.join(sorted(quiet_settled))}\n")

    # ---- anomalies --------------------------------------------------------
    anomalies = []

    for d in sorted(reopened):
        anomalies.append(
            f"SETTLED DECISION REOPENED: {d} is settled but no longer qualifies "
            f"({reopened[d]}) — archive-cycle will move it back to the active set.")

    if drift:
        for tid in sorted(drift):
            impl_ds = reindex.ids_in(tasks[tid][1].get("Implements", ""), "D")
            anomalies.append(
                f"IMPLEMENTATION DRIFT: {tid} (implements {','.join(impl_ds) or '—'}) "
                f"done but anchor(s) do not resolve: {', '.join(drift[tid])}. "
                f"Re-open the task or update its Evidence if the code moved.")

    reversed_ds = [d for d, (v, *_) in views.items() if v == "reversed"]
    for d in sorted(reversed_ds):
        anomalies.append(
            f"SILENT REVERSAL: {d} is accepted but every implementing task is "
            f"dropped — it likely wants superseded/deprecated (via /challenge-me).")

    uncovered = [d for d, (v, _w, _i, promo, _a) in views.items()
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
    # Report output is machine-parsed, so emit deterministic UTF-8
    # regardless of console code page — Windows cp1252 or a POSIX C
    # locale must never crash on report typography (—, ≤, →) (R-010).
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="replace")
    from skill_version import check_skill_version
    from spec_version import check_spec_version, scope_from_argv
    argv = check_skill_version(sys.argv)
    check_spec_version(scope_from_argv(argv))
    sys.exit(main(argv))
