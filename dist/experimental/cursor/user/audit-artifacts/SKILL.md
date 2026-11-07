---
name: audit-artifacts
description: Run structural invariant checks across decisions, risks, and tasks. Reports violations by severity; does not fix them. Run before any downstream skill (triage-risks, decompose-plan, sequence-work, reconcile-status, promote, archive-cycle) and before shipping planning work to reviewers.
---
> Provider note (Cursor experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental cursor`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Cursor's exact live skill activation behavior remains experimental until a runtime parity pass is recorded.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.2.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.2.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Verify the structural invariants of a scope. The script decides everything mechanical; you add the judgment passes it deliberately leaves out, then report.

**Reads:** every record and INDEX in the scope (active + archive), and the project scope for promotion symmetry; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** nothing.

## Steps

1. **Scope.** Project (`docs`) or one feature (`docs/features/<name>`).

2. **Mechanical pass.** `python3 ~/.treenail/scripts/audit.py <scope-dir> [--project docs]`. It prints a BLOCKER / WARN / INFO report and exits 1 if any BLOCKER exists. It covers: INDEX ↔ record consistency (using `reindex.py`'s own projection), header-ID/filename/zero-padding, IDs duplicated across active and archive, empty claimed files, required fields, enum values, every link resolving (active or archive, same scope), supersession and promotion symmetry, bare IDs copied verbatim by `promote`, dependency cycles, Evidence anchor shape, and retrospective `Boundary-end`. Field completeness is checked on active records only — archived records are frozen, so only their links are checked.

3. **Judgment pass** — what the script cannot decide:
   - **Defer-trigger quality.** Is each `defer` Action's trigger observable (threshold, date, event)? "When it becomes a problem" is not a trigger → Warn.
   - **Decompose status.** The script guesses whether `decompose-plan` has run (any task mitigates a risk), which decides whether a taskless `mitigate` risk is a Warn or a Blocker. Correct the severity if you know better, e.g. a brownfield scope.
   - **Semantic wrongness.** A record that is well-formed but plainly wrong in a way the schema cannot encode.
   - **Implementation smells** (orphan tasks, uncovered decisions, silent reversals) belong to `reconcile-status` — cite it, don't re-derive.

4. **Report** grouped by severity:
   - **Blocker** — downstream will misbehave: pending dispositions, dangling refs, missing required fields, cycles, broken promotion links, INDEX drift, empty claimed files.
   - **Warn** — smells: thin defer triggers, undecomposed mitigations, all-dropped mitigations, verbatim-copied promotion links.
   - **Info** — harmless: ID gaps (lost mint races), terminal records awaiting reap, missing optional fields.

   Give each finding its remedy:
   - INDEX drift → always the `reindex` skill. Never hand-edit an INDEX line.
   - Empty claimed file → fill it in, or give it a minimal `dropped`/`deprecated` body. Never delete it — that reopens the ID.
   - ID gap → leave it. Never renumber.

## Never

- Modify any file. Fixing is the owner's job.

## Next

- Zero Blockers → the downstream skill that was waiting (`triage-risks`, `decompose-plan`, `sequence-work`, `promote`, `archive-cycle`).
