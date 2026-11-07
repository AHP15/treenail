#!/usr/bin/env python3
"""audit.py — mechanically-decidable invariant checks for a docs scope.

Runs the structural invariants from the `audit-artifacts` skill that can
be decided without judgment, and prints a severity-grouped report
(BLOCKER / WARN / INFO). It NEVER modifies a file. The skill layers the
judgment-only findings (defer-trigger quality, smells that need
task-status reasoning, "has decompose-plan run yet") on top of this.

Field-completeness is checked for ACTIVE records only; archived records
are terminal/frozen and only their ID-resolution and link symmetry are
checked (matching the skill's bounded-audit rule).

The INDEX-consistency check reuses reindex.py's projection, so "does the
INDEX match its records" is decided by the exact same code that rebuilds
it — never a second, drifting implementation.

Usage:
    audit.py <scope-dir> [--project <project-docs-dir>]

  <scope-dir>   docs root for the scope, e.g. `docs` or
                `docs/features/<feature>`.
  --project     project docs root, for cross-scope promotion-symmetry
                checks when <scope-dir> is a feature. Auto-derived from a
                `.../features/<name>` path when omitted.

Exit codes: 0 no blockers; 1 one or more BLOCKERs; 2 usage error.
"""

import os
import re
import sys

import anchors
import reindex  # same dir; import-safe (guarded by __main__)

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DEC_STATUS = {"accepted", "superseded", "deprecated", "promoted"}
RISK_DISP = {"pending", "fix", "mitigate", "accept", "defer"}
TASK_STATUS = {"todo", "in_progress", "done", "dropped"}
SIZES = {"S", "M", "L"}
SEVERITY = {"low", "medium", "high", "critical"}
LIKELIHOOD = {"low", "medium", "high"}
DEC_TERMINAL_DATE = {
    "superseded": "Date superseded",
    "deprecated": "Date deprecated",
    "promoted": "Date promoted",
}


class Findings:
    def __init__(self):
        self.items = []  # (severity, code, msg)

    def add(self, sev, msg):
        self.items.append((sev, msg))

    blocker = lambda self, m: self.add("BLOCKER", m)
    warn = lambda self, m: self.add("WARN", m)
    info = lambda self, m: self.add("INFO", m)


def load_scope(scope, artifact):
    """Return dict id -> (title, fields, is_active) for an artifact."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope, artifact)
    out = {}
    for active, d in ((True, base), (False, os.path.join(base, "archive"))):
        for path in reindex.record_files(d, prefix):
            rid, title, fields = reindex.parse_record(path)
            if rid is None:
                out.setdefault("__empty__", []).append(os.path.basename(path))
                continue
            out[rid] = (title, fields, active, path)
    return out


def check_index(scope, artifact, f):
    """Compare on-disk INDEX.md to reindex's projection (read-only)."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope, artifact)
    for sub, label in ((base, f"{artifact}/INDEX.md"),
                       (os.path.join(base, "archive"), f"{artifact}/archive/INDEX.md")):
        idx_path = os.path.join(sub, "INDEX.md")
        expected = []
        for path in reindex.record_files(sub, prefix):
            rid, title, fields = reindex.parse_record(path)
            if rid is None:
                continue
            expected.append(reindex.project(artifact, rid, title, fields, []))
        expected.sort(key=lambda ln: int(ln.split(" | ")[0].split("-")[1]))
        actual = []
        if os.path.exists(idx_path):
            with open(idx_path, encoding="utf-8") as fh:
                actual = [ln for ln in fh.read().splitlines() if ln.strip()]
        if expected != actual:
            f.blocker(f"INDEX drift in {label}: does not match record projection "
                      f"— fix with `reindex.py {scope} {artifact}`")


def require(rid, fields, names, f):
    for n in names:
        if not fields.get(n, "").strip():
            f.blocker(f"{rid}: missing/empty required field '{n}'")


def check_dates(rid, fields, f, *names):
    for n in names:
        v = fields.get(n, "").strip()
        if v and not ISO_RE.match(v):
            f.info(f"{rid}: '{n}' is not ISO YYYY-MM-DD ({v!r})")


