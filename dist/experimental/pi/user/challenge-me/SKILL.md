---
name: challenge-me
description: Thoroughly interview the user about a plan or design, surfacing the implicit and unstated decisions hidden in their framing, resolving everything in order of leverage, and producing a decisions record at the end. Use this whenever the user wants to stress-test a plan, pressure-test a design, find the hidden decisions in a plan, or mentions "challenge me" or "grill me" — even if they don't use those exact words.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Interview me systematically until all the important decisions are settled, including the ones I haven't noticed I'm making. Walk the decision tree in leverage order, grow it as answers spawn new branches, then write one decision record per resolved decision.

**Reads:** latest `retrospectives/` entry, `decisions/INDEX.md`, the codebase, optionally the Graphiti graph; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `decisions/D-NNN.md` + `decisions/INDEX.md` (and the conventions bootstrap on a fresh project).

## Steps

1. **Scope.** Confirm what we're designing, what's already decided (don't re-litigate), what's out of scope, and project-level (`docs`) vs feature-level (`docs/features/<name>`). List the decision branches in rough order and confirm the ordering before diving in.

2. **Prior calibration.** Load the newest retrospective named in `retrospectives/INDEX.md`. Its `Watch-for` items are where this project has mis-calibrated before — carry them into the ordering and your recommendations. No retrospective = greenfield, not an error.

3. **Existing constraints.** Read `decisions/INDEX.md`; titles are usually enough. Load a `D-NNN.md` body only when a question depends on it.

4. **Prior art (optional, advisory).** Per major branch: `python3 ~/.treenail/scripts/graph_query.py docs "<the design problem in a sentence>" --scope all`. Hits from other scopes inform ordering and recommendations, never settle anything. Silence (no graph, no hits) changes nothing.

5. **Surface unstated premises.** Ask what the framing assumes without saying — single-tenant, synchronous, one writer, never-deleted, trusted caller, English-only, fits-in-memory. Scan the code for commitments it already makes (schema, boundaries, concurrency model, error contract). Each premise or commitment becomes a node to ratify or reject — code shows what *is*, never what *should be*.

6. **Order by leverage.** Hardest-to-reverse and most load-bearing first (data model, trust boundaries, core abstractions); cosmetic last; dependencies before dependents. Re-rank continuously as the tree grows (step 9).

7. **Ask, one question at a time.**
   - Settle questions of *fact* from the codebase yourself; don't make me confirm what the code states. If what you find would settle a *design* choice, present it as your proposal with its provenance ("the code does X; I'd keep it because Y — does that work?").
   - **Hard rule — rationale first.** Every question carries your recommended answer plus a 1-2 sentence "this over the alternatives because…" **in the chat as prose**, before or alongside the question. This holds when you also render a structured option list (e.g. `AskUserQuestion`): terse option descriptions do not count as the rationale, and the recommended option is marked. A question without a visible rationale is a defect.

8. **Handle the answer.**
   - Confirmed → resolved.
   - Redirected → take the new direction.
   - "I don't know" / "you decide" → your recommendation stands as a tentative default.
   - Pushback you still disagree with → argue once with your strongest reasoning, then defer.

9. **Grow the tree.** After each load-bearing resolution, before moving on:
   - **Children** — what decisions did this answer just create? (Event sourcing → snapshotting, event versioning, replay.)
   - **Depth** — stress it against failure / partial failure, concurrency, scale limits, trust boundary, evolution / migration, observability. Raise only the dimensions that genuinely bite.

   Splice new nodes into the ordering.

10. **Keep it honest.** If a new answer contradicts an earlier one, say so and confirm which to revise. Checkpoint with a short summary every ~5 resolutions. Stop when what remains is low-leverage, I'm satisfied, or answers need implementation feedback. Don't manufacture questions.

11. **Write the records.**
    - `python3 ~/.treenail/scripts/bootstrap.py <scope-dir> decisions` (idempotent; adopts the spec on a fresh project).
    - Per decision: `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/decisions D` claims the next ID and prints `D-NNN<TAB><path>`. Write the body there per spec § DECISIONS (`Status: accepted`). Where a decision came from code you read, say so in Context.
    - `python3 ~/.treenail/scripts/reindex.py <scope-dir> decisions`.
    - In chat, one line per decision.

## Never

- Ask an open-ended question without a recommendation.
- Re-litigate a recorded decision. Revising one is a supersession, made explicitly.

## Next

- `red-team-me` on the new decisions.
