---
name: task-brief
description: 'Drive implementation of the sequenced plan — work tasks one at a time, but continuously across a user-bounded batch (one task, a phase, or "until you need me"), instead of cold-reinvoking per task. For each task it assembles a build-ready brief from the full decision + risk + conventions context, then enforces the per-task status hygiene the rest of the pipeline depends on: flip to `in_progress` at start, and at completion fill `Date done` plus machine-resolvable `Evidence` anchors verified to resolve before they are written. Use to start building, get a brief for what to build next, work through a phase, or correctly close out a finished task.'
---
> Provider note (opencode): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Steps that write records shell out to `~/.treenail` scripts and need file-write permission; in non-interactive runs approval must be granted up front.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead.

This is the executor for the `[implementation]` seam — where `sequence-work`'s order stops being a plan and someone builds it. `sequence-work` produces the order (ephemeral, read-only); this skill *runs* it: pick the next eligible task → brief → build → land with verified evidence → continue to the next, staying in warm context across the batch rather than re-deriving scope on every task. It does not mint, supersede, triage, or promote — it implements already-planned tasks and records each one correctly.

Two things are non-negotiable per task, because they are what `reconcile-status` reads: the status transition and **verified** Evidence anchors. The continuous loop is the convenience; the per-task bookkeeping inside it is the correctness. Never let a fast batch skip the write-backs — that is exactly how drift detection rots.

1. **Scope + batch size.** Project- or feature-level, matching the `tasks/` you read. Establish up front **how much of the plan this run covers**, from the user's phrasing — one named `T-NNN`; a phase from `sequence-work`; "the next N"; or "work the plan until you need me." That bound is the loop's stop condition (step 8). Default, if unstated, to a single task and offer to continue.

2. **Pick the next eligible task.** From `tasks/INDEX.md`, the open set is `in_progress` then `todo` (in_progress first — already started). Exclude any task whose `Depends on` are not all `done`. Among the rest, honor an existing `sequence-work` phasing if the user has one in working notes; otherwise prefer tasks that unblock others or mitigate `high`/`critical` risks (read `risks/INDEX.md`), mirroring `sequence-work`'s risk-front-loading. State which task you picked and why before briefing it.

3. **Assemble the brief (read-only).** Load full bodies — the one time titles are not enough:
   - `tasks/T-NNN.md` — the Acceptance is the bar; any pre-seeded Evidence anchor is your target.
   - each `Implements: D-NNN` — **Decision and Rationale** tell you *what* to build and *why this way*; do not re-litigate a decided choice.
   - each `Mitigates: R-NNN` — **Description** is the failure mode you must not reintroduce; **Action** is the guard.
   - relevant `CONVENTIONS-SPEC.md` sections and any house conventions the codebase enforces.
   Resolve IDs against both `<artifact>/<ID>.md` and `<artifact>/archive/<ID>.md` (linked records may have been reaped). Then grep the codebase for the files/symbols the Acceptance and anchors name, so the brief points at real locations.

4. **Emit the brief.** A tight block to build against:
   - **Goal** — the task, declarative.
   - **Why** — the decision's rationale in one line (the load-bearing constraint).
   - **Guard** — the risk being mitigated and how *not* to reintroduce it (omit if the task only `Implements`).
   - **Acceptance** — verbatim from the task; the done bar, checkable against a diff.
   - **Target anchors** — the concrete `file:` / `grep:` / `symbol:<path>:<regex>` / `test:` the finished work should make resolve. If the task has none and its Acceptance names a concrete file/symbol/test, pre-seed the anticipated anchor now.
   - **Out of scope** — decided questions not to reopen, and adjacent work owned by other tasks.

5. **Start.** Flip the task `todo` → `in_progress` in `tasks/T-NNN.md` and update its `tasks/INDEX.md` status column. This skill is the designated writer of `in_progress` — the signal `reconcile-status` reads to derive a decision as `in_progress` rather than `not_started`. A trivially small task may go straight to `done` in step 7 (the spec allows skipping `in_progress`); a larger one flips here first so an interruption mid-build leaves correct state.

6. **Build to Acceptance.** Implement with the normal coding tools, scoped to this task's Acceptance — nothing more. If the work surfaces a **new decision** (a genuine choice the recorded ones don't cover), **stop the loop** and route to the `challenge-me` skill; do not invent a decision inside a task. A **new risk** → note it for the `red-team-me` or `triage-risks` skill and continue. The task implements the plan; it does not amend it.

7. **Land — the evidence hygiene the pipeline rests on.** When Acceptance is met:
   - Status → `done`; fill **Date done** (today, ISO). `done ⇔ non-empty Date done`.
   - Fill **Evidence** with machine-resolvable anchors (`file:<path>` / `grep:<regex>[ in <pathglob>]` / `symbol:<path>:<regex>` / `test:<id-or-path>`) for the code that landed, and **verify each resolves before writing it** — read-only `rg -l` / path check, exactly as `reconcile-status` will. Never write an anchor you have not just resolved: a non-resolving anchor manufactures the precise plan-vs-code drift the pipeline exists to catch, and prose or malformed anchors in `Evidence` on a `done` task are `audit-artifacts` Blockers. Human explanation goes in **Notes**, never `Evidence`.
   - Update the `tasks/INDEX.md` line (status + Date done). If you are minting several lines across a batch, you may instead run `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks` once at the end.
   - **Can't land?** Infeasible or redundant → Status `dropped`; fill **Date dropped** (today, ISO) and a **Notes** line saying why; update INDEX. Never silently leave it `in_progress`; a dropped task is evidence for the next `retrospective`. (Date dropped is the terminal date the INDEX projects and `archive-cycle` reads, so don't leave the drop date only in prose.)

8. **Loop or stop.** After landing, check the batch bound from step 1. **Continue** — return to step 2 for the next eligible task, in warm context — until any of these, then **stop and hand back**: the batch is exhausted; no eligible task remains (all open tasks blocked on unfinished deps); a new decision surfaced (step 6); an Evidence anchor would not resolve; or the user asked to go task-by-task. Report what you completed and what stopped you.

9. **Recommend next.** When the run ends, recommend the `reconcile-status` skill — it re-resolves the anchors you wrote and recomputes each implementing decision's view, closing the loop from code back to plan. Reaping the finished tasks is `archive-cycle`'s job on its normal cadence.

10. **Stay in lane + conventions.** Do not triage risks, mint or supersede decisions, promote, or re-order the whole task list (that is `sequence-work`). This skill writes only each task's Status, Date done, Evidence, Notes, and that task's INDEX line. Reference `docs/CONVENTIONS-SPEC.md` for the TASKS field order, the Evidence anchor grammar, and the INDEX line format.
