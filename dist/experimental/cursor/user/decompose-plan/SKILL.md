---
name: decompose-plan
description: Break the hardened decisions and mitigation list into atomic, individually-shippable tasks with dependencies and rough sizing. Writes per-record T-NNN.md files and backfills task references into mitigate-risk Action fields. Use after triage-risks, before sequence-work.
---
> Provider note (Cursor experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental cursor`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Cursor's exact live skill activation behavior remains experimental until a runtime parity pass is recorded.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Load `decisions/INDEX.md` and `risks/INDEX.md`. Produce tasks per accepted decision and per mitigate risk. Write per-record files; update indices.

1. Coverage pass. Every `accepted` decision (read INDEX status) and every `mitigate` risk maps to ≥1 task. If something doesn't produce a task, say so explicitly — it's already built (covered by existing `done` tasks; the `reconcile-status` skill will derive the decision as implemented — implementation is never a stored Status), environmental, or a planning gap.

2. Atomicity. Each task must:
   - Acceptance fits in one sentence and is checkable against a diff.
   - Size fits S (<1d), M (1-3d), or L (3-10d).
   - Independently shippable, or explicitly depends on specific other tasks that make it so.
   Split until every leaf passes.

3. Load full bodies only when needed. Most decision titles in INDEX are enough to know what tasks are required — load D-NNN.md only when nuance affects the split.

4. For each task:
   - Mint the next T-NNN by running `python3 ~/.treenail/scripts/mint_id.py <tasks-dir> T` (e.g. `docs/tasks` or `docs/features/<feature>/tasks`). The script executes the **ID reservation protocol** — filesystem-arbitrated max over active + archive, atomic no-clobber claim, retry on collision (not from INDEX, which may lag) — and prints the claimed `T-NNN` and its file path. Because it claims by creating the file, running it once per task in this run automatically counts each just-claimed file in the next candidate; no manual bookkeeping. IDs are immutable once claimed. (Fall back to the protocol by hand if `python3` is unavailable.)
   - Write the body into the claimed `tasks/T-NNN.md` per the TASKS section of CONVENTIONS-SPEC.md: Title, Status `todo`, Size, Implements/Mitigates, Depends on (optional), Acceptance, Evidence (empty — filled when the task is marked `done`; if the Acceptance already names a concrete target file/symbol/test you may pre-seed a well-formed anticipated anchor such as `grep:<regex> in <pathglob>` or `symbol:<path>:<regex>`), Date done (empty), Date dropped (empty), Notes (optional).
   - Add its INDEX line: append `T-NNN | todo | <size> | <implements/mitigates> | <title> |`, or — preferred when you wrote several tasks — after writing all bodies run `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks` to project the whole tasks index at once.

5. Backfill mitigations. For every risk with `Disposition: mitigate`:
   - Update `risks/R-NNN.md` Action field to reference the T-NNN(s) that mitigate it.
   - Update `risks/INDEX.md` line: append `[tasks: T-NNN,T-MMM,...]`.

6. Spike tasks for unknowns, not hidden risk. A spike's Acceptance is a decision or estimate, not shipped code. Same task format. `Implements`/`Mitigates` points at the decision or risk it unblocks.

7. Same scope as source decisions/risks. Project-level tasks for project-level decisions; feature-level for feature.

8. Conventions. Reference `docs/CONVENTIONS-SPEC.md`. If missing, copy [~/.treenail/conventions-spec.md](~/.treenail/conventions-spec.md) and [~/.treenail/conventions-examples.md](~/.treenail/conventions-examples.md) to `docs/`.

9. Output. Flat list of minted task IDs and titles, plus any coverage gaps from step 1. Do not sequence, do not assign owners, do not estimate calendar time. That's `sequence-work`'s job.
