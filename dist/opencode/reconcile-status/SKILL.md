---
name: reconcile-status
description: Compute the implementation view for each accepted decision from current task statuses, and surface orphan tasks, uncovered decisions, silent reversals, stale mitigation coverage, and cross-record judgment smells (un-red-teamed decisions, thin high-severity defers, completed mitigations to re-triage). Read-only — implementation status is not stored. Run on cadence — every time tasks change state, and before any planning review.
---
> Provider note (opencode): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Steps that write records shell out to `~/.treenail` scripts and need file-write permission; in non-interactive runs approval must be granted up front.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Derive each accepted decision's implementation status from its tasks, check every `done` task's Evidence against the working tree, and route each anomaly to the skill that owns the fix. Implementation status is never stored; it is recomputed on every read.

**Reads:** `decisions/`, `risks/`, `tasks/` (active + archive) and the working tree.
**Writes:** nothing.

## Steps

1. **Scope.** Project or one feature; never cross. Run from the repo root, or pass `--root`.

2. **Mechanical view.** `python3 ~/.treenail/scripts/reconcile.py <scope-dir> [--root <repo-root>]`. Per accepted decision it prints the view:
   - **uncovered** — no tasks;
   - **reversed** — no live tasks (all dropped);
   - **implemented** — all live tasks done; **partial** if some tasks were dropped;
   - **not_started** — all live tasks todo;
   - **in_progress** — anything else.

   It also resolves every `done` task's Evidence anchors read-only (presence, never test runs), qualifies each implemented or partial decision as `(verified)`, `(UNVERIFIED: drift)` or `(unverified: no anchor)`, and lists ANOMALIES. It exits 1 if and only if drift was found, so it can gate CI. A decision with `Promoted from` derives its view from project-level tasks, and the script handles that.

3. **Smell pass.** `python3 ~/.treenail/scripts/reconcile_smells.py <scope-dir>` reports, advisory only:
   - **un-red-teamed** — an accepted decision no risk points at;
   - **thin defer** — a high or critical `defer` with no threshold or concrete event;
   - **mitigation complete** — every mitigating task of a `mitigate` risk is done.

4. **Route each finding.** Recommend; never fix.

   | Finding | Route |
   |---|---|
   | **Drift**: a `done` task's anchor no longer resolves | Moved code → repoint the anchor. Abolished → pin it as `git:<sha>:<anchor>` (spec § TASKS, anchor maintenance). Actually missing → reopen the task. |
   | **Silent reversal**: all implementing tasks dropped | `challenge-me`, to supersede or deprecate the decision |
   | **Uncovered**: no implementing tasks | Ask: already built, environmental, or a planning gap? → `decompose-plan` |
   | **Mitigation notional**: all mitigating tasks dropped | `triage-risks` |
   | **Un-red-teamed** | `red-team-me` |
   | **Thin defer** / **mitigation complete** | `triage-risks` |

## Never

- Modify any file, or mint, split, triage, supersede, or promote. Structural validity is `audit-artifacts`' job; this skill is about implementation reality.

## Next

- Whichever routing skill the findings point to.
