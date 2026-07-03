#!/usr/bin/env python3
"""compact-select.py — list archive records eligible for compaction.

`archive-cycle`'s compaction must never collapse a record's prose before
a retrospective has had the chance to read it. The consumption frontier
is the latest retrospective's **Boundary-end** (a machine-readable
YYYY-MM-DD field); a reaped, still-uncompacted record is eligible only
once its own terminal date is at or before that frontier.

Determining the frontier and selecting the eligible set is mechanical
and easy to get subtly wrong by hand (vague cycle prose, off-by-one
dates), so this script decides it deterministically. The actual
compaction — collapsing each eligible body to a ≤5-line summary — stays
in the skill, because it is prose judgment.

Usage:
    compact-select.py <scope-dir>

Prints the boundary in use and, per artifact, the uncompacted archive
records that are eligible (terminal date ≤ boundary), plus any it had to
skip (no parseable Boundary-end, or a record with no parseable terminal
date). It NEVER modifies a file.

Exit codes:
  0  a boundary was found (eligible set may still be empty)
  1  no parseable Boundary-end on any retrospective — caller MUST skip
     compaction entirely (records stay uncompacted, safely out of the
     hot path)
  2  usage error
"""

import os
import re
import sys

import reindex  # same dir; import-safe

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_iso(s):
    s = (s or "").strip()
    return s if ISO_RE.match(s) else None


def latest_boundary(scope):
    """Return (boundary_str, source_filename) or (None, None).

    The frontier is the maximum parseable `Boundary-end` across all
    retrospectives — the most recent period that has been harvested.
    """
    d = os.path.join(scope, "retrospectives")
    if not os.path.isdir(d):
        return None, None
    best, src = None, None
    for name in sorted(os.listdir(d)):
        if not re.match(r"^\d{4}-\d{2}-\d{2}\.md$", name):
            continue
        _, _, fields = reindex.parse_record(os.path.join(d, name))
        b = parse_iso(fields.get("Boundary-end", ""))
        if b and (best is None or b > best):
            best, src = b, name
    return best, src


def terminal_date(artifact, fields):
    if artifact == "decisions":
        status = fields.get("Status", "").strip()
        by_status = {
            "superseded": ["Date superseded"],
            "deprecated": ["Date deprecated"],
            "promoted": ["Date promoted"],
        }
        for name in by_status.get(status, []):
            v = parse_iso(fields.get(name, ""))
            if v:
                return v
        return None

    if artifact == "risks":
        disp = fields.get("Disposition", "").strip()
        # `accept` becomes terminal at disposition time, after a
        # retrospective reviews it. `fix`/`defer` become terminal only when a
        # later confirmation says the fix shipped or the trigger passed; that
        # confirmation date is separate from the original triage Date.
        fields_by_disp = {
            "accept": ["Date"],
            "fix": ["Date resolved"],
            "defer": ["Date resolved"],
        }
        for name in fields_by_disp.get(disp, []):
            v = parse_iso(fields.get(name, ""))
            if v:
                return v
        return None

    if artifact == "tasks":
        status = fields.get("Status", "").strip()
        fields_by_status = {
            "done": ["Date done"],
            "dropped": ["Date dropped"],
        }
        for name in fields_by_status.get(status, []):
            v = parse_iso(fields.get(name, ""))
            if v:
                return v
    return None


def main(argv):
    if len(argv) != 2:
        print("usage: compact-select.py <scope-dir>", file=sys.stderr)
        return 2
    scope = os.path.expanduser(argv[1])
    if not os.path.isdir(scope):
        print(f"compact-select.py: no such scope dir: {scope}", file=sys.stderr)
        return 2

    boundary, src = latest_boundary(scope)
    if boundary is None:
        print("NO BOUNDARY: no retrospective carries a parseable "
              "`Boundary-end` field.")
        print("→ archive-cycle MUST skip compaction. Reaped records stay "
              "uncompacted in archive/ (already off the hot path) until a "
              "retrospective harvests them.")
        return 1

    print(f"boundary-end: {boundary}  (from retrospectives/{src})")
    print("Eligible = uncompacted archive record whose terminal date "
          f"≤ {boundary}.\n")

    any_eligible = False
    for artifact in ("decisions", "risks", "tasks"):
        prefix = reindex.PREFIX[artifact]
        adir = os.path.join(scope, artifact, "archive")
        eligible, not_yet, no_date = [], [], []
        for path in reindex.record_files(adir, prefix):
            rid, _, fields = reindex.parse_record(path)
            if rid is None:
                continue
            if fields.get("Summary", "").strip():
                continue  # already compacted
            td = terminal_date(artifact, fields)
            if td is None:
                no_date.append(rid)
            elif td <= boundary:
                eligible.append((rid, td))
            else:
                not_yet.append((rid, td))
        if eligible or not_yet or no_date:
            print(f"{artifact}:")
        if eligible:
            any_eligible = True
            for rid, td in eligible:
                print(f"  COMPACT  {rid}  (terminal {td})")
        for rid, td in not_yet:
            print(f"  hold     {rid}  (terminal {td} > boundary)")
        for rid in no_date:
            print(f"  SKIP     {rid}  (no parseable terminal date — fix the "
                  f"record's terminal-date field before it can compact)")

    if not any_eligible:
        print("No records eligible for compaction at this boundary.")
    return 0


if __name__ == "__main__":
    # Report output is machine-parsed, so emit deterministic UTF-8
    # regardless of console code page — Windows cp1252 or a POSIX C
    # locale must never crash on report typography (—, ≤, →) (R-010).
    for _stream in (sys.stdout, sys.stderr):
        _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv))
