#!/usr/bin/env python3
"""archive_cycle.py — mechanically reap terminal records into archive/.

This script implements the deterministic half of the archive-cycle skill:
move terminal active records into `<artifact>/archive/` and rebuild the
affected INDEX files from the per-record sources. It does not compact
record prose; compaction remains a judgment step driven by compact-select.py.

Usage:
    archive_cycle.py <scope-dir> [--dry-run] [--confirm-risk R-001,R-002]
                     [--today YYYY-MM-DD]

  --dry-run       print what would move; write nothing.
  --confirm-risk  comma-separated fix/defer risks the user has explicitly
                  confirmed are spent. For these, Date resolved is filled
                  before moving if absent.
  --today         date used for Date resolved (default: UTC today).

Exit codes: 0 success; 1 blocked move; 2 usage error.
"""

from datetime import datetime, timezone
import os
import re
import sys

import reindex

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_args(argv):
    if len(argv) < 2:
        return None, False, set(), date.today().isoformat(), "missing scope"
    scope = os.path.expanduser(argv[1])
    dry = False
    confirmed = set()
    today = datetime.now(timezone.utc).date().isoformat()
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
        return None, False, set(), today, f"unknown or incomplete option {arg}"
    if not ISO_RE.match(today):
        return None, False, set(), today, "--today must be YYYY-MM-DD"
    return scope, dry, confirmed, today, None


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


def reindex_changed(scope, changed_artifacts):
    malformed = []
    reports = []
    for artifact in sorted(changed_artifacts):
        reports.extend(reindex.reindex_artifact(scope, artifact, malformed))
    return reports, malformed


def main(argv):
    scope, dry, confirmed, today, err = parse_args(argv)
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
            else:
                skipped.append((rid, "accept awaiting retrospective boundary"))
        elif disp in {"fix", "defer"}:
            if rid in confirmed:
                to_move.append(("risks", rid, path, f"{disp} confirmed"))
            else:
                skipped.append((rid, f"{disp} awaiting explicit confirmation"))

    print(f"archive-cycle reap {scope}{' (dry-run)' if dry else ''}")
    if not to_move:
        print("  no records eligible to reap")
    for artifact, rid, path, note in to_move:
        print(f"  REAP  {artifact}/{rid}  ({note})")
    for rid, reason in skipped:
        print(f"  skip  {rid}  ({reason})")

    if dry:
        return 0

    changed = set()
    blocked = []
    for artifact, rid, path, note in to_move:
        if artifact == "risks" and "confirmed" in note:
            ensure_date_resolved(path, today)
        ok, dest = move_to_archive(path, artifact)
        if not ok:
            blocked.append((rid, dest))
            continue
        changed.add(artifact)

    if blocked:
        print("\nBLOCKED moves:")
        for rid, dest in blocked:
            print(f"  {rid}: archive destination already exists: {dest}")
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
    sys.exit(main(sys.argv))
