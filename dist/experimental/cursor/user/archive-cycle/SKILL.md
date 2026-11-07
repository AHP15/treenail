---
name: archive-cycle
description: Keep the active per-record set bounded to in-flight work. Reaps terminal decisions, risks, and tasks out of the active directory into archive/ with full prose kept — run this on cadence, e.g. session start. Also compacts archived records the latest retrospective has already consumed into 3-5 line summaries. Idempotent and safe to run any time. Never changes status, dispositions, or supersession links.
---
> Provider note (Cursor experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental cursor`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Cursor's exact live skill activation behavior remains experimental until a runtime parity pass is recorded.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Two decoupled, idempotent operations (spec § ARCHIVAL): **reap** moves terminal records out of the active dir so the hot read path stays bounded; **compact** shrinks archived records a retrospective has already harvested.

**Reads:** `decisions/`, `risks/`, `tasks/` (active + archive), latest `retrospectives/*.md`; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** record file *locations* and compacted bodies; `Date resolved` on confirmed `fix`/`defer` risks; INDEX files (via script).

## Steps

1. **Scope.** Project (`docs`) or one feature (`docs/features/<name>`). Never cross scopes.

2. **Reap — dry run.** `python3 ~/.treenail/scripts/archive_cycle.py <scope-dir> --dry-run`. The script decides eligibility:
   - decisions `superseded` / `deprecated` / `promoted`, and tasks `done` / `dropped` → reap;
   - `accept` risks → reap once their `Date` ≤ the latest retrospective's `Boundary-end`;
   - `fix` / `defer` risks → **never** without explicit confirmation. A `fix` is spent only when its superseding decision is *implemented* (derived, not stored — cite the `reconcile-status` skill); a `defer` only when its trigger passed without firing. Both are judgments.

3. **Confirm.** For every `skip` line (`fix`/`defer` awaiting confirmation, `accept` awaiting a boundary), ask the user which are spent. Then run for real: `python3 ~/.treenail/scripts/archive_cycle.py <scope-dir> [--confirm-risk R-NNN,R-MMM]`. It moves files with full prose, fills `Date resolved` on confirmed `fix`/`defer` risks, and rebuilds the affected indexes.

4. **Compact — select.** `python3 ~/.treenail/scripts/compact-select.py <scope-dir>`. If it exits 1 (**NO BOUNDARY**), skip compaction entirely — prose must never collapse before a retrospective has read it. Otherwise it lists `COMPACT` / `hold` / `SKIP` per record (`SKIP` = no parseable terminal date: report it as a record to fix).

5. **Compact — rewrite.** For each `COMPACT` record, replace the body (keep the `## <ID>: <Title>` header) with only:
   - terminal Status / Disposition (unchanged);
   - projection-required fields, verbatim: **Size** (tasks), **Severity** and **Likelihood** (risks);
   - its terminal date fields and **Date archived** (today);
   - key links: `Supersedes` / `Superseded by` / `Promoted to` / `Promoted from` / `Implements` / `Mitigates` / `Action` / `Evidence` (keep `Evidence` so archived done tasks stay drift-checkable);
   - **Summary**: 1-2 sentences condensing the prose. ≤5 meaningful lines total; full prose stays in git history.

   Compaction does not touch any INDEX line.

6. **Report** per artifact: IDs reaped, IDs compacted, and what was skipped awaiting confirmation or a boundary. A no-op run is the normal steady state — say so.

## Never

- Change Status, Disposition, or supersession links — archival is never a state transition. The only field reap adds is `Date resolved`, and only on confirmed `fix`/`defer` risks.
- Reap a `fix`/`defer` risk the user has not confirmed.

## Next

- `audit-artifacts` to confirm cross-references still resolve (IDs resolve against active and `archive/`).
