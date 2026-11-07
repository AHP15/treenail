#!/usr/bin/env python3
"""reindex.py — rebuild INDEX.md files as a pure projection of records.

Implements the "INDEX projection" from CONVENTIONS-SPEC.md. The
per-record `<ID>.md` files are authoritative; each INDEX is a
deterministic function of the records in its directory. Two runs over
an unchanged record set produce byte-identical output, so INDEX drift
is always repaired by recomputation, never adjudicated.

Usage:
    reindex.py <scope-dir> [artifact ...]

  <scope-dir>  the docs root for a scope, e.g. `docs` or
               `docs/features/oauth-login`.
  artifact     one or more of: decisions risks tasks retrospectives.
               Default: all four.

For each artifact it rebuilds the active `<artifact>/INDEX.md` from the
records directly in `<artifact>/`, and `<artifact>/archive/INDEX.md`
from the records in `<artifact>/archive/` (retrospectives have no
archive). It writes ONLY INDEX.md files; record bodies are never
touched. A record missing a field the line format requires is emitted
with that field empty and reported as malformed — reindex cannot fix a
body, only the index.

Exit codes: 0 clean; 1 malformed records were found (index still
rebuilt); 2 usage error.
"""

import os
import re
import sys

HEADER_RE = re.compile(r"^##\s+([A-Za-z]-\d+):\s*(.*?)\s*$")
FIELD_RE = re.compile(r"^-\s+\*\*([^*]+)\*\*:\s?(.*)$")

PREFIX = {"decisions": "D", "risks": "R", "tasks": "T"}
REQUIRED = {
    "decisions": ["Status"],
    "risks": ["Disposition", "Severity"],
    "tasks": ["Status", "Size"],
}


def parse_record(path):
    """Return (id, title, fields) where fields maps name -> value.

    The header `## <ID>: <Title>` carries ID and Title. A field value is
    the rest of its `- **Name**:` line plus any following continuation
    lines, up to the next field marker — enough to recover IDs from a
    multi-line Action field.

    The parser is deliberately line-oriented: continuation lines (including
    sub-bullets and paragraphs separated by a blank line) are flattened into
    the current field's value with single-space joins. This is lossless for
    the INDEX, because every field the projection reads (Status, Disposition,
    Severity, Size, Date*, Superseded by, Promoted to, Implements, Mitigates,
    Action's IDs) is single-line or ID-bearing; it is mildly lossy for prose
    fields (Context/Rationale/Description) that only the graph projection
    reads. If a *projected* field ever becomes multi-line, revisit this.
    """
    rec_id, title = None, ""
    fields = {}
    cur = None
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            h = HEADER_RE.match(line)
            if h and rec_id is None:
                rec_id, title = h.group(1), h.group(2).strip()
                cur = None
                continue
            m = FIELD_RE.match(line)
            if m:
                cur = m.group(1).strip()
                fields[cur] = m.group(2).strip()
            elif cur is not None and line.strip():
                fields[cur] = (fields[cur] + " " + line.strip()).strip()
    return rec_id, title, fields


def ids_in(value, prefix):
    """Scope-local IDs of the given prefix in textual order, de-duplicated.

    Scope-qualified references (`project:D-001`, `feature:<name>/D-001`)
    are skipped: they point into another scope, so they must never be
    resolved — or projected — as if they were links in this one.
    """
    seen, out = set(), []
    for tok in re.findall(r"(?<![/:])\b" + prefix + r"-\d+\b", value or ""):
        if tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


def join_line(cols):
    """Pipe-join columns; trailing-empty columns leave a bare `|`, and
    no trailing whitespace remains (matches the spec line format)."""
    return (" | ".join(cols)).rstrip()


