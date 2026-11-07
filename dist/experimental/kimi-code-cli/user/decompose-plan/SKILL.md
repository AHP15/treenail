---
name: decompose-plan
description: Break the hardened decisions and mitigation list into atomic, individually-shippable tasks with dependencies and rough sizing. Writes per-record T-NNN.md files and backfills task references into mitigate-risk Action fields. Use after triage-risks, before sequence-work.
---
> Provider note (Kimi Code CLI experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental kimi-code-cli`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Kimi Code CLI exposes configurable permission modes and rules; scripted write steps depend on the active Kimi permission settings.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Turn every accepted decision and every `mitigate` risk into atomic, shippable tasks.

**Reads:** `decisions/INDEX.md`, `risks/INDEX.md`, `tasks/` (active + archive); decision bodies only when nuance affects the split; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `tasks/T-NNN.md`, the `Action` field of `mitigate` risks, and INDEX files (via script).

## Steps

1. **Scope.** Same scope as the source decisions and risks — never cross.

2. **Coverage.** Every active `accepted` decision and every `mitigate` risk maps to ≥1 task. Settled decisions (in `decisions/archive/`) are already covered. A new task that `Implements` one moves it back to the active set on the next `archive-cycle`. If something produces none, say which: already built (existing `done` tasks cover it — `reconcile-status` will derive it as implemented), environmental, or a planning gap.

3. **Atomicity.** Split until every task:
   - has an Acceptance that is one sentence, checkable against a diff;
   - fits S (<1d), M (1-3d), or L (3-10d);
   - is independently shippable, or names the `Depends on` tasks that make it so.

   **Spikes** cover genuine unknowns: their Acceptance is a decision or an estimate, not code, and `Implements`/`Mitigates` points at what they unblock.

4. **Write each task.**
   - `python3 ~/.treenail/scripts/bootstrap.py <scope-dir> tasks` once.
   - `python3 ~/.treenail/scripts/mint_id.py <scope-dir>/tasks T` per task (it claims by creating the file, so sequential runs never collide).
   - Body per spec § TASKS: `Status: todo`, Size, `Implements` and/or `Mitigates`, `Depends on`, Acceptance, empty `Date done`/`Date dropped`. Leave `Evidence` empty, or pre-seed an anticipated anchor when the Acceptance names a concrete file/symbol/test.

5. **Backfill mitigations.** In each `mitigate` risk's `Action`, reference the T-NNN(s) that implement the guard.

6. **Project.** `python3 ~/.treenail/scripts/reindex.py <scope-dir> tasks risks` (this also projects the risks' `[tasks: …]` suffix).

7. **Report.** A flat list of minted IDs and titles, plus coverage gaps from step 2.

## Never

- Sequence, assign owners, or estimate calendar time — that's `sequence-work`.

## Next

- `audit-artifacts`, then `sequence-work`.
