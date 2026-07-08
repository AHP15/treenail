---
name: reconcile-status
description: Compute the implementation view for each accepted decision from current task statuses, and surface orphan tasks, uncovered decisions, silent reversals, stale mitigation coverage, and cross-record judgment smells (un-red-teamed decisions, thin high-severity defers, completed mitigations to re-triage). Read-only — implementation status is not stored. Run on cadence — every time tasks change state, and before any planning review.
---
> Provider note (Codex CLI): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

Compute the implementation view per accepted decision and resolve each
`done` task's Evidence anchors against the working tree, then report. This
skill writes nothing. Implementation is not a stored field — it is derived
on every read.

**Run the mechanical reconcile first, then layer judgment on top** — the
same split as `audit-artifacts`. The view derivation and anchor resolution
are purely mechanical and are the pipeline's highest-signal output
(plan↔code drift), so they live in a script (`reconcile.py`) rather than
in prose, where a model could "believe" an anchor resolves without
searching and two runs could disagree.

1. Scope. Match `decisions/` and `tasks/` scope (project- or
   feature-level). Never cross. For decisions with `Promoted from`, the
   view derives from project-level tasks (the script handles this and tags
   an uncovered promoted-from decision as expected).

2. Run the mechanical pass:

   ```
   python3 ~/.treenail/scripts/reconcile.py <scope-dir> [--root <repo-root>]
   ```

   `<scope-dir>` is the docs root (`docs` or `docs/features/<feature>`).
   `--root` is the repo root that Evidence paths are relative to (default:
   the current directory — run the skill from the repo root). It unions
   `tasks/` active **and** archive (because `done` tasks are reaped
   continuously), groups tasks by `Implements`, prints the view per
   accepted decision grouped by value, and for every `done` task resolves
   its `Evidence` anchors **read-only** (ripgrep with a pure-Python
   fallback; `file:`→path exists, `grep:`→pattern found, `symbol:`→regex
   found within its file, `test:`→file/identifier present — presence only,
   it never runs tests or builds). It qualifies each `implemented`/`partial` decision as
   `(verified)`, `(UNVERIFIED: drift)`, or `(unverified: no anchor)`, then
   prints an ANOMALIES section. It exits **1 iff implementation drift was
   found** (CI-gateable), else 0; it modifies nothing.

   The view rule it implements (for reference and the hand fallback): split
   a decision's implementing tasks into `dropped` (no longer live coverage)
   and `live` (todo/in_progress/done), then first match wins — no tasks →
   **uncovered**; no live tasks → **reversed**; all live `done` →
   **implemented** (or **partial** if some were dropped); all live `todo` →
   **not_started**; otherwise → **in_progress**.

3. Run the judgment-smell pass (the quality half):

   ```
   python3 ~/.treenail/scripts/reconcile_smells.py <scope-dir>
   ```

   It unions active + archive and reports three advisory smells —
   **un-red-teamed decision** (an `accepted` decision no risk points at),
   **thin defer** (a high/critical `defer` with neither a measurable
   threshold nor a concrete event trigger), and **mitigation complete** (a
   `mitigate` risk whose every mitigating task is `done`). These are the
   missing symmetric halves of checks the pipeline already does the
   failure-half of; they are surfaced to adjudicate, never auto-fixed.

4. Layer judgment on the two reports. For each finding, interpret and
   recommend the routing skill — never auto-fix:
   - **Implementation drift** (the highest-signal anomaly): a `done` task
     whose Evidence anchor no longer resolves — the plan claims the decision
     is implemented but the code says otherwise. Recommend re-opening the
     task (`done` → `todo`/`in_progress`) or updating its Evidence if the
     code merely moved.
   - **Silent reversal**: an `accepted` decision whose implementing tasks
     all `dropped` → it likely wants `superseded`/`deprecated` via
     the `challenge-me` skill.
   - **Uncovered**: an `accepted` decision with zero implementing tasks —
     already built? environmental? planning gap?
   - **Orphan task**: no `Implements` and no `Mitigates`.
   - **Mitigation notional**: a `mitigate` risk whose tasks are all dropped
     — no longer mitigated in practice though the disposition still claims
     it is. Re-triage via the `triage-risks` skill.
   - **Smells**: route un-red-teamed → the `red-team-me` skill, thin defer and
     mitigation-complete → the `triage-risks` skill, as the smell pass prints.

5. Hand fallback (no `python3`). Build the map yourself: read both
   `tasks/INDEX.md` and `tasks/archive/INDEX.md`, union, group by
   `Implements`; from `decisions/INDEX.md` list every `accepted` decision.
   Apply the step-2 view rule. For each `done` task contributing to an
   `implemented`/`partial` decision, load its body (resolve the ID against
   `tasks/<ID>.md` and `tasks/archive/<ID>.md`) and resolve each `Evidence`
   anchor read-only with `rg -l` / a path check. Then surface the same
   anomalies and smells.

6. Do not modify any file. Do not mint, split, or rewrite tasks. Do not
   triage risks. Do not create, supersede, or promote decisions. Structural
   validity is `audit-artifacts`' job; this skill is implementation reality.

7. Conventions. Reference `docs/CONVENTIONS-SPEC.md`. If missing, copy
   [~/.treenail/conventions-spec.md](~/.treenail/conventions-spec.md) and
   [~/.treenail/conventions-examples.md](~/.treenail/conventions-examples.md)
   to `docs/`.
