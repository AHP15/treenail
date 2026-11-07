---
name: triage-risks
description: Reconcile decisions with the risk list by assigning each pending risk a disposition (fix, mitigate, accept, defer) and updating decisions accordingly. Use after red-team-me, before implementation planning.
---
> Provider note (Codex CLI): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Give every `pending` risk a disposition and write it back, superseding decisions where a fix requires it. Also re-dispositions existing risks that `reconcile-status` flags.

**Reads:** `risks/INDEX.md`, `decisions/INDEX.md`, each risk body and its `Related decisions` bodies; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** risk Disposition / Date / Disposition rationale / Action; superseded and new decisions; INDEX files (via script).

## Steps

1. **Scope.** The same scope for `risks/` and `decisions/`.

2. **Pending set.** Every risk in `risks/INDEX.md` whose disposition is `pending`.

3. **Decide each one**, after loading the risk and its related decisions in full (you need the rationale). Weigh **Severity × Likelihood**:
   - high × high → address now (`fix` / `mitigate`);
   - high severity × low likelihood → `defer` with a real trigger, or `accept`;
   - low × low → usually `accept`.

   At equal severity, Likelihood breaks the tie.

   | Disposition | Meaning | Action field |
   |---|---|---|
   | `fix` | Change a decision so the failure mode disappears (step 4) | Link to the new decision |
   | `mitigate` | Keep the decision and add a guard | The guard, described narratively; `decompose-plan` mints the tasks |
   | `accept` | Live with it | Why the blast radius is acceptable, or "none" |
   | `defer` | Revisit later | **An observable trigger**: a threshold, date, or event. "When it becomes a problem" is not one. |

   Write Disposition, `Date: <today>`, Disposition rationale, and Action into the risk.

4. **Fix flow: supersede.**
   - Mint the new decision: `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/decisions D`. Write it per spec § DECISIONS with `Supersedes: D-NNN`.
   - On the old decision, set `Status: superseded`, `Date superseded: <today>`, and `Superseded by: D-MMM`. Don't touch its Context, Decision, or Rationale.
   - Set the risk's Action to "Superseded by D-MMM".
   - The new decision hasn't been examined. Recommend `red-team-me` on it before it ships.

5. **Re-triage** (risks flagged by `reconcile-status`). Edit in place; never supersede or delete.
   - **Mitigation complete:** if the shipped guard leaves an acceptable residual, change `mitigate` → `accept` with a rationale citing the tasks (this also lets the risk reap after the next retrospective). If not, leave it `mitigate` deliberately.
   - **Thin defer:** add a real trigger. If there is genuinely no future trigger, it was an `accept`; re-disposition it honestly.

6. **Project.** `python3 ~/.treenail/scripts/reindex.py <scope-dir> risks decisions`.

## Never

- Leave a risk `pending`, or write a `defer` without an observable trigger.
- Edit the body of a superseded decision, or delete a risk.

## Next

- `audit-artifacts`, then `decompose-plan`.
