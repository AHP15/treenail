#!/usr/bin/env python3
"""reconcile_smells.py — surface cross-record JUDGMENT smells (advisory).

`audit.py` decides hard, mechanical invariants (BLOCKER/WARN). This script
is its complement: it computes the *quality-half* heuristics that audit
deliberately leaves to a skill — second-order smells that are usually, but
not always, a problem, so they are surfaced for a human/model to adjudicate
rather than enforced. It is read-only and exits 0 even with findings: a
smell is a prompt to look, never a gate.

It is invoked by the `reconcile-status` skill, which layers judgment on the
output. The three smells are the missing symmetric halves of checks the
pipeline already does the failure-half of:

  1. UN-RED-TEAMED DECISION — an accepted decision with zero risks pointing
     at it. (audit already notes the inverse: a risk with no Related
     decisions.) A load-bearing decision that attracted no failure-mode
     hypothesis was either trivial or never adversarially examined.

  2. THIN DEFER — a high/critical risk deferred with no firing condition.
     A defer is where risks go to be quietly forgotten; a high one whose
     trigger names neither a measurable threshold NOR a concrete event is a
     deferral disguised as a decision. (Event triggers like "before adding
     tax" are valid — only a *vacuous* trigger flags.)

  3. MITIGATION COMPLETE — a mitigate risk whose every mitigating task is
     done. The mitigation shipped, so the risk should likely be re-triaged
     (mitigate -> accept, "residual acceptable") — which is also what makes
     it reap-eligible (mitigate has no reap path of its own; accept reaps
     after a retrospective). This is the routed close for the mitigate-reap
     gap: surface here, decide in triage-risks, reap in archive-cycle.

Usage:
    reconcile_smells.py <scope-dir>

Exit codes: 0 always (advisory). 2 usage error only.
"""

import os
import re
import sys

import reindex  # same dir; reuses parse_record / PREFIX / ids_in / record_files


# ---- trigger-quality heuristics (smell 2) --------------------------------
# A defer trigger is adequate if it names a MEASURABLE THRESHOLD or a
# CONCRETE EVENT. It is "thin" only when it names neither. This is why a
# digit-only check is wrong: event triggers ("before adding tax", "when a
# second currency is onboarded") are perfectly valid and carry no number.
THRESHOLD_RE = re.compile(
    r"\d|%|>|<|≥|≤|\b(exceed\w*|above|below|over|under|greater|less|reach\w*|"
    r"p50|p95|p99|threshold|latency|throughput|per[- ]second|count|rate|"
    r"quota|limit)\b", re.I)
EVENT_RE = re.compile(
    r"\b(before|when|once|upon|as soon as|the moment|the first of|first\b|"
    r"introduc\w*|onboard\w*|add(s|ing)?\b|implement\w*|ship\w*|migrat\w*|"
    r"enabl\w*|launch\w*|adopt\w*)\b", re.I)
VAGUE_RE = re.compile(
    r"\b(revisit later|monitor|keep an eye|as needed|if needed|as necessary|"
    r"tbd|reconsider later|down the road|eventually|someday|later on|"
    r"if it becomes|when it becomes)\b", re.I)


def load(scope, artifact):
    """id -> (title, fields, is_active), unioning active + archive."""
    prefix = reindex.PREFIX[artifact]
    base = os.path.join(scope, artifact)
    out = {}
    for active, d in ((True, base), (False, os.path.join(base, "archive"))):
        for path in reindex.record_files(d, prefix):
            rid, title, fields = reindex.parse_record(path)
            if rid:
                out[rid] = (title, fields, active)
    return out


def smell_unredteamed(decs, risks):
    """Accepted (active) decisions that no risk — active or archived —
    references in its Related decisions."""
    cited = set()
    for _rid, (_t, fields, _a) in risks.items():
        cited.update(reindex.ids_in(fields.get("Related decisions", ""), "D"))
    out = []
    for did, (title, fields, active) in sorted(decs.items()):
        if active and fields.get("Status", "").strip() == "accepted" and did not in cited:
            out.append((did, title))
    return out


def smell_thin_defer(risks):
    out = []
    for rid, (title, fields, active) in sorted(risks.items()):
        if not active:
            continue
        if fields.get("Disposition", "").strip() != "defer":
            continue
        if fields.get("Severity", "").strip() not in ("high", "critical"):
            continue
        action = fields.get("Action", "")
        has_threshold = bool(THRESHOLD_RE.search(action))
        has_event = bool(EVENT_RE.search(action))
        if not has_threshold and not has_event:
            why = "vague trigger" if VAGUE_RE.search(action) else "no firing condition"
            out.append((rid, title, why))
    return out


def smell_mitigation_complete(risks, tasks):
    out = []
    for rid, (title, fields, active) in sorted(risks.items()):
        if not active or fields.get("Disposition", "").strip() != "mitigate":
            continue
        tids = reindex.ids_in(fields.get("Action", ""), "T")
        if not tids:
            continue  # not-yet-decomposed; audit handles that
        statuses = [tasks.get(t, ("", {}, True))[1].get("Status", "").strip()
                    for t in tids]
        if any(t not in tasks for t in tids):
            continue  # missing tasks => reconcile's existing coverage failure
        if statuses and all(s == "done" for s in statuses):
            out.append((rid, title, tids))
    return out


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: reconcile_smells.py <scope-dir>", file=sys.stderr)
        return 2
    scope = os.path.expanduser(args[0])
    if not os.path.isdir(scope):
        print(f"reconcile_smells.py: no such scope dir: {scope}", file=sys.stderr)
        return 2

    decs = load(scope, "decisions")
    risks = load(scope, "risks")
    tasks = load(scope, "tasks")

    unredteamed = smell_unredteamed(decs, risks)
    thin = smell_thin_defer(risks)
    complete = smell_mitigation_complete(risks, tasks)

    total = len(unredteamed) + len(thin) + len(complete)
    print(f"judgment smells {scope}: {total} (advisory — adjudicate, do not auto-fix)")

    if unredteamed:
        print("\n== UN-RED-TEAMED DECISIONS (no risk points at them) ==")
        for did, title in unredteamed:
            print(f"  {did}: {title}")
        print("  → run /red-team-me scoped to these, or confirm the decision is trivial.")

    if thin:
        print("\n== THIN DEFERS (high/critical risk, no firing condition) ==")
        for rid, title, why in thin:
            print(f"  {rid} [{why}]: {title}")
        print("  → give each a measurable threshold or a concrete event trigger via /triage-risks,")
        print("    or it is a silent accept wearing a defer label.")

    if complete:
        print("\n== MITIGATION COMPLETE (all mitigating tasks done) ==")
        for rid, title, tids in complete:
            print(f"  {rid} (tasks {','.join(tids)} all done): {title}")
        print("  → re-triage mitigate → accept ('residual acceptable, shipped via these tasks')")
        print("    in /triage-risks; that also makes it reap-eligible at the next retrospective.")

    if not total:
        print("  clean — no judgment smells")
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
