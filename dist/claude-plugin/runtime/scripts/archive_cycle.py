#!/usr/bin/env python3
"""archive_cycle.py — mechanically reap terminal records into archive/
and settle/unsettle accepted decisions.

This script implements the deterministic half of the archive-cycle skill:
move terminal active records into `<artifact>/archive/`, move *settled*
accepted decisions there too (and move any settled decision that no longer
qualifies back), then rebuild the affected INDEX files from the per-record
sources. It does not compact record prose; compaction remains a judgment
step driven by compact-select.py.

Settling (spec § ARCHIVAL) keeps the active decision set bounded: an
accepted decision leaves the working set once reconcile.py derives it as
implemented with verified Evidence, no open risk names it, and a
retrospective has covered its last task's Date done. Its Status stays
`accepted` — it is still in effect, just no longer in flight. The check
is re-run every time, so drift, a new implementing task, or a new open
risk moves it straight back.

Usage:
    archive_cycle.py <scope-dir> [--dry-run] [--confirm-risk R-001,R-002]
                     [--today YYYY-MM-DD] [--root <repo-root>]

  --dry-run       print what would move; write nothing.
  --confirm-risk  comma-separated risks the user has explicitly confirmed
                  are spent: fix/defer risks (which never reap without it;
                  Date resolved is filled before moving if absent), or
                  accept risks newer than the latest retrospective boundary
                  (their Date already serves as the terminal date).
  --today         date used for Date resolved (default: UTC today).
  --root          repo root that Evidence anchors resolve against, for the
                  settle check (default: the current directory).

Exit codes: 0 success; 1 blocked move; 2 usage error.
"""

from datetime import datetime, timezone
import os
import re
import sys

import reconcile
import reindex

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_args(argv):
    today = datetime.now(timezone.utc).date().isoformat()
    if len(argv) < 2 or argv[1].startswith("-"):
        return None, False, set(), today, ".", "missing scope"
    scope = os.path.expanduser(argv[1])
    dry = False
    confirmed = set()
    root = "."
    i = 2
    while i < len(argv):
        arg = argv[i]
        if arg == "--dry-run":
            dry = True
            i += 1
            continue
        if arg == "--confirm-risk" and i + 1 < len(argv):
            confirmed.update(x.strip() for x in argv[i + 1].split(",") if x.strip())
            i += 2
            continue
        if arg == "--today" and i + 1 < len(argv):
            today = argv[i + 1]
            i += 2
            continue
        if arg == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
            i += 2
            continue
        return None, False, set(), today, root, f"unknown or incomplete option {arg}"
    if not ISO_RE.match(today):
        return None, False, set(), today, root, "--today must be YYYY-MM-DD"
    return scope, dry, confirmed, today, root, None


def parse_iso(value):
    value = (value or "").strip()
    return value if ISO_RE.match(value) else None


def latest_boundary(scope):
    d = os.path.join(scope, "retrospectives")
    if not os.path.isdir(d):
        return None
    best = None
    for name in sorted(os.listdir(d)):
        if not re.match(r"^\d{4}-\d{2}-\d{2}\.md$", name):
            continue
        _, _, fields = reindex.parse_record(os.path.join(d, name))
        b = parse_iso(fields.get("Boundary-end", ""))
        if b and (best is None or b > best):
            best = b
    return best


def active_records(scope, artifact):
    base = os.path.join(scope, artifact)
    prefix = reindex.PREFIX[artifact]
    for path in reindex.record_files(base, prefix):
        rid, title, fields = reindex.parse_record(path)
        if rid:
            yield rid, title, fields, path


