---
name: retrospective
description: Harvest calibration signal from a completed planning cycle by walking decisions, risks, and tasks for structural evidence of what the plan got right and wrong, then writing a dated retrospective entry with a watch-for list that seeds future challenge-me and red-team-me cycles. Run at phase boundaries, milestones, or on cadence.
---

Read prior retrospective + current artifact state. Write a new retrospective file. Do not modify decisions/risks/tasks.

1. Scope. Project- or feature-level. Retrospectives live in `retrospectives/` (project-level: `/docs/retrospectives/`; feature-level: `/docs/features/<feature>/retrospectives/`).

2. Prior context. Read `retrospectives/INDEX.md`. If non-empty, load the most recent retrospective file — its `Watch-for` is what to grade in this retro's Prior watch-for review.

3. Cycle boundary. Confirm with the user what period this retro covers (date range, milestone, "since last retrospective"). Record it two ways: a human `Cycle` line, and a machine-readable **`Boundary-end: YYYY-MM-DD`** — the last day the cycle covers. `Boundary-end` is load-bearing: it is the frontier `archive-cycle` uses to decide which reaped records are safe to compact (everything terminal at or before it has now been harvested by this retro). For an open-ended "since last retrospective" cycle, set `Boundary-end` to today (the write date). Without a parseable `Boundary-end`, compaction will safely skip — so always emit it.

4. Gather evidence. Walk both the active `<artifact>/INDEX.md` and the `<artifact>/archive/INDEX.md` files; load specific records when citing them or when a one-line INDEX entry isn't enough. Records that turned terminal this cycle may already have been reaped into `archive/` (continuous reaping keeps the active set bounded) — their lines now live in `archive/INDEX.md` and their bodies are **uncompacted there, full prose intact**, so resolve each cited ID against both `<artifact>/<ID>.md` and `<artifact>/archive/<ID>.md`. This is the read that must happen *before* compaction, which is exactly why `archive-cycle` compacts only records a retrospective has already covered.
   - **Risks materialized**: dispositions that fired (`accept`s where the failure occurred, `defer`s whose triggers tripped, `mitigate`s that had to expand). Load the R-NNN.md to cite specifics.
   - **Risks didn't**: `defer`s well outside trigger range; `mitigate`s where the guard was over-engineered.
   - **Decisions held**: `accepted` still implemented with no related risks materialized.
   - **Decisions broke**: `superseded` or `deprecated` this cycle. Load both old and new D-NNN.md to cite the trigger.
   - **Silent reversals**: from `reconcile-status`'s last anomaly report.
   - **Tasks dropped mid-cycle**: read INDEX, cite Notes lines from T-NNN.md (load only those).
   - **Spikes**: did they resolve cleanly, or trigger cascades / re-splits?
   - **Prior watch-for**: each item from prior retro — hit, partial, didn't, plus misses (things that hit without being on the list).

5. Patterns. 2-5 calibration claims, each backed by ≥2 evidence items. These describe how this team mis-calibrates.

6. Watch-for. 3-7 concrete items for the next cycle, each tied to a pattern. These are the instructions for the next `challenge-me` and `red-team-me`.

7. Prior watch-for review. Mandatory from the second retro onward. Empty section on first only.

8. Write the file. Filename: `YYYY-MM-DD.md` in `retrospectives/`. Include the `Boundary-end` field (step 3). Append one line to `retrospectives/INDEX.md`: `YYYY-MM-DD | <cycle name>`. Follow the RETROSPECTIVES section of CONVENTIONS-SPEC.md.

9. Do not modify decisions/risks/tasks. Recommendations live in Watch-for; supersessions still flow through `challenge-me`, re-triages through `triage-risks`.

10. After writing, recommend running the `archive-cycle` skill — now that this retro has harvested them, it will compact the records that became terminal during this cycle (and reap any newly-terminal ones still in the active dir).
