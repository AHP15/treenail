---
name: parallel-work
description: 'Build the task list in parallel waves instead of one task at a time. Picks the largest set of open tasks that are safe to build together (dependencies done, no shared decision, no overlapping code footprint), builds each in its own isolated git worktree via a parallel subagent, merges them one by one behind the test suite, re-verifies every Evidence anchor, then pauses for review before the next wave. Wave size defaults to 5 and is set per run with --max. Use when the user wants to implement many tasks faster, work a phase in parallel, or says "parallel-work". Falls back to building the same waves sequentially on agents without subagents.'
---
> Provider note (Kiro experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental kiro`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Kiro supports Agent Skills and configurable permissions; scripted write steps depend on the active Kiro permission settings.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.2.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.2.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

The parallel counterpart of `task-brief`. Each wave builds up to `--max` tasks at once, each in its own git worktree, then merges them behind the tests. Per-task correctness (brief, build to Acceptance, verified Evidence) is still `task-brief`'s procedure; this skill only orchestrates. Parallel is faster in elapsed time but costs more tokens than sequential, because every worker starts with a fresh context.

**Reads:** `tasks/`, `risks/`, the decisions and risks each wave task links to, and the codebase; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** code (via merged worker branches), each wave task's Status / `Date done` / `Date dropped` / Evidence / Notes, INDEX files (via script), and git commits.

## Steps

1. **Bounds.** From the user's phrasing, settle:
   - `--max N`, the wave size (default **5**);
   - optional `--only T-…,T-…` to work one phase or list;
   - how many waves to run.

   **Pause for review after every wave** unless the user explicitly says not to.

2. **Preconditions.** Stop and say why if any of these fails:
   - the scope's tasks are audit-clean (run `audit-artifacts` if unsure);
   - git has a clean working tree on a non-default branch (offer to create one);
   - you know the project's test command (find it in the repo or ask).

   If this agent cannot run subagents in isolated worktrees, use **sequential fallback**: run the same waves, building each task in this session per `task-brief` steps 3-6. The results are the same, just slower.

3. **Pick the wave.** `python3 ~/.treenail/scripts/waves.py <scope-dir> --max N [--only …]`. It prints:
   - `WAVE`: the tasks to build now;
   - `DEFERRED`: each with its reason (a conflicting task, a full wave, or unscoped);
   - `BLOCKED`: tasks waiting on dependencies.

   Exit 1 means nothing is eligible: stop and report the blocked set. Show the user the wave before starting it. A task the script calls *unscoped* has no target anchors, so its edits can't be predicted and it runs alone. Suggest pre-seeding its anchors if many tasks show up unscoped.

4. **Brief and start.** For each wave task, assemble the brief per `task-brief` step 3. Set every wave task to `Status: in_progress`, run `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks`, and **commit**. Workers branch from this commit, so the status flips can't conflict with their work.

5. **Launch the workers all at once.** Spawn one subagent per wave task in a single step, each in its own isolated git worktree (on Claude Code, the Agent tool with worktree isolation). Give each worker:
   - its brief, verbatim;
   - "Implement exactly T-NNN, following `task-brief` steps 5-6 in **worker mode**: build to the Acceptance; on landing, write only `tasks/T-NNN.md` (Status, `Date done` or `Date dropped`, verified Evidence, Notes); don't run `reindex.py` or edit any other record; run the tests; commit on your branch.";
   - "If the work needs a decision the records don't cover, stop without landing and report it. Note any new risk in your report.";
   - "Report: landed / dropped / stopped-for-decision, your branch name, files changed, the Evidence anchors written, and the test result."

6. **Merge one by one**, in wave order, onto the working branch:
   - **Stopped for a decision**, or tests failing in the worktree: don't merge. Set the task back to `todo` with a Notes line, and keep the decision for step 9.
   - **Merge conflict**: abort the merge. Set the task back to `todo` with Notes "re-queued: merge conflict in wave N". It returns in a later wave.
   - **Tests fail after the merge**: undo that merge commit (e.g. `git reset --merge ORIG_HEAD`; it's the commit you just made). Re-queue the task the same way.
   - Otherwise keep the merge and run the next one.

7. **Verify the wave.**
   - Run `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks`.
   - Run `python3 ~/.treenail/scripts/reconcile.py <scope-dir>`. An anchor that resolved in a worktree but not after the merge is drift: reopen that task (`todo`, with Notes) rather than leave a false `done`.
   - Commit "Land wave N: T-…".
   - Remove the merged worktrees and branches. Keep the unmerged ones until the user has seen them.

8. **Pause.** Report the wave:
   - landed, with each task's Evidence;
   - re-queued, with the reason;
   - dropped, with the reason;
   - decisions and risks the workers surfaced;
   - what the next wave would be (re-run `waves.py`; it's read-only, so this starts nothing).

   Wait for the user's go-ahead, unless they waived pausing. Then return to step 3.

9. **Stop** when the wave bound is reached, nothing is eligible, or any worker surfaced a new decision. Route the decision to `challenge-me` before continuing; never decide it inside the wave.

## Never

- Start more than `--max` workers, or put two tasks in one wave that `waves.py` deferred.
- Let a worker write INDEX files or any record other than its own task.
- Keep a merge whose tests fail, or record `done` for a task whose anchors don't resolve after the merge.
- Skip the pause between waves unless the user said to.

## Next

- `reconcile-status` once the run ends; `archive-cycle` on its normal cadence to reap the landed tasks.
