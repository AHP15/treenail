---
name: audit-artifacts
description: Run structural invariant checks across decisions, risks, and tasks. Reports violations by severity; does not fix them. Run before any downstream skill (triage-risks, decompose-plan, sequence-work, reconcile-status, promote, archive-cycle) and before shipping planning work to reviewers.
---
> Provider note (opencode): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Steps that write records shell out to `~/.treenail` scripts and need file-write permission; in non-interactive runs approval must be granted up front.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead.

Verify structural invariants across decisions, risks, and tasks. Do not modify any file.

**Run the mechanical checker first, then layer judgment on top.** The
decidable invariants (steps 2-6 below, minus the smell/judgment calls)
are implemented in `~/.treenail/scripts/audit.py`, which reuses
`reindex.py`'s projection so its INDEX-consistency check is decided by
the exact code that rebuilds the index — no second, drifting
implementation. Start with:

```
python3 ~/.treenail/scripts/audit.py <scope-dir>
```

`<scope-dir>` is the docs root — `docs` or `docs/features/<feature>`. It
prints a BLOCKER/WARN/INFO report and exits non-zero if any BLOCKER
exists. Read that report, then do the **judgment-only** passes the
script intentionally leaves to you and folds into your final report:
- **defer-trigger quality** (step 4): is each `defer` Action's trigger
  actually observable (threshold/date/event), or vague hand-waving?
- **smells** (step 7 Warn): orphan tasks, uncovered decisions, silent
  reversals — these need task-status reasoning `reconcile-status` owns;
  cite it rather than re-deriving.
- **cross-scope promotion symmetry** (step 6): the script checks this
  when it can load both scopes (`--project <docs>` is explicit for feature
  scopes). If the project scope is unavailable, verify by hand.
- any record the script flags **malformed** but whose body you can see is
  semantically wrong in a way the schema can't encode.

If `python3` is unavailable, perform all of steps 2-7 by hand. The prose
below is the full specification the script implements plus the judgment
layer; it remains authoritative.

1. Scope. Project- or feature-level. Audit `decisions/`, `risks/`, `tasks/` INDEX.md and per-record files together. Cross-scope only via promotion links (step 6).

   Field-completeness (steps 3-5) applies to **active records only**.
   Archived records — whether reaped-uncompacted (full body) or compacted
   (`Summary` only) — are terminal and frozen: do not re-validate their
   fields every run. For archived records check only that their ID
   resolves and their links are symmetric (step 6). This is what keeps
   the audit bounded to in-flight work: because terminal records are
   reaped out of the active dir continuously, the full-body validation
   pass never grows with a cycle's accumulated done/superseded records.
   (A manually corrupted archived record is caught by the `reindex` skill and the
   step-6 link checks, not by a full re-scan.)

2. INDEX consistency. INDEX is a pure projection of the per-record
   files (see CONVENTIONS-SPEC.md "INDEX projection"), so this check is
   "does the projection match its source," not a judgment call. For each
   artifact:
   - Every line in `<artifact>/INDEX.md` corresponds to an existing per-record file directly in `<artifact>/`; every line in `<artifact>/archive/INDEX.md` corresponds to a file in `<artifact>/archive/`.
   - Every active per-record file has a line in the active index; every archived per-record file has a line in the archive index. A record must appear in exactly one of the two indexes — the one matching its location.
   - INDEX line fields match the record body (status, disposition, etc.).

   Any mismatch here is INDEX drift, and the **only** remedy is
   the `reindex` skill run on the scope — which recomputes the INDEX from the
   authoritative records. Never report "edit the INDEX line to match";
   the per-record files are the source of truth and the index is
   regenerated, not patched. (A field that is wrong in the *record body*
   is a different finding — that belongs under the artifact's own
   invariants below.)

   The script also runs this consistency pass over
   `retrospectives/INDEX.md`, and checks file-level invariants that
   `mint_id.py` normally guarantees but a manual edit can break: each
   record's **header ID matches its filename** (`## D-007:` lives in
   `D-007.md`), each filename is zero-padded (`D-001.md`, not `D-1.md`),
   and **no ID exists in both the active and archive dirs** (an ID is
   unique across the two). All are Blockers.

