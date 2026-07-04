# Treenail — Planning Pipeline Guide (v2 — context-bounded)

**Treenail** is the name of this pipeline: the load-bearing spine every
project is built up from — decision records laid down first, append-only,
never removed, with every risk and task hanging off them for alignment.

Same pipeline as v1, but storage is partitioned so day-to-day skills
read O(active work) instead of O(all history). Solves the
forever-growing-DECISIONS.md problem without losing the durability
guarantees (ID-stable, append-only, never delete).

---

## What changed from v1

v1 stored each artifact as one append-only file (`DECISIONS.md`,
`RISKS.md`, `TASKS.md`). Forever-growing, forever-read.

v2 splits each artifact into:

- **INDEX.md** — one line per *active* record, partitioned to mirror the
  record dirs: `<artifact>/INDEX.md` for active records (the
  always-loaded "what's in flight" map) and `<artifact>/archive/INDEX.md`
  for archived records (loaded only by the deep skills). The active index
  never accumulates a line per terminal record, so it stays O(in-flight
  work), not O(all history).
- **Per-record files** — full body in `docs/<artifact>/<ID>.md`. Read on
  demand by ID.
- **archive/** — terminally-resolved records, moved out of the active
  read path body *and* INDEX line together (the line moves from
  `<artifact>/INDEX.md` to `<artifact>/archive/INDEX.md`). A reaped
  record keeps its full body until a retrospective harvests it, then
  `archive-cycle` compacts it to a 3-5 line summary. Read only by audit
  (cross-links), retrospective, reconcile, and promote — never on the
  day-to-day hot path.

A new skill, `archive-cycle`, has two decoupled jobs: it **reaps**
terminal records out of the active directory continuously (scripted path
moves with full prose kept — run on cadence so the active read path stays
bounded *within* a cycle, not just at its boundary), and it **compacts**
the bodies of records a retrospective has already harvested. The full
prose lives in git history.

The conventions template is also split: `CONVENTIONS-SPEC.md` (the
schema, ~150 lines, loaded by skills) and `CONVENTIONS-EXAMPLES.md`
(exemplars, loaded only when a human is tailoring).

---

## The artifact layout

```
/docs/
  CONVENTIONS-SPEC.md            # concise schema (always loaded by writers)
  CONVENTIONS-EXAMPLES.md        # exemplars (loaded only when tailoring)
  decisions/
    INDEX.md                     # active decisions (always loaded)
    D-001.md, D-002.md, ...      # active records
    archive/
      INDEX.md                   # archived decisions (loaded on demand)
      D-NNN.md                   # reaped (full body) or compacted (3-5 lines)
  risks/
    INDEX.md
    R-NNN.md ...
    archive/
      INDEX.md
      R-NNN.md ...
  tasks/
    INDEX.md
    T-NNN.md ...
    archive/
      INDEX.md
      T-NNN.md ...
  retrospectives/
    INDEX.md                     # cycle list
    YYYY-MM-DD.md
  features/
    <feature>/
      <same structure>
```

A record's ID is unique within scope across active and archive — moving
to archive does not change the ID. Skills that resolve a reference must
check both `<artifact>/<ID>.md` and `<artifact>/archive/<ID>.md`.

---

## INDEX.md format

One line per record, pipe-separated, sorted by ID. Each artifact has two
indexes with the **identical** line format: `<artifact>/INDEX.md` lists
the active records, `<artifact>/archive/INDEX.md` lists the archived
ones. A record's line lives in exactly one of them, matching where its
file sits — there is no `[archived]` marker on the line.

**decisions/INDEX.md** (active):
```
D-001 | accepted   | Use Postgres as primary datastore
D-019 | accepted   | OAuth2 PKCE for first-party clients
```

**decisions/archive/INDEX.md** (D-002 was reaped here when it went superseded):
```
D-002 | superseded | Session cookies (→ D-019)
```

**risks/INDEX.md**:
```
R-001 | mitigate | high   | Refresh token leakage from client storage [tasks: T-031,T-032]
R-004 | defer    | medium | Postgres write throughput at >300 tenants
```

**tasks/INDEX.md** (active — only the open task remains):
```
T-061 | todo    | M | D-023       | Hardware-attested client check         |
```

**tasks/archive/INDEX.md** (terminal tasks reaped here, same line format):
```
T-031 | done    | M | D-019,R-001 | Rotate refresh token on every use      | 2025-09-04
T-044 | dropped | L | R-001       | Per-device anomaly detection           | 2025-10-12
```

**retrospectives/INDEX.md**:
```
2025-10-01 | OAuth rollout phase
2026-02-14 | Mobile GA cycle
```

There is no `[archived]` flag: which index a line sits in *is* the
location signal. The body lives next to its index — `<artifact>/<ID>.md`
for active records, `<artifact>/archive/<ID>.md` for archived ones.

The index is the cheap-to-load summary. Full bodies load by ID. Per-record files are authoritative; INDEX is a derived cache that audit-artifacts cross-checks.

---

## Read patterns by skill

| Skill | Reads by default | Reads on demand |
|---|---|---|
| `extract-decisions` | the existing codebase (manifests, entrypoints, schema, boundaries) | decisions/INDEX.md to avoid re-recording covered areas |
| `challenge-me` | latest retrospective, decisions/INDEX.md | active D-NNN.md (rare) |
| `red-team-me` | decisions/INDEX.md + latest retro Watch-for | active D-NNN.md by ID |
| `triage-risks` | risks/INDEX.md, decisions/INDEX.md | full risk + linked decisions by ID |
| `decompose-plan` | decisions/INDEX.md, risks/INDEX.md | full record by ID |
| `sequence-work` | tasks/INDEX.md | full task by ID |
| `task-brief` | tasks/INDEX.md, risks/INDEX.md (eligibility) | the picked T-NNN.md + its Implements/Mitigates bodies + codebase grep |
| `reconcile-status` | tasks + decisions + risks INDEX (active + archive, for the smell pass) | `done` task bodies (for Evidence anchors) + working-tree grep/stat; record bodies for smells |
| `audit-artifacts` | active INDEX.md + active records | archive/INDEX.md + archived records on cross-link checks |
| `retrospective` | active + archive INDEX.md, archive-uncompacted bodies (this cycle's terminal records), latest retrospective | older archive for trend evidence |
| `promote` | full source + destination scope INDEX.md | — |
| `archive-cycle` | INDEX.md + active records (reap); archive-uncompacted (compact) | — |
| `reindex` | all per-record files in scope (active + archive) | — |
| `graph-sync` | all per-record files in scope (one-way projection to Graphiti) | — |

The active `<artifact>/INDEX.md` is bounded to in-flight work;
`archive/INDEX.md` is loaded only by the deep skills — `reconcile-status`
(for reaped `done` tasks), `retrospective`, and `audit`'s cross-link pass.

Day-to-day implementation: read INDEX.md to see what's open, then load
the specific T-NNN.md you're working on plus its linked D-NNN.md /
R-NNN.md. Never load all of TASKS.md just to find one task.

---

## The pipeline (unchanged)

```
(extract-decisions — brownfield ingress)
challenge-me → red-team-me → audit-artifacts → triage-risks →
  audit-artifacts → decompose-plan → sequence-work →
  task-brief [implementation] → reconcile-status → retrospective →
  archive-cycle
```

`audit-artifacts` and `reconcile-status` are gates, not phases — run
them any time you want to verify state. `promote` is on-demand for
feature → project transitions. `extract-decisions` is an alternate
ingress, not a phase: it seeds the records for a brownfield project from
existing code (the code-reading counterpart of `challenge-me`), after
which the normal pipeline runs. `task-brief` is the executor of the
`[implementation]` step — it drives `sequence-work`'s order one task at a
time across a user-bounded batch, assembling each task's brief and
writing back the status + verified Evidence that `reconcile-status`
reads; the build itself is still done with the normal coding tools. `archive-cycle` is also a gate, not a
phase: its **reap** runs on cadence (session start) to keep the active
set bounded; its **compact** half only does work once a retrospective
has harvested the records, so running it after a retrospective is what
collapses that cycle's bodies. Same skill, safe to run any time.

---

## Scenario A: starting a new project (empty folder)

1. **`/challenge-me` — project scope.** Confirms scope. Copies
   `_shared/conventions-spec.md` and `_shared/conventions-examples.md`
   to `docs/` on first run. Writes one `docs/decisions/D-NNN.md` per
   accepted decision plus `docs/decisions/INDEX.md`.

2. **`/red-team-me`.** Writes `docs/risks/R-NNN.md` files (Disposition:
   pending) plus `risks/INDEX.md`. No fixes proposed.

3. **`/audit-artifacts`.** Zero Blockers expected. Fix any before
   moving on.

4. **`/triage-risks`.** Assigns `fix` / `mitigate` / `accept` / `defer`
   to every risk. `fix` creates a new D-NNN.md superseding the old
   (old's Status flips to superseded, both INDEX lines update).
   `mitigate` writes a narrative Action; decompose-plan mints the
   T-NNN IDs.

5. **`/audit-artifacts` again.** No `pending` left; supersessions
   symmetric.

6. **`/decompose-plan`.** Writes `docs/tasks/T-NNN.md` files plus
   `tasks/INDEX.md`. Backfills task IDs into mitigate-risk Action
   fields.

7. **`/sequence-work`.** Phased plan, ephemeral.

8. **Implement (drive with `/task-brief`).** `task-brief` runs this loop
   for you over a user-bounded batch — picking the next eligible task,
   assembling its brief, and writing back the status + verified Evidence
   below — so the steps here are what it automates, and also the manual
   fallback. Pick a task → load its T-NNN.md + `Implements`
   D-NNN.md + `Mitigates` R-NNN.md. Flip Status to `in_progress` when
   you start (and update its INDEX line) — that is what makes a task
   visibly active rather than merely planned, and it is the signal
   `reconcile-status` reads to derive a decision as `in_progress`
   instead of `not_started`. Build. Then flip Status to `done`, fill
   Date done, and fill `Evidence` with the code anchor(s) that prove it
   landed. **Evidence must be machine-resolvable anchors, not prose** —
   each one of `file:<path>`, `grep:<regex>[ in <pathglob>]`,
   `symbol:<path>:<regex>`, or `test:<id-or-path>`, written as an inline
   code span (`` `file:src/foo.ts` ``). Prose like "see settle.ts decline
   path" is what `reconcile-status` *cannot* resolve, so `audit-artifacts`
   now treats prose or malformed anchors in Evidence on a `done` task as a
   **Blocker**, not a warning. Put the human explanation in `Notes` (or
   the compaction `Summary`), never in `Evidence`. Update tasks/INDEX.md.

9. **`/reconcile-status` — on cadence.** Reads tasks/INDEX.md and
   decisions/INDEX.md, prints the computed implementation view per
   accepted decision, and surfaces orphans, uncovered decisions, and
   silent reversals. For `done` tasks it also resolves their `Evidence`
   anchors against the working tree (read-only grep/stat) and flags
   **implementation drift** — a decision marked implemented whose code
   anchor no longer exists. This is the hook from plan back to code:
   "tasks done" no longer blindly means "decision implemented." Still
   read-only — implementation status is not stored.

10. **`/retrospective` — at phase boundary.** Writes a new
    `retrospectives/YYYY-MM-DD.md` plus INDEX line.

11. **`/archive-cycle`.** Reap runs on cadence throughout the cycle
    (e.g. session start), moving terminal records to archive/ with full
    bodies and moving each one's INDEX line from `<artifact>/INDEX.md` to
    `<artifact>/archive/INDEX.md`. Run again after this retrospective to
    additionally compact the bodies it just harvested.

---

## Scenario B: feature on an existing project

**Session start (every session):**

```
/archive-cycle (reap) → /audit-artifacts → /reconcile-status
```

Reaping first moves any newly-terminal records out of the active dir, so
audit and reconcile then read a set bounded to in-flight work. All three
default to INDEX-only reads otherwise — cheap. Load full records only
when investigating a specific violation.

**Brownfield project with no records yet?** If the codebase predates the
pipeline and has no `docs/` decisions/risks for the area you're touching,
seed them first with `/extract-decisions` — it reconstructs the
`accepted` decisions already embodied in the code, mints a `done` task
with verified Evidence anchors per built decision (so `reconcile-status`
sees them as `implemented (verified)`, not uncovered), and raises the
standing risks visible in the tree as `pending`. Then run
`/audit-artifacts` → `/reconcile-status` → `/triage-risks`, and use
`/challenge-me` for go-forward decisions from there.

**For a non-trivial feature:**

1. Create `/docs/features/<feature>/` with `decisions/`, `risks/`,
   `tasks/`, `retrospectives/` subfolders, each containing an empty
   `INDEX.md`.

2. **`/challenge-me` — feature scope.** Reads
   `docs/decisions/INDEX.md` (project) for constraint context — does
   not re-litigate. Reads feature-level retrospective if any. Writes
   `docs/features/<feature>/decisions/D-NNN.md`.

3. **`/red-team-me` (feature scope).** Writes
   `docs/features/<feature>/risks/R-NNN.md`.

4. **Pipeline as in Scenario A**, all feature-scoped.

5. **Implement.** Same loop.

6. **`/retrospective` (feature scope) when feature ships.**

7. **`/archive-cycle` (feature scope).**

**When to `/promote feature:<feature>/D-NNN`** (or R-NNN):

- Other features start adopting the same decision → promote the
  decision.
- A risk turns out to be structural (whole project, not just this
  feature) → promote the risk.

One record per invocation. Tasks don't migrate (cross-scope chain
resolves their links); new tasks target the project-level ID.

**When to skip the pipeline entirely:**

- One-line bug fixes
- Typos, renames, comment edits
- Pure refactors with no decision change

---

## Migration from v1

If you have existing monolithic `DECISIONS.md` / `RISKS.md` / `TASKS.md`:

1. Create the directory layout above (empty INDEX.md files in each).
2. For each record in the old file, create a per-ID file in the
   appropriate folder with the same body content. (Decisions: omit any
   `Implementation` field — it is now derived on demand by
   `/reconcile-status`, not stored.)
3. Add a one-line index entry per record.
4. Move records that are already in terminal states (`superseded`,
   `deprecated`, `promoted`, `done`, `dropped`) to `archive/` and run
   `/archive-cycle` to compact them. Leave `accept`/`fix`/`defer` risks
   in the active dir — they reap only after a retrospective review or
   user confirmation (see ARCHIVAL), not on migration.
5. Delete the old monolithic files.

Do this once, manually or with a one-off script. Migration is out of
scope for the skills.

---

## Edge cases

**Decision turns out wrong mid-cycle.** Re-run `/challenge-me` scoped
to that decision. New decision gets next D-NNN with `Supersedes:
D-NNN`; old's status flips to superseded and gets `Date superseded:
YYYY-MM-DD`. Old body is historical, do not edit.

**Risk's disposition no longer fits.** Edit disposition, date, and
rationale in place in R-NNN.md. Update INDEX line. No supersession —
the risk is durable, the disposition is current state.

**Task becomes infeasible or redundant.** Status → dropped, fill Date
dropped (the parseable terminal date the INDEX projects and compaction
reads), add Notes explaining why, update INDEX. Do not delete — dropped
tasks are evidence for the next retrospective.

**Feature cancelled.** Mark `accepted` decisions `deprecated` with
`Date deprecated: YYYY-MM-DD` (no successor); open tasks `dropped` with Notes. Still run
`/retrospective` — cancelled work is high-signal calibration.

**Concurrent minting.** Two sessions or branches minting an ID at the
same time cannot collide: the ID reservation protocol
(CONVENTIONS-SPEC.md) computes the next ID from the *files* (active +
archive, not the lagging INDEX) and claims it with an atomic
no-clobber create, retrying on collision. The loser of a race simply
takes the next number. A claim interrupted before its body is written
leaves an empty file that audit-artifacts flags; a resulting ID gap is
harmless and is never renumbered.

**INDEX drift.** INDEX is a pure deterministic projection of the
per-record files, so drift is repaired, not adjudicated. If INDEX.md
falls out of sync (manual edit, partial skill failure), audit-artifacts
catches it and the fix is always `/reindex <scope>`, which discards the
INDEX and recomputes it from the authoritative records. Never hand-edit
an INDEX line to "match" — there is nothing to decide, only to
recompute. `reindex` is idempotent: re-running on a clean tree is a
no-op.

**No CONVENTIONS-SPEC.md exists yet.** First skill that writes an
artifact copies `_shared/conventions-spec.md` and
`_shared/conventions-examples.md` to `docs/`. Edit the spec to tailor;
keep the schema intact.

---

## Cadence summary

| Trigger | Run |
|---|---|
| Session start (existing project) | `/archive-cycle` (reap) → `/audit-artifacts` → `/reconcile-status` |
| Batch of tasks changed state | `/archive-cycle` (reap) → `/reconcile-status` |
| Before any downstream planning skill | `/audit-artifacts` |
| Phase boundary, milestone, ≥3 done tasks | `/retrospective` |
| After every retrospective | `/archive-cycle` (now also compacts the harvested records) |
| audit-artifacts reports INDEX drift | `/reindex <scope>` |
| New cycle starts | `/challenge-me` (auto-reads latest retrospective Watch-for) |

---

## Optional: the Graphiti semantic layer

The pipeline above is complete and deterministic on its own. `graph-sync`
adds an **optional, derived, advisory** semantic index on top, for one
thing the file layout deliberately does not do: fuzzy, cross-scope recall
("have we decided/feared something like this before, in another feature?").
The explicit-link graph (`Supersedes`, `Implements`, `Mitigates`,
`Promoted to`, `Related decisions`) is exact but only connects records
someone hand-linked within a scope; Graphiti adds semantic adjacency
across scopes.

Non-negotiable boundaries that keep it from undermining the determinism
the rest of this guide buys:

- **One way.** Records → graph, never graph → records. Files + git stay
  the single source of truth. The graph is rebuildable from the files at
  any time (`graph-sync --rebuild`), exactly like INDEX is rebuildable by
  `reindex` — so an LLM mis-extraction is advisory noise, never
  corruption.
- **Advisory only.** Only the three judgment skills read it —
  `challenge-me`, `red-team-me`, `promote` — and only to *suggest* prior
  art the user weighs. `audit`, `reindex`, `decompose`, `sequence`,
  `reconcile`, `archive-cycle` never touch it and stay file-only.
- **Optional.** No backend configured ⇒ clean no-op everywhere. The
  retrieval hooks fall back to their original behaviour; nothing breaks.
- **It's a recall play, not a token play.** It *costs* extraction tokens
  on sync to *gain* cross-scope intelligence. The active-INDEX
  partitioning already solved the read-token problem; don't adopt the
  graph expecting it to save tokens.

Likely worth it once you have several features/projects and feel the
"have we done this before" pain. Below that scale it is probably premature.

## Why this layout fixes the bloat problem

- **Bounded reads.** A day-to-day skill loads the *active*
  `<artifact>/INDEX.md`, which is one line per *in-flight* record — not
  per record ever created. Terminal records' lines live in
  `<artifact>/archive/INDEX.md`, off the hot path, so the active index is
  O(in-flight work). The deep skills that genuinely need history
  (`reconcile-status` for reaped `done` tasks, `retrospective`, `audit`'s
  cross-link pass) opt into the archive index explicitly. Per-record
  bodies are read only when needed.
- **Active vs historical separation.** Resolved records — body *and*
  INDEX line — live under `archive/`, out of the day-to-day read path.
- **Continuously bounded active set.** Reaping is decoupled from the
  retrospective: a record whose terminal state is self-evident from its
  own fields (superseded/deprecated/promoted decisions, done/dropped
  tasks) leaves the active directory the moment it goes terminal, not at
  the next cycle boundary. So the active read path stays
  O(in-flight work) *within* a long cycle, not just across cycles —
  `audit-artifacts` and `reconcile-status` don't pay for a cycle's worth
  of accumulated done/superseded records. (Resolved *risks* —
  accept/fix/defer — are the deliberate exception: they stay active as
  standing concerns until a retrospective reviews them or the user
  confirms, so next cycle's challenge/red-team still see them. A
  `mitigate` risk has no reap path of its own *by design* — it is a
  permanent standing concern unless re-triaged. `reconcile-status` flags
  a `mitigate` whose tasks are all `done` as a re-triage candidate;
  `triage-risks` then moves it `mitigate → accept` if the residual is
  acceptable, after which it reaps like any accept. The risk never leaves
  the active set silently — only through an explicit judgment.)
  Compaction (the body collapse)
  still waits for the retrospective to harvest the prose; the two are
  separate events on `archive/`.
- **Conventions split.** Spec is concise (~150 lines); exemplars load
  only when tailoring. Skills don't pull 500+ lines on every write.
- **No write contention.** Per-record files mean two skills working
  on different records don't touch the same file.
- **Git diffs are local.** A status flip on T-031 changes T-031.md and
  one INDEX line — not a 5000-line monolithic TASKS.md.

The principle: **append-only is correct for durability, wrong for
context.** Solve it by separating durable record from working set.