def project(artifact, rec_id, title, fields, malformed):
    """Project one record to its INDEX line for the given artifact."""
    def need(name):
        if name not in fields or fields[name] == "":
            malformed.append((rec_id, name))
            return ""
        return fields[name]

    if artifact == "decisions":
        status = need("Status")
        t = title
        sup = ids_in(fields.get("Superseded by", ""), "D")
        promo = fields.get("Promoted to", "")
        if sup:
            t = f"{t} (→ {sup[0]})"
        elif "project:" in promo:
            mm = re.search(r"project:D-\d+", promo)
            if mm:
                t = f"{t} (→ {mm.group(0)})"
        return join_line([rec_id, status, t])

    if artifact == "risks":
        disp = need("Disposition")
        sev = need("Severity")
        t = title
        if disp == "mitigate":
            tasks = ids_in(fields.get("Action", ""), "T")
            if tasks:
                t = f"{t} [tasks: {','.join(tasks)}]"
        return join_line([rec_id, disp, sev, t])

    if artifact == "tasks":
        status = need("Status")
        size = need("Size")
        refs = ids_in(fields.get("Implements", ""), "D") + ids_in(
            fields.get("Mitigates", ""), "R"
        )
        # Terminal-date column is status-gated: stale Date done/Date dropped
        # fields on reopened tasks are audit INFO, not projected state.
        if status == "done":
            terminal_date = fields.get("Date done", "")
        elif status == "dropped":
            terminal_date = fields.get("Date dropped", "")
        else:
            terminal_date = ""
        return join_line(
            [rec_id, status, size, ",".join(refs), title, terminal_date]
        )

    raise ValueError(artifact)


def record_files(d, prefix):
    if not os.path.isdir(d):
        return []
    pat = re.compile(r"^" + prefix + r"-(\d+)\.md$")
    out = []
    for name in os.listdir(d):
        m = pat.match(name)
        if m:
            out.append((int(m.group(1)), os.path.join(d, name)))
    out.sort(key=lambda x: x[0])
    return [p for _, p in out]


def retro_lines(d, malformed):
    if not os.path.isdir(d):
        return []
    pat = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
    rows = []
    for name in sorted(os.listdir(d)):
        m = pat.match(name)
        if not m:
            continue
        date = m.group(1)
        _, _, fields = parse_record(os.path.join(d, name))
        cycle = fields.get("Cycle", "")
        if cycle == "":
            malformed.append((date, "Cycle"))
        rows.append(join_line([date, cycle]))
    return rows


def write_index(path, lines):
    """Write the index; return (changed, added, removed) vs prior."""
    new = ("\n".join(lines) + "\n") if lines else ""
    prior = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            prior = fh.read()
    if new == prior:
        return False, 0, 0
    old_set = set(prior.splitlines())
    new_set = set(lines)
    added = len(new_set - old_set)
    removed = len(old_set - new_set)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    return True, added, removed


def reindex_artifact(scope, artifact, malformed):
    base = os.path.join(scope, artifact)
    reports = []

    if artifact == "retrospectives":
        lines = retro_lines(base, malformed)
        changed, a, r = write_index(os.path.join(base, "INDEX.md"), lines)
        reports.append((os.path.join(base, "INDEX.md"), len(lines), changed, a, r))
        return reports

    prefix = PREFIX[artifact]
    for sub, idx in ((base, "INDEX.md"), (os.path.join(base, "archive"), "INDEX.md")):
        lines = []
        for path in record_files(sub, prefix):
            rec_id, title, fields = parse_record(path)
            if rec_id is None:
                malformed.append((os.path.basename(path), "header/ID"))
                continue
            lines.append(project(artifact, rec_id, title, fields, malformed))
        lines.sort(key=lambda ln: int(ln.split(" | ")[0].split("-")[1]))
        idx_path = os.path.join(sub, idx)
        changed, a, r = write_index(idx_path, lines)
        reports.append((idx_path, len(lines), changed, a, r))
    return reports


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: reindex.py <scope-dir> [artifact ...]", file=sys.stderr)
        return 2
    scope = os.path.expanduser(argv[1])
    artifacts = argv[2:] or ["decisions", "risks", "tasks", "retrospectives"]
    valid = {"decisions", "risks", "tasks", "retrospectives"}
    bad = [a for a in artifacts if a not in valid]
    if bad:
        print(f"unknown artifact(s): {', '.join(bad)}", file=sys.stderr)
        return 2

    malformed = []
    all_reports = []
    for artifact in artifacts:
        all_reports.extend(reindex_artifact(scope, artifact, malformed))

    for path, n, changed, added, removed in all_reports:
        tag = "rebuilt" if changed else "unchanged"
        delta = f" (+{added}/-{removed})" if changed else ""
        print(f"{tag:9} {n:4d} lines  {path}{delta}")

    if malformed:
        print("\nMALFORMED records (body must be fixed by the owning skill):")
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