3. DECISIONS invariants:
   - IDs unique, no duplicates. Gaps are allowed (lost mint races — Info only, see step 7); never renumber to close one.
   - Every D-NNN.md has all required fields per CONVENTIONS-SPEC.md.
   - Status ∈ {`accepted`, `superseded`, `deprecated`, `promoted`}.
   - Every `superseded` has `Superseded by: D-NNN` pointing at an existing same-scope decision whose `Supersedes` points back.
   - No `superseded` without successor; no `deprecated` with successor.
   - Every `promoted` lives at feature scope, has `Promoted to: project:D-NNN`, no Supersedes/Superseded by. Project-level cannot be `promoted`.
   - Terminal decisions should carry `Date superseded`, `Date deprecated`, or `Date promoted` so `archive-cycle` can compact them after a retrospective.
   - No decision both superseded and promoted.
   - Dates ISO.

4. RISKS invariants:
   - IDs unique, no duplicates. Gaps are allowed (lost mint races — Info only, see step 7); never renumber to close one.
   - No `Disposition: pending` (blocker for downstream).
   - Every `defer` has Action with an observable trigger (threshold, date, event). "When it becomes a problem" is not a trigger.
   - Every `mitigate` Action that names a `T-NNN` must reference one that exists in tasks/ (active or archive); a named-but-missing task is a dangling ref (Blocker). A `mitigate` risk with a narrative Action and **no** task IDs yet is **expected before `decompose-plan` has run** — report it as Warn (a coverage gap that `decompose-plan` will close), not a Blocker. It only becomes a Blocker once `decompose-plan` has run for the scope and still left a mitigate risk taskless.
   - Every `fix` has Action referencing an existing decision supersession.
   - Every risk has ≥1 `Related decisions: D-NNN` whose ID exists.
   - `Promoted to` only at feature scope.

5. TASKS invariants:
   - IDs unique, no duplicates. Gaps are allowed (lost mint races — Info only, see step 7); never renumber to close one.
   - Every task has ≥1 of `Implements`/`Mitigates`; references resolve in same scope (active or archive).
   - `done` ⇔ non-empty `Date done`.
   - `Evidence` anchors, if present, are well-formed: each is a non-empty `file:`, `grep:`, `symbol:<path>:<regex>`, or `test:` anchor per CONVENTIONS-SPEC.md. Check shape only — whether an anchor *resolves* against the tree is `reconcile-status`'s job, not this skill's. A malformed anchor on a `done` task is a Blocker; on unfinished tasks it is a Warn. Empty `Evidence` on a `done` task is Info (coverage gap), not a violation.
   - Every `dropped` has a Notes line.
   - Every `Depends on: T-NNN` resolves; no cycles.
   - Size ∈ {S, M, L}.

6. Cross-artifact and cross-scope:
   - Every `Implements`/`Mitigates`/`Supersedes`/`Superseded by`/`Related decisions`/`Depends on` reference resolves to an existing ID in the correct file and scope.
   - Cross-scope promotion symmetric: feature D-NNN's `Promoted to: project:D-MMM` ↔ project D-MMM's `Promoted from: feature:<name>/D-NNN`. Same for risks. Asymmetric or dangling = Blocker.
   - For every `mitigate` risk, referenced tasks not all `dropped`. If they are, mitigation is notional only.

7. Output. Grouped report by severity:
   - **Blocker**: downstream will misbehave or corrupt (pending dispositions, dangling refs, missing required fields, dependency cycles, broken promotion links, INDEX/file mismatches). An empty or field-less per-record file — the residue of an ID claim (reservation protocol step 2) whose process died before the body was written — is a Blocker: it must be filled in or, if abandoned, given a minimal `dropped`/`deprecated` body. Never delete it (that would reopen the ID).
   - **Warn**: smells (orphan risks/tasks, uncovered decisions, silent reversals, all-dropped mitigations, `mitigate` risks not yet decomposed into tasks when `decompose-plan` has not run for the scope).
   - **Info**: cosmetic (date drift, field ordering). An ID gap (a missing N between two existing IDs) is Info, not a defect — it is the harmless trace of a lost mint race under the reservation protocol. Do not renumber to close it; renumbering breaks inbound links. A terminal record still sitting in the active dir (its line correctly in the active index) is also Info, not a defect — reap is asynchronous and on-cadence, so a record legitimately waits in the active set between going terminal and the next `archive-cycle` reap.

   Fixing is the owner's job, not this skill's.
