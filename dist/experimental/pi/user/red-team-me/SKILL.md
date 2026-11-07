---
name: red-team-me
description: Adversarially stress-test the decisions record by hunting for failure modes, hidden assumptions, and missing pieces. Use after challenge-me, before implementation, or whenever the user wants an outside-view critique of a plan.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Hunt for what breaks in the accepted decisions, and record each concrete failure mode as a `pending` risk. Be adversarial: find failures, don't validate.

**Reads:** latest `retrospectives/` entry, `decisions/INDEX.md`, bodies of the decisions under test, optionally the Graphiti graph; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `risks/R-NNN.md` + INDEX files (via script).

## Steps

1. **Scope.** Project or one feature. Risks live in the same scope.

2. **Prior calibration.** Load the newest retrospective named in `retrospectives/INDEX.md`. Apply its `Watch-for` failure patterns first, and avoid its known mis-calibrations (e.g. predicting contention with no traffic evidence).

3. **Pick targets.** From `decisions/INDEX.md`, load the bodies of the accepted decisions you are testing. Titles tell you which ones to load. Settled decisions (in `decisions/archive/`) are implemented, verified, and retrospective-reviewed, so skip them unless the user names one.

4. **Prior failures (optional, advisory).** Per target: `python3 ~/.treenail/scripts/graph_query.py docs "<the decision being tested>" --scope all`. A related risk that materialized elsewhere points toward an evidence-backed failure mode. Re-derive it for this decision; don't copy it.

5. **Hunt.** For each decision, ask:
   - What hidden assumption makes this work?
   - What does it implicitly forbid that may be needed later?
   - What environment or dependency is it sensitive to?
   - What's the blast radius if it's wrong?
   - What does it fail to cover?

   One risk per *concrete* failure mode, not abstract categories. Prefer evidence-backed failure modes over speculative ones.

6. **Write each risk.**
   - `python3 ~/.treenail/scripts/bootstrap.py <scope-dir> risks` once.
   - `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/risks R` per risk; body per spec § RISKS. Set Severity and Likelihood and `Disposition: pending`; leave Date, Disposition rationale, and Action empty; `Related decisions` names the source decision(s).
   - `python3 ~/.treenail/scripts/reindex.py <scope-dir> risks`.

## Never

- Propose fixes. That's `triage-risks`.
- Pad. If an area has no meaningful risk, say so; a short honest list beats a long ceremonial one.

## Next

- `triage-risks`.
