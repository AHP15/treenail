---
name: triage-risks
description: Reconcile decisions with the risk list by assigning each pending risk a disposition (fix, mitigate, accept, defer) and updating decisions accordingly. Use after red-team-me, before implementation planning.
---

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
   - Mint the new decision: `python3 ~/.claude/skills/_shared/scripts/mint_id.py <scope-dir>/decisions D`. Write it per spec § DECISIONS with `Supersedes: D-NNN`.
   - On the old decision, set `Status: superseded`, `Date superseded: <today>`, and `Superseded by: D-MMM`. Don't touch its Context, Decision, or Rationale.
   - Set the risk's Action to "Superseded by D-MMM".
   - The new decision hasn't been examined. Recommend `red-team-me` on it before it ships.

5. **Re-triage** (risks flagged by `reconcile-status`). Edit in place; never supersede or delete.
   - **Mitigation complete:** if the shipped guard leaves an acceptable residual, change `mitigate` → `accept` with a rationale citing the tasks (this also lets the risk reap after the next retrospective). If not, leave it `mitigate` deliberately.
   - **Thin defer:** add a real trigger. If there is genuinely no future trigger, it was an `accept`; re-disposition it honestly.

6. **Project.** `python3 ~/.claude/skills/_shared/scripts/reindex.py <scope-dir> risks decisions`.

## Never

- Leave a risk `pending`, or write a `defer` without an observable trigger.
- Edit the body of a superseded decision, or delete a risk.

## Next

- `audit-artifacts`, then `decompose-plan`.