def ensure_date_resolved(path, today):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    field_re = re.compile(r"^-\s+\*\*Date resolved\*\*:\s?(.*)$")
    date_re = re.compile(r"^-\s+\*\*Date\*\*:")
    for i, line in enumerate(lines):
        m = field_re.match(line)
        if m:
            if m.group(1).strip():
                return False
            lines[i] = f"- **Date resolved**: {today}"
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines) + "\n")
            return True

    insert_at = None
    for i, line in enumerate(lines):
        if date_re.match(line):
            insert_at = i + 1
            break
    if insert_at is None:
        insert_at = len(lines)
    lines.insert(insert_at, f"- **Date resolved**: {today}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return True


def move_to_archive(path, artifact):
    base = os.path.dirname(path)
    dest_dir = os.path.join(base, "archive")
    dest = os.path.join(dest_dir, os.path.basename(path))
    if os.path.exists(dest):
        return False, dest
    os.makedirs(dest_dir, exist_ok=True)
    os.rename(path, dest)
    return True, dest


def move_to_active(path):
    base = os.path.dirname(os.path.dirname(path))
    dest = os.path.join(base, os.path.basename(path))
    if os.path.exists(dest):
        return False, dest
    os.rename(path, dest)
    return True, dest


def settle_moves(scope, root, boundary):
    """(to_settle, to_unsettle, waiting) for accepted decisions.
    to_settle / to_unsettle: [(rid, path, note)]; waiting: [(rid, reason)]
    for decisions that qualify except for the retrospective boundary."""
    decs, risks, tasks, drift, no_anchor, views = reconcile.derive(scope, root)
    ddir = os.path.join(scope, "decisions")
    to_settle, to_unsettle, waiting = [], [], []
    for did, (view, _why, _impl, _promoted, active) in sorted(views.items()):
        ok, info = reconcile.settle_check(did, views, risks, tasks,
                                          drift, no_anchor)
        if active and ok:
            if boundary and info and info <= boundary:
                to_settle.append((did, os.path.join(ddir, f"{did}.md"),
                                  f"{view}, verified, last done {info}"))
            else:
                waiting.append((did, "settle awaiting retrospective boundary"))
        elif not active and not ok:
            to_unsettle.append((did, os.path.join(ddir, "archive", f"{did}.md"),
                                f"no longer settled: {info}"))
    return to_settle, to_unsettle, waiting


def reindex_changed(scope, changed_artifacts):
    malformed = []
    reports = []
    for artifact in sorted(changed_artifacts):
        reports.extend(reindex.reindex_artifact(scope, artifact, malformed))
    return reports, malformed


def main(argv):
    scope, dry, confirmed, today, root, err = parse_args(argv)
    if err:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print(f"archive_cycle.py: {err}", file=sys.stderr)
        return 2
    if not os.path.isdir(scope):
        print(f"archive_cycle.py: no such scope dir: {scope}", file=sys.stderr)
        return 2

    boundary = latest_boundary(scope)
    to_move = []  # (artifact, rid, path, note)
    skipped = []

    for rid, _title, fields, path in active_records(scope, "decisions"):
        status = fields.get("Status", "").strip()
        if status in {"superseded", "deprecated", "promoted"}:
            to_move.append(("decisions", rid, path, status))

    for rid, _title, fields, path in active_records(scope, "tasks"):
        status = fields.get("Status", "").strip()
        if status in {"done", "dropped"}:
            to_move.append(("tasks", rid, path, status))

    for rid, _title, fields, path in active_records(scope, "risks"):
        disp = fields.get("Disposition", "").strip()
        if disp == "accept":
            d = parse_iso(fields.get("Date", ""))
            if boundary and d and d <= boundary:
                to_move.append(("risks", rid, path, "accept reviewed"))
            elif rid in confirmed:
                to_move.append(("risks", rid, path, "accept user-confirmed"))
            else:
                skipped.append((rid, "accept awaiting retrospective boundary"))
        elif disp in {"fix", "defer"}:
            if rid in confirmed:
                to_move.append(("risks", rid, path, f"{disp} confirmed"))
            else:
                skipped.append((rid, f"{disp} awaiting explicit confirmation"))

    to_settle, to_unsettle, waiting = settle_moves(scope, root, boundary)
    skipped.extend(waiting)

    print(f"archive-cycle reap {scope}{' (dry-run)' if dry else ''}")
    if not (to_move or to_settle or to_unsettle):
        print("  no records eligible to move")
    for artifact, rid, path, note in to_move:
        print(f"  REAP  {artifact}/{rid}  ({note})")
    for rid, _path, note in to_settle:
        print(f"  SETTLE  decisions/{rid}  ({note})")
    for rid, _path, note in to_unsettle:
        print(f"  UNSETTLE  decisions/{rid}  ({note})")
    for rid, reason in skipped:
        print(f"  skip  {rid}  ({reason})")

    if dry:
        return 0

    changed = set()
    blocked = []
    for artifact, rid, path, note in to_move:
        if artifact == "risks" and note.endswith(" confirmed"):
            ensure_date_resolved(path, today)
        ok, dest = move_to_archive(path, artifact)
        if not ok:
            blocked.append((rid, dest))
            continue
        changed.add(artifact)
    for rid, path, _note in to_settle:
        ok, dest = move_to_archive(path, "decisions")
        if not ok:
            blocked.append((rid, dest))
            continue
        changed.add("decisions")
    for rid, path, _note in to_unsettle:
        ok, dest = move_to_active(path)
        if not ok:
            blocked.append((rid, dest))
            continue
        changed.add("decisions")

    if blocked:
        print("\nBLOCKED moves:")
        for rid, dest in blocked:
            print(f"  {rid}: destination already exists: {dest}")
        return 1

    if changed:
        reports, malformed = reindex_changed(scope, changed)
        for path, n, changed_idx, added, removed in reports:
            tag = "rebuilt" if changed_idx else "unchanged"
            delta = f" (+{added}/-{removed})" if changed_idx else ""
            print(f"{tag:9} {n:4d} lines  {path}{delta}")
        if malformed:
            print("\nMALFORMED records after reindex:")
            for rec, field in malformed:
                print(f"  {rec}: missing/empty {field}")
            return 1
    return 0


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
