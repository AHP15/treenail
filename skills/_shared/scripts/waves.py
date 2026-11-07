#!/usr/bin/env python3
"""waves.py — pick the next wave of tasks that can be built in parallel.

The mechanical half of the `parallel-work` skill. Choosing which open tasks
are safe to build at the same time is deterministic — dependency state plus
a predicted code footprint — so it lives here rather than in skill prose,
where two runs could disagree.

A task is **eligible** when it is `todo` or `in_progress` and every
`Depends on` task is `done`. Two eligible tasks **conflict** — and so never
share a wave — when either:

  * they implement the same decision (they usually touch the same code), or
  * their footprints overlap. A task's footprint is the set of paths its
    pre-seeded Evidence anchors name (`file:` path, `grep:` path glob,
    `symbol:` path, `test:` path), reduced to the static prefix before any
    glob character. Two footprints overlap when one path equals, contains,
    or is contained by the other. A glob with no static prefix (`**/*.ts`)
    covers the whole tree and conflicts with everything.

A task with no footprint is **unscoped**: nothing predicts what it will
touch, so it only ever runs alone, in a wave of one, once no scoped task
is eligible.

The wave is filled greedily in priority order — `in_progress` first (work
already started), then tasks mitigating a `critical`/`high` risk, then
tasks that unblock the most other open tasks, then by ID — up to `--max`.
Only the next wave is computed: later waves depend on what actually merges.

Usage:
    waves.py <scope-dir> [--max N] [--only T-001,T-002,...]

  --max N    wave size cap (default 5).
  --only     restrict the open set to these task IDs (e.g. one phase from
             sequence-work).

Exit codes: 0 a non-empty wave was found; 1 nothing eligible (no open
tasks, or every open task is blocked); 2 usage error. Never modifies a file.
"""

import os
import re
import sys

import anchors
import reindex

DEFAULT_MAX = 5
OPEN = ("todo", "in_progress")
HIGH_SEVERITY = ("critical", "high")
GLOB_CHARS = re.compile(r"[*?\[{]")


def load(scope, artifact):
    """id -> (title, fields), unioning active + archive."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope, artifact)
    out = {}
    for d in (base, os.path.join(base, "archive")):
        for path in reindex.record_files(d, prefix):
            rid, title, fields = reindex.parse_record(path)
            if rid:
                out[rid] = (title, fields)
    return out


def static_prefix(path):
    """`src/auth/**/*.ts` -> `src/auth`; `**/*.ts` -> `` (whole tree)."""
    path = path.strip().strip("`").replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    m = GLOB_CHARS.search(path)
    if m:
        path = path[:m.start()]
        path = path[:path.rfind("/") + 1] if "/" in path else ""
    return path.rstrip("/")


def footprint(fields):
    """Paths a task's Evidence anchors name; None if it names none."""
    paths = set()
    for text in anchors.extract_anchor_texts(fields.get("Evidence", "")):
        kind, parts, err = anchors.parse_anchor(text)
        if err or kind == "git":
            continue  # a history pin names no working-tree footprint
        path = None
        if kind in ("file", "symbol"):
            path = parts["path"]
        elif kind == "grep":
            path = parts.get("scope") or ""  # unscoped grep = whole tree
        elif kind == "test" and "/" in parts["target"]:
            path = parts["target"]
        if path is not None:
            paths.add(static_prefix(path))
    return paths or None


def overlap(a, b):
    """Shared path, or None. An empty prefix covers the whole tree."""
    for p in sorted(a):
        for q in sorted(b):
            if p == "" or q == "":
                return ""  # whole tree
            if p == q or p.startswith(q + "/") or q.startswith(p + "/"):
                return p if len(p) >= len(q) else q
    return None


def conflict(t, u, info):
    """Reason tasks t and u may not share a wave, or None."""
    shared = sorted(set(info[t]["implements"]) & set(info[u]["implements"]))
    if shared:
        return f"both implement {shared[0]}"
    hit = overlap(info[t]["footprint"], info[u]["footprint"])
    if hit is not None:
        return f"overlapping footprint {hit or '(whole tree)'}"
    return None


