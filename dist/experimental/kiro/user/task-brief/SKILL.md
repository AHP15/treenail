---
name: task-brief
description: 'Drive implementation of the sequenced plan — work tasks one at a time, but continuously across a user-bounded batch (one task, a phase, or "until you need me"), instead of cold-reinvoking per task. For each task it assembles a build-ready brief from the full decision + risk + conventions context, then enforces the per-task status hygiene the rest of the pipeline depends on: flip to `in_progress` at start, and at completion fill `Date done` plus machine-resolvable `Evidence` anchors verified to resolve before they are written. Use to start building, get a brief for what to build next, work through a phase, or correctly close out a finished task.'
---
> Provider note (Kiro experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental kiro`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Kiro supports Agent Skills and configurable permissions; scripted write steps depend on the active Kiro permission settings.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Execute the plan task by task in warm context. Pick the next task, brief it, build it, land it with verified evidence, and continue. The loop is a convenience. The per-task write-backs are what correctness rests on, because `reconcile-status` reads them, so never skip them to go faster.

**Reads:** `tasks/`, the decisions and risks each task links to (active + archive), `risks/INDEX.md`, the codebase; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** code, plus each worked task's Status, `Date done` / `Date dropped`, Evidence, Notes, and its INDEX line (via script).

## Steps

1. **Scope and batch.** Settle how much this run covers from the user's phrasing: one `T-NNN`, a phase, "the next N", or "until you need me". The default is one task, then offer to continue.

2. **Pick.** The open set is `in_progress`, then `todo`, excluding tasks whose `Depends on` aren't all `done`. Follow the user's `sequence-work` phasing if they have one; otherwise prefer tasks that unblock others or mitigate `high`/`critical` risks. Say which task you picked and why.

3. **Brief.** Load the full bodies: the task (its Acceptance is the bar), each `Implements` decision (Decision and Rationale: what to build and why, which you don't re-litigate), and each `Mitigates` risk (Description is the failure not to reintroduce; Action is the guard). Grep the code for what the Acceptance names. Then emit:
   - **Goal** — the task, in one declarative line.
   - **Why** — the decision's load-bearing constraint.
   - **Guard** — the risk not to reintroduce (omit if the task only implements).
   - **Acceptance** — verbatim from the task.
   - **Target anchors** — the Evidence the finished work should make resolve; pre-seed them if the task has none.
   - **Out of scope** — settled questions and work that belongs to other tasks.

4. **Start.** Set the task to `Status: in_progress` and run `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks`, so an interrupted build leaves state that is correct and audit-clean. A trivially small task may jump straight to `done` at step 6.

5. **Build** to the Acceptance and nothing more. If the work exposes a **new decision**, stop the loop and route it to `challenge-me`; never decide inside a task. A **new risk**: note it for `red-team-me` and continue.

6. **Land.**
   - **Done:** set `Status: done` and `Date done: <today>`. Write Evidence anchors (spec § TASKS) for the code that landed, and **resolve each one (`rg -l` / path check) before writing it**. An unresolved or prose anchor on a done task is an `audit-artifacts` Blocker and fakes drift. Explanation goes in Notes.
   - **Can't land** (infeasible or redundant): set `Status: dropped`, `Date dropped: <today>`, and a Notes line saying why. Never leave a task stranded in `in_progress`.
   - Then run `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks`.

7. **Loop or stop.** Return to step 2 unless the batch is done, nothing is eligible, a new decision came up, an anchor wouldn't resolve, or the user wants to go task by task. Report what you completed and what stopped you.

## Never

- Triage, mint or supersede decisions, promote, or reorder the whole plan. This skill implements tasks already planned; it does not amend the plan.

## Next

- `reconcile-status`, to re-resolve the anchors you wrote and recompute each decision's status. Reaping is `archive-cycle`'s job.