def ids_gaps(records, prefix, f):
    nums = sorted(int(k.split("-")[1]) for k in records if k != "__empty__")
    for a, b in zip(nums, nums[1:]):
        if b - a > 1:
            lo, hi = a + 1, b - 1
            rng = (f"{prefix}-{lo:03d}" if lo == hi
                   else f"{prefix}-{lo:03d}..{prefix}-{hi:03d}")
            # One INFO per contiguous gap, not one per missing ID — gaps are
            # the expected, harmless trace of lost mint races; enumerating
            # every number just drowns the report.
            f.info(f"{rng}: ID gap (harmless lost-mint trace; never renumber)")
    for name in records.get("__empty__", []):
        f.blocker(f"{name}: empty/field-less record (died-mid-claim residue) — fill it in or give it a minimal dropped/deprecated body; never delete")


def check_filename_id(scope, artifact, f):
    """Header ID must match the filename, and an ID must not exist in both
    the active and archive dirs. mint_id.py prevents both, but a manual edit
    can introduce them and nothing else catches it."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope, artifact)
    name_re = re.compile(r"^" + prefix + r"-(\d+)\.md$")
    seen = {}
    for loc, d in (("active", base), ("archive", os.path.join(base, "archive"))):
        for path in reindex.record_files(d, prefix):
            name = os.path.basename(path)
            m = name_re.match(name)
            n = int(m.group(1)) if m else None
            file_id = f"{prefix}-{n:03d}" if n is not None else None
            expected_name = f"{file_id}.md" if file_id else None
            if n is not None and n <= 0:
                f.blocker(f"{name}: ID number must be >= 001")
            if expected_name and name != expected_name:
                f.blocker(f"{name}: filename must be zero-padded as "
                          f"{expected_name}")
            rid, _, _ = reindex.parse_record(path)
            if rid and file_id and rid != file_id:
                f.blocker(f"{name}: header ID {rid!r} does not match filename "
                          f"(expected header `## {file_id}: …`)")
            key = rid or file_id
            if key in seen:
                f.blocker(f"{key}: exists in both {seen[key]} and {loc} dirs "
                          f"— an ID must be unique across active+archive")
            else:
                seen[key] = loc


def check_retro_index(scope, f):
    """retrospectives/INDEX.md is a projection too — check it for drift."""
    d = os.path.join(scope, "retrospectives")
    if not os.path.isdir(d):
        return
    expected = reindex.retro_lines(d, [])
    idx_path = os.path.join(d, "INDEX.md")
    actual = []
    if os.path.exists(idx_path):
        with open(idx_path, encoding="utf-8") as fh:
            actual = [ln for ln in fh.read().splitlines() if ln.strip()]
    if expected != actual:
        f.blocker(f"INDEX drift in retrospectives/INDEX.md: does not match "
                  f"projection — fix with `reindex.py {scope} retrospectives`")


def check_decisions(scope, decs, f):
    is_feature = "/features/" in scope.replace(os.sep, "/")
    for rid, (title, fields, active, _) in decs.items():
        if rid == "__empty__":
            continue
        status = fields.get("Status", "").strip()
        if active:
            require(rid, fields, ["Status", "Date", "Context", "Decision", "Rationale"], f)
            if not title:
                f.blocker(f"{rid}: missing Title (header `## {rid}: <title>`)")
        if status and status not in DEC_STATUS:
            f.blocker(f"{rid}: invalid Status {status!r}")
        sup_by = reindex.ids_in(fields.get("Superseded by", ""), "D")
        supersedes = reindex.ids_in(fields.get("Supersedes", ""), "D")
        promoted_to = fields.get("Promoted to", "").strip()
        terminal_field = DEC_TERMINAL_DATE.get(status)
        if terminal_field:
            if not fields.get(terminal_field, "").strip():
                f.warn(f"{rid}: terminal decision missing '{terminal_field}' "
                       f"(archive compaction will hold it)")
            check_dates(rid, fields, f, terminal_field)
        if status == "superseded" and not sup_by:
            f.blocker(f"{rid}: status superseded but no 'Superseded by'")
        if status == "deprecated" and sup_by:
            f.blocker(f"{rid}: deprecated must have no successor (has 'Superseded by')")
        if status == "promoted":
            if not is_feature:
                f.blocker(f"{rid}: project-level decision cannot be 'promoted'")
            if "project:" not in promoted_to:
                f.blocker(f"{rid}: promoted but no 'Promoted to: project:D-NNN'")
            if sup_by or supersedes:
                f.blocker(f"{rid}: promoted decision must not have Supersedes/Superseded by")
        if status == "superseded" and promoted_to:
            f.blocker(f"{rid}: decision is both superseded and promoted (mutually exclusive)")
        # supersession symmetry within scope
        for tgt in sup_by:
            if tgt not in decs:
                f.blocker(f"{rid}: 'Superseded by: {tgt}' does not resolve in scope")
            else:
                back = reindex.ids_in(decs[tgt][1].get("Supersedes", ""), "D")
                if rid not in back:
                    f.blocker(f"{rid}↔{tgt}: supersession not symmetric ({tgt} lacks 'Supersedes: {rid}')")
        for tgt in supersedes:
            if tgt not in decs:
                f.blocker(f"{rid}: 'Supersedes: {tgt}' does not resolve in scope")
        check_dates(rid, fields, f, "Date")


def check_risks(scope, risks, decs, tasks, f, decompose_ran):
    is_feature = "/features/" in scope.replace(os.sep, "/")
    for rid, (title, fields, active, _) in risks.items():
        if rid == "__empty__":
            continue
        disp = fields.get("Disposition", "").strip()
        if active:
            require(rid, fields, ["Severity", "Likelihood", "Disposition", "Description"], f)
        sev = fields.get("Severity", "").strip()
        if sev and sev not in SEVERITY:
            f.blocker(f"{rid}: invalid Severity {sev!r}")
        lk = fields.get("Likelihood", "").strip()
        if lk and lk not in LIKELIHOOD:
            f.blocker(f"{rid}: invalid Likelihood {lk!r}")
        if disp and disp not in RISK_DISP:
            f.blocker(f"{rid}: invalid Disposition {disp!r}")
        if disp == "pending":
            f.blocker(f"{rid}: Disposition is 'pending' — triage-risks must resolve it before downstream")
        elif active:
            require(rid, fields, ["Date", "Disposition rationale", "Action"], f)
        # Related decisions
        rel = reindex.ids_in(fields.get("Related decisions", ""), "D")
        if active and not rel:
            # Optional per spec (a standalone risk on undecided code is
            # legal), so its absence is a coverage note, not a smell.
            f.info(f"{rid}: no 'Related decisions' (optional; standalone risk)")
        for d in rel:
            if d not in decs:
                f.blocker(f"{rid}: 'Related decisions: {d}' does not resolve in scope")
        # mitigate task linkage
        action = fields.get("Action", "")
        if disp == "mitigate":
            tids = reindex.ids_in(action, "T")
            if not tids:
                if decompose_ran:
                    f.blocker(f"{rid}: mitigate risk has no task IDs though decompose-plan has run for the scope")
                else:
                    f.warn(f"{rid}: mitigate risk not yet decomposed into tasks (expected before decompose-plan runs)")
            else:
                missing = [t for t in tids if t not in tasks]
                if missing:
                    f.blocker(f"{rid}: mitigate Action names missing task(s) {','.join(missing)}")
                elif all(tasks[t][1].get("Status", "").strip() == "dropped" for t in tids):
                    f.warn(f"{rid}: all mitigating tasks {','.join(tids)} are dropped — mitigation is notional")
        if disp == "fix":
            fix_decs = reindex.ids_in(action, "D")
            if not fix_decs:
                f.blocker(f"{rid}: fix risk Action references no superseding decision")
            else:
                missing = [d for d in fix_decs if d not in decs]
                if missing:
                    f.blocker(f"{rid}: fix Action names missing decision(s) "
                              f"{','.join(missing)}")
                present = [d for d in fix_decs if d in decs]
                if present and not any(
                    reindex.ids_in(decs[d][1].get("Supersedes", ""), "D")
                    for d in present
                ):
                    f.blocker(f"{rid}: fix Action references decision(s) "
                              f"{','.join(present)} but none has a "
                              f"'Supersedes' link")
        if fields.get("Promoted to", "").strip() and not is_feature:
            f.blocker(f"{rid}: 'Promoted to' only valid at feature scope")
        if disp in {"fix", "defer"} and not active and not fields.get("Date resolved", "").strip():
            f.warn(f"{rid}: archived {disp} risk missing 'Date resolved' "
                   f"(archive compaction will hold it)")
        check_dates(rid, fields, f, "Date", "Date resolved")


def check_tasks(scope, tasks, decs, risks, f):
    # dependency graph for cycle detection (within scope)
    deps = {}
    for rid, (title, fields, active, _) in tasks.items():
        if rid == "__empty__":
            continue
        status = fields.get("Status", "").strip()
        if active:
            require(rid, fields, ["Status", "Size", "Acceptance"], f)
            if not title:
                f.blocker(f"{rid}: missing Title")
        size = fields.get("Size", "").strip()
        if size and size not in SIZES:
            f.blocker(f"{rid}: invalid Size {size!r} (must be S/M/L; larger must split)")
        if status and status not in TASK_STATUS:
            f.blocker(f"{rid}: invalid Status {status!r}")
        impl = reindex.ids_in(fields.get("Implements", ""), "D")
        mit = reindex.ids_in(fields.get("Mitigates", ""), "R")
        if active and not impl and not mit:
            f.blocker(f"{rid}: task has neither 'Implements' nor 'Mitigates' (≥1 required)")
        for d in impl:
            if d not in decs:
                f.blocker(f"{rid}: 'Implements: {d}' does not resolve in scope")
        for r in mit:
            if r not in risks:
                f.blocker(f"{rid}: 'Mitigates: {r}' does not resolve in scope")
        date_done = fields.get("Date done", "").strip()
        if status == "done" and not date_done:
            f.blocker(f"{rid}: status done but empty 'Date done'")
        if status != "done" and date_done:
            f.info(f"{rid}: 'Date done' set but status is {status!r}")
        if status == "dropped" and not fields.get("Notes", "").strip():
            f.blocker(f"{rid}: dropped task missing 'Notes'")
        date_dropped = fields.get("Date dropped", "").strip()
        if status == "dropped" and not date_dropped:
            f.warn(f"{rid}: dropped task has no 'Date dropped' — its body can never "
                   f"compact (compact-select skips it); add the drop date as a field")
        if status != "dropped" and date_dropped:
            f.info(f"{rid}: 'Date dropped' set but status is {status!r}")
        if status == "done" and active and not fields.get("Evidence", "").strip():
            f.info(f"{rid}: done task has no Evidence anchor (coverage gap)")
        # Evidence anchor shape. A `done` task's Evidence is the proof
        # reconcile-status resolves against the tree, so an unresolvable
        # (prose, not anchor) Evidence on a done task is a BLOCKER — it
        # silently defeats plan-vs-code drift detection. On a not-yet-done
        # task it is only a WARN (still being authored).
        ev = fields.get("Evidence", "")
        anchor_texts = anchors.extract_anchor_texts(ev)
        report = f.blocker if status == "done" else f.warn
        for a in anchor_texts:
            _kind, _parts, err = anchors.parse_anchor(a)
            if err:
                report(f"{rid}: malformed Evidence anchor {a!r}: {err}"
                       f"{' — done task: Evidence must be machine-resolvable' if status == 'done' else ''}")
        d = reindex.ids_in(fields.get("Depends on", ""), "T")
        deps[rid] = d
        for t in d:
            if t not in tasks:
                f.blocker(f"{rid}: 'Depends on: {t}' does not resolve in scope")
        check_dates(rid, fields, f, "Date done", "Date dropped")
    # cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in deps}
    stack = []

    def dfs(u):
        color[u] = GRAY
        stack.append(u)
        for v in deps.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                cyc = stack[stack.index(v):] + [v]
                f.blocker(f"dependency cycle: {' → '.join(cyc)}")
                return True
            if color[v] == WHITE and dfs(v):
                return True
        stack.pop()
        color[u] = BLACK
        return False

    for k in deps:
        if color[k] == WHITE:
            dfs(k)


def check_terminal_in_active(decs, risks, tasks, f):
    for rid, (_, fields, active, _) in decs.items():
        if rid == "__empty__":
            continue
        if active and fields.get("Status", "").strip() in {"superseded", "deprecated", "promoted"}:
            f.info(f"{rid}: terminal decision still in active dir (awaiting archive-cycle reap)")
    for rid, (_, fields, active, _) in tasks.items():
        if rid == "__empty__":
            continue
        if active and fields.get("Status", "").strip() in {"done", "dropped"}:
            f.info(f"{rid}: terminal task still in active dir (awaiting archive-cycle reap)")


def mitigation_decomposition_started(risks, tasks):
    """Heuristic for whether mitigation task backfill has begun.

    Brownfield extraction can create implementation-only done tasks before
    decompose-plan runs. Treat decomposition as started only once at least
    one task mitigates a risk, or at least one mitigate-risk Action names a
    concrete task ID.
    """
    for rid, record in tasks.items():
        if rid == "__empty__":
            continue
        _title, fields, _active, _path = record
        if reindex.ids_in(fields.get("Mitigates", ""), "R"):
            return True
    for rid, record in risks.items():
        if rid == "__empty__":
            continue
        _title, fields, _active, _path = record
        if fields.get("Disposition", "").strip() == "mitigate":
            if reindex.ids_in(fields.get("Action", ""), "T"):
                return True
    return False


def feature_project_scope(scope):
    norm = scope.replace(os.sep, "/").rstrip("/")
    m = re.match(r"^(.*)/features/([^/]+)$", norm)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def project_ref(value, prefix):
    m = re.search(r"\bproject:(" + prefix + r"-\d+)\b", value or "")
    return m.group(1) if m else None


def promoted_from_ref(value, prefix):
    m = re.search(r"\bfeature:([^/]+)/(" + prefix + r"-\d+)\b", value or "")
    if not m:
        return None, None
    return m.group(1), m.group(2)


# Scope-local link fields on a risk. When promote copies a risk up, a bare
# ID left in these still names a *feature* record but would be resolved
# against the project scope. promote rewrites them to qualified
# `feature:<name>/X-NNN` form; a bare ID matching the source is a copy slip.
# (Decisions need no equivalent: a promoted decision may not carry
# Supersedes/Superseded by at all.)
RISK_SCOPE_LOCAL_LINKS = (("Related decisions", "D"), ("Action", "D"), ("Action", "T"))


def check_copied_links(src_id, src_fields, dest_label, dest_fields, f):
    for field, prefix in RISK_SCOPE_LOCAL_LINKS:
        src_ids = set(reindex.ids_in(src_fields.get(field, ""), prefix))
        dest_ids = reindex.ids_in(dest_fields.get(field, ""), prefix)
        copied = [i for i in dest_ids if i in src_ids]
        if copied:
            f.warn(f"{dest_label}: '{field}' has bare {','.join(copied)} copied "
                   f"from {src_id} — feature-scope IDs resolve against the "
                   f"project here; qualify them as feature:<name>/<ID>")


def check_feature_promotions(feature_scope, feature_name, project_scope, f):
    if not project_scope or not os.path.isdir(project_scope):
        return

    fdecs = load_scope(feature_scope, "decisions")
    frisks = load_scope(feature_scope, "risks")
    pdecs = load_scope(project_scope, "decisions")
    prisks = load_scope(project_scope, "risks")

    for did, record in fdecs.items():
        if did == "__empty__":
            continue
        _title, fields, _active, _path = record
        dest = project_ref(fields.get("Promoted to", ""), "D")
        if not dest:
            continue
        if dest not in pdecs:
            f.blocker(f"{did}: Promoted to project:{dest} but destination "
                      f"decision does not exist")
            continue
        expected = f"feature:{feature_name}/{did}"
        actual = pdecs[dest][1].get("Promoted from", "").strip()
        if actual != expected:
            f.blocker(f"{did}↔project:{dest}: promotion not symmetric "
                      f"(project record Promoted from is {actual!r}, "
                      f"expected {expected!r})")

    for rid, record in frisks.items():
        if rid == "__empty__":
            continue
        _title, fields, _active, _path = record
        dest = project_ref(fields.get("Promoted to", ""), "R")
        if not dest:
            continue
        if dest not in prisks:
            f.blocker(f"{rid}: Promoted to project:{dest} but destination "
                      f"risk does not exist")
            continue
        expected = f"feature:{feature_name}/{rid}"
        actual = prisks[dest][1].get("Promoted from", "").strip()
        if actual != expected:
            f.blocker(f"{rid}↔project:{dest}: promotion not symmetric "
                      f"(project record Promoted from is {actual!r}, "
                      f"expected {expected!r})")

    for did, record in pdecs.items():
        if did == "__empty__":
            continue
        _title, fields, _active, _path = record
        feat, src = promoted_from_ref(fields.get("Promoted from", ""), "D")
        if feat != feature_name:
            continue
        if src not in fdecs:
            f.blocker(f"project:{did}: Promoted from feature:{feat}/{src} "
                      f"but source decision does not exist")
            continue
        expected = f"project:{did}"
        actual = fdecs[src][1].get("Promoted to", "").strip()
        if actual != expected:
            f.blocker(f"project:{did}↔{src}: promotion not symmetric "
                      f"(feature record Promoted to is {actual!r}, "
                      f"expected {expected!r})")

    for rid, record in prisks.items():
        if rid == "__empty__":
            continue
        _title, fields, _active, _path = record
        feat, src = promoted_from_ref(fields.get("Promoted from", ""), "R")
        if feat != feature_name:
            continue
        if src not in frisks:
            f.blocker(f"project:{rid}: Promoted from feature:{feat}/{src} "
                      f"but source risk does not exist")
            continue
        check_copied_links(src, frisks[src][1], f"project:{rid}", fields, f)
        expected = f"project:{rid}"
        actual = frisks[src][1].get("Promoted to", "").strip()
        if actual != expected:
            f.blocker(f"project:{rid}↔{src}: promotion not symmetric "
                      f"(feature record Promoted to is {actual!r}, "
                      f"expected {expected!r})")


def check_promotion_symmetry(scope, explicit_project_scope, f):
    project_scope, feature_name = feature_project_scope(scope)
    if feature_name:
        check_feature_promotions(
            scope, feature_name, explicit_project_scope or project_scope, f
        )
        return

    feature_root = os.path.join(scope, "features")
    if not os.path.isdir(feature_root):
        return
    for name in sorted(os.listdir(feature_root)):
        feature_scope = os.path.join(feature_root, name)
        if os.path.isdir(feature_scope):
            check_feature_promotions(feature_scope, name, scope, f)


def check_retrospectives(scope, f):
    d = os.path.join(scope, "retrospectives")
    if not os.path.isdir(d):
        return
    for name in sorted(os.listdir(d)):
        if not re.match(r"^\d{4}-\d{2}-\d{2}\.md$", name):
            continue
        _, _, fields = reindex.parse_record(os.path.join(d, name))
        b = fields.get("Boundary-end", "").strip()
        if not b:
            f.warn(f"retrospectives/{name}: no 'Boundary-end' field — compaction "
                   f"cannot advance its frontier from this retro (fail-safe: it skips)")
        elif not ISO_RE.match(b):
            f.warn(f"retrospectives/{name}: 'Boundary-end' is not ISO YYYY-MM-DD ({b!r})")


def main(argv):
    args = []
    explicit_project_scope = None
    i = 1
    while i < len(argv):
        if argv[i] == "--project" and i + 1 < len(argv):
            explicit_project_scope = argv[i + 1]
            i += 2
            continue
        if argv[i].startswith("--"):
            print(f"audit.py: unknown option {argv[i]}", file=sys.stderr)
            return 2
        args.append(argv[i])
        i += 1
    if not args:
        print("usage: audit.py <scope-dir> [--project <project-docs-dir>]", file=sys.stderr)
        return 2
    scope = os.path.expanduser(args[0])
    if not os.path.isdir(scope):
        print(f"audit.py: no such scope dir: {scope}", file=sys.stderr)
        return 2

    f = Findings()
    decs = load_scope(scope, "decisions")
    risks = load_scope(scope, "risks")
    tasks = load_scope(scope, "tasks")

    decompose_ran = mitigation_decomposition_started(risks, tasks)

    for artifact, records in (("decisions", decs), ("risks", risks), ("tasks", tasks)):
        check_index(scope, artifact, f)
        check_filename_id(scope, artifact, f)
        ids_gaps(records, reindex.PREFIX[artifact], f)

    check_decisions(scope, decs, f)
    check_risks(scope, risks, decs, tasks, f, decompose_ran)
    check_tasks(scope, tasks, decs, risks, f)
    check_terminal_in_active(decs, risks, tasks, f)
    check_retrospectives(scope, f)
    check_retro_index(scope, f)
    check_promotion_symmetry(scope, explicit_project_scope, f)

    order = {"BLOCKER": 0, "WARN": 1, "INFO": 2}
    f.items.sort(key=lambda x: order[x[0]])
    counts = {"BLOCKER": 0, "WARN": 0, "INFO": 0}
    for sev, _ in f.items:
        counts[sev] += 1

    print(f"audit {scope}: {counts['BLOCKER']} blocker(s), "
          f"{counts['WARN']} warn, {counts['INFO']} info")
    cur = None
    for sev, msg in f.items:
        if sev != cur:
            print(f"\n== {sev} ==")
            cur = sev
        print(f"  {msg}")
    if not f.items:
        print("  clean — no mechanical violations")
    print("\nNote: judgment checks (defer-trigger quality and uncovered/"
          "orphan/silent-reversal smells) are the skill's to layer on top.")
    return 1 if counts["BLOCKER"] else 0


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
