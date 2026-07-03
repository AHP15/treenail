---
name: red-team-me
description: Adversarially stress-test the decisions record by hunting for failure modes, hidden assumptions, and missing pieces. Use after challenge-me, before implementation, or whenever the user wants an outside-view critique of a plan.
---
> Provider note (opencode): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Steps that write records shell out to `~/.keel` scripts and need file-write permission; in non-interactive runs approval must be granted up front.

> Keel shared runtime: paths under `~/.keel` are the installed Keel runtime. If the `KEEL_HOME` environment variable is set, read every `~/.keel/...` path as `$KEEL_HOME/...` instead.

Read the decisions in scope and produce per-risk files. Adversarial — find what breaks, don't validate.

1. Scope. Project-level (`/docs/decisions/INDEX.md`) or feature-level (`/docs/features/<feature>/decisions/INDEX.md`). Risks live in the same scope under `risks/`.

2. Prior calibration. Read the latest retrospective for the scope (most recent file in `retrospectives/`). Its `Watch-for` is prior context — apply those failure-mode patterns first. Note past mis-calibrations to avoid (e.g. over-predicting contention without traffic evidence).

3. Read `decisions/INDEX.md`. Load full D-NNN.md bodies only for the accepted decisions you're actively stress-testing. You don't need every decision's prose to think about failure modes — titles are usually enough to know what to load.

3b. Prior failures (advisory; optional). If the Graphiti graph is configured, query it per decision you're stress-testing for risks that materialized — or decisions that broke — elsewhere in the project, including other features:

   ```
   python3 ~/.keel/scripts/graph_query.py docs "<the decision being tested>" --scope all
   ```

   A hit on a related prior risk is a strong steer toward a concrete, evidence-backed failure mode rather than a speculative one (and it counters the over-prediction patterns the retrospective Watch-for warns about). Treat results as leads to investigate, not as risks to copy verbatim — re-derive the failure mode for *this* decision. If the script is silent (graph unavailable or no hits), continue with step 4 unchanged.

4. Hunt failure modes per accepted decision. For each, ask:
   - What hidden assumption makes this work?
   - What does this implicitly forbid that might be needed later?
   - What environment/dependency is it sensitive to?
   - What's the blast radius if it's wrong?
   - What does it not cover that probably should be covered?
   One risk per concrete failure mode — not abstract categories.
   Where step 3b surfaced a real prior failure, prefer it over a speculative one.

5. For each risk:
   - Mint the next R-NNN by running `python3 ~/.keel/scripts/mint_id.py <risks-dir> R` (e.g. `docs/risks` or `docs/features/<feature>/risks`). The script executes the **ID reservation protocol** — filesystem-arbitrated max over active + archive, atomic no-clobber claim, retry on collision — and prints the claimed `R-NNN` and its (empty) file path. Don't take the max from INDEX; it may lag. (Fall back to the protocol by hand per CONVENTIONS-SPEC.md if `python3` is unavailable.)
   - Write the body into the claimed `risks/R-NNN.md` per the RISKS section of `CONVENTIONS-SPEC.md`. Disposition: `pending`. Date, Disposition rationale, and Action stay empty — `triage-risks` fills them in.
   - Set `Related decisions: D-NNN` linking to the source decision(s).
   - Add its INDEX line: append `R-NNN | pending | <severity> | <title>` to `risks/INDEX.md`, or after writing all risks run `python3 ~/.keel/scripts/reindex.py <scope-dir> risks` (preferred when you wrote several).

6. Don't propose fixes. Triage is the next skill's job. Stay in failure-mode-finding mode.

7. Don't pad. If you don't see a meaningful risk in an area, say so. A short honest list beats a long ceremonial one.

8. On first run, ensure `docs/CONVENTIONS-SPEC.md` exists; if not, copy [~/.keel/conventions-spec.md](~/.keel/conventions-spec.md) and [~/.keel/conventions-examples.md](~/.keel/conventions-examples.md) to `docs/`.