---
name: decompose-plan
description: Break the hardened decisions and mitigation list into atomic, individually-shippable tasks with dependencies and rough sizing. Writes per-record T-NNN.md files and backfills task references into mitigate-risk Action fields. Use after triage-risks, before sequence-work.
---

Turn every accepted decision and every `mitigate` risk into atomic, shippable tasks.

**Reads:** `decisions/INDEX.md`, `risks/INDEX.md`, `tasks/` (active + archive); decision bodies only when nuance affects the split; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `tasks/T-NNN.md`, the `Action` field of `mitigate` risks, and INDEX files (via script).

## Steps

1. **Scope.** Same scope as the source decisions and risks — never cross.

2. **Coverage.** Every `accepted` decision and every `mitigate` risk maps to ≥1 task. If something produces none, say which: already built (existing `done` tasks cover it — `reconcile-status` will derive it as implemented), environmental, or a planning gap.

3. **Atomicity.** Split until every task:
   - has an Acceptance that is one sentence, checkable against a diff;
   - fits S (<1d), M (1-3d), or L (3-10d);
   - is independently shippable, or names the `Depends on` tasks that make it so.

   **Spikes** cover genuine unknowns: their Acceptance is a decision or an estimate, not code, and `Implements`/`Mitigates` points at what they unblock.

4. **Write each task.**
   - `python3 ~/.claude/skills/_shared/scripts/bootstrap.py <scope-dir> tasks` once.
   - `python3 ~/.claude/skills/_shared/scripts/mint_id.py <scope-dir>/tasks T` per task (it claims by creating the file, so sequential runs never collide).
   - Body per spec § TASKS: `Status: todo`, Size, `Implements` and/or `Mitigates`, `Depends on`, Acceptance, empty `Date done`/`Date dropped`. Leave `Evidence` empty, or pre-seed an anticipated anchor when the Acceptance names a concrete file/symbol/test.

5. **Backfill mitigations.** In each `mitigate` risk's `Action`, reference the T-NNN(s) that implement the guard.

6. **Project.** `python3 ~/.claude/skills/_shared/scripts/reindex.py <scope-dir> tasks risks` (this also projects the risks' `[tasks: …]` suffix).

7. **Report.** A flat list of minted IDs and titles, plus coverage gaps from step 2.

## Never

- Sequence, assign owners, or estimate calendar time — that's `sequence-work`.

## Next

- `audit-artifacts`, then `sequence-work`.
