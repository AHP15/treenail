---
name: audit-artifacts
description: Run structural invariant checks across decisions, risks, and tasks. Reports violations by severity; does not fix them. Run before any downstream skill (triage-risks, decompose-plan, sequence-work, reconcile-status, promote, archive-cycle) and before shipping planning work to reviewers.
---

Verify the structural invariants of a scope. The script decides everything mechanical; you add the judgment passes it deliberately leaves out, then report.

**Reads:** every record and INDEX in the scope (active + archive), and the project scope for promotion symmetry; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** nothing.

## Steps

1. **Scope.** Project (`docs`) or one feature (`docs/features/<name>`).

2. **Mechanical pass.** `python3 ~/.claude/skills/_shared/scripts/audit.py <scope-dir> [--project docs]`. It prints a BLOCKER / WARN / INFO report and exits 1 if any BLOCKER exists. It covers: INDEX ↔ record consistency (using `reindex.py`'s own projection), header-ID/filename/zero-padding, IDs duplicated across active and archive, empty claimed files, required fields, enum values, every link resolving (active or archive, same scope), supersession and promotion symmetry, bare IDs copied verbatim by `promote`, dependency cycles, Evidence anchor shape, and retrospective `Boundary-end`. Field completeness is checked on active records only — archived records are frozen, so only their links are checked.

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