def parse_args(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        return None, None, None, "missing scope"
    scope, cap, only = argv[1], DEFAULT_MAX, None
    i = 2
    while i < len(argv):
        if argv[i] == "--max" and i + 1 < len(argv):
            try:
                cap = int(argv[i + 1])
            except ValueError:
                return None, None, None, "--max must be an integer"
            if cap < 1:
                return None, None, None, "--max must be at least 1"
            i += 2
            continue
        if argv[i] == "--only" and i + 1 < len(argv):
            only = {x.strip() for x in argv[i + 1].split(",") if x.strip()}
            i += 2
            continue
        return None, None, None, f"unknown or incomplete option {argv[i]}"
    return scope, cap, only, None


def main(argv):
    scope, cap, only, err = parse_args(argv)
    if err:
        print(f"usage: waves.py <scope-dir> [--max N] [--only T-001,...]\n"
              f"waves.py: {err}", file=sys.stderr)
        return 2
    scope = os.path.expanduser(scope)
    if not os.path.isdir(scope):
        print(f"waves.py: no such scope dir: {scope}", file=sys.stderr)
        return 2

    tasks = load(scope, "tasks")
    risks = load(scope, "risks")
    high_risks = {rid for rid, (_t, f) in risks.items()
                  if f.get("Severity", "").strip() in HIGH_SEVERITY}

    def status(tid):
        return tasks[tid][1].get("Status", "").strip() if tid in tasks else None

    open_ids = sorted(t for t in tasks if status(t) in OPEN
                      and (only is None or t in only))
    if only:
        for t in sorted(only - set(open_ids)):
            print(f"note: {t} is not an open task in this scope; ignored")

    info, blocked = {}, []
    for tid in open_ids:
        fields = tasks[tid][1]
        deps = reindex.ids_in(fields.get("Depends on", ""), "T")
        waiting = [d for d in deps if status(d) != "done"]
        if waiting:
            blocked.append((tid, waiting))
            continue
        info[tid] = {
            "implements": reindex.ids_in(fields.get("Implements", ""), "D"),
            "mitigates_high": any(r in high_risks for r in
                                  reindex.ids_in(fields.get("Mitigates", ""), "R")),
            "footprint": footprint(fields),
            "size": fields.get("Size", "").strip() or "?",
            "status": status(tid),
        }

    unblocks = {t: 0 for t in info}
    for tid in open_ids:
        for d in reindex.ids_in(tasks[tid][1].get("Depends on", ""), "T"):
            if d in unblocks:
                unblocks[d] += 1

    def priority(t):
        i = info[t]
        return (i["status"] != "in_progress", not i["mitigates_high"],
                -unblocks[t], t)

    ranked = sorted(info, key=priority)
    scoped = [t for t in ranked if info[t]["footprint"] is not None]
    unscoped = [t for t in ranked if info[t]["footprint"] is None]

    wave, deferred = [], []
    for t in scoped:
        if len(wave) >= cap:
            deferred.append((t, f"wave is full (--max {cap})"))
            continue
        reason = next(((u, r) for u in wave
                       for r in [conflict(t, u, info)] if r), None)
        if reason:
            deferred.append((t, f"conflicts with {reason[0]}: {reason[1]}"))
        else:
            wave.append(t)
    if not wave and unscoped:
        wave.append(unscoped.pop(0))
    for t in unscoped:
        deferred.append((t, "unscoped — no target anchors, so it runs alone "
                            "once no scoped task is eligible"))

    print(f"waves {scope}: {len(open_ids)} open, {len(info)} eligible, "
          f"max {cap}")
    if wave:
        print(f"\nWAVE ({len(wave)} task{'s' if len(wave) != 1 else ''})")
        for t in wave:
            i = info[t]
            fp = ", ".join(sorted(p or "(whole tree)" for p in i["footprint"])) \
                if i["footprint"] is not None else "unscoped"
            impl = ",".join(i["implements"]) or "—"
            tag = "  [in_progress]" if i["status"] == "in_progress" else ""
            print(f"  {t}  {i['size']}  {tasks[t][0]}{tag}")
            print(f"      footprint: {fp}; implements: {impl}")
    else:
        print("\nWAVE: none — nothing is eligible")
    if deferred:
        print("\nDEFERRED (eligible; a later wave)")
        for t, why in deferred:
            print(f"  {t}  {why}")
    if blocked:
        print("\nBLOCKED (dependencies not done)")
        for t, waiting in blocked:
            print(f"  {t}  waiting on "
                  + ", ".join(f"{d}:{status(d) or 'missing'}" for d in waiting))
    return 0 if wave else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="replace")
    from skill_version import check_skill_version
    from spec_version import check_spec_version, scope_from_argv
    argv = check_skill_version(sys.argv)
    check_spec_version(scope_from_argv(argv))
    sys.exit(main(argv))
