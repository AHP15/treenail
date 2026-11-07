---
name: red-team-me
description: Adversarially stress-test the decisions record by hunting for failure modes, hidden assumptions, and missing pieces. Use after challenge-me, before implementation, or whenever the user wants an outside-view critique of a plan.
---

Hunt for what breaks in the accepted decisions, and record each concrete failure mode as a `pending` risk. Be adversarial: find failures, don't validate.

**Reads:** latest `retrospectives/` entry, `decisions/INDEX.md`, bodies of the decisions under test, optionally the Graphiti graph; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `risks/R-NNN.md` + INDEX files (via script).

## Steps

1. **Scope.** Project or one feature. Risks live in the same scope.

2. **Prior calibration.** Load the newest retrospective named in `retrospectives/INDEX.md`. Apply its `Watch-for` failure patterns first, and avoid its known mis-calibrations (e.g. predicting contention with no traffic evidence).

3. **Pick targets.** From `decisions/INDEX.md`, load the bodies of the accepted decisions you are testing. Titles tell you which ones to load. Settled decisions (in `decisions/archive/`) are implemented, verified, and retrospective-reviewed, so skip them unless the user names one.

4. **Prior failures (optional, advisory).** Per target: `python3 ~/.claude/skills/_shared/scripts/graph_query.py docs "<the decision being tested>" --scope all`. A related risk that materialized elsewhere points toward an evidence-backed failure mode. Re-derive it for this decision; don't copy it.

5. **Hunt.** For each decision, ask:
   - What hidden assumption makes this work?
   - What does it implicitly forbid that may be needed later?
   - What environment or dependency is it sensitive to?
   - What's the blast radius if it's wrong?
   - What does it fail to cover?

   One risk per *concrete* failure mode, not abstract categories. Prefer evidence-backed failure modes over speculative ones.

6. **Write each risk.**
   - `python3 ~/.claude/skills/_shared/scripts/bootstrap.py <scope-dir> risks` once.
   - `python3 ~/.claude/skills/_shared/scripts/mint_id.py <scope-dir>/risks R` per risk; body per spec § RISKS. Set Severity and Likelihood and `Disposition: pending`; leave Date, Disposition rationale, and Action empty; `Related decisions` names the source decision(s).
   - `python3 ~/.claude/skills/_shared/scripts/reindex.py <scope-dir> risks`.

## Never

- Propose fixes. That's `triage-risks`.
- Pad. If an area has no meaningful risk, say so; a short honest list beats a long ceremonial one.

## Next

- `triage-risks`.
