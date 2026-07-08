---
name: archive-cycle
description: Keep the active per-record set bounded to in-flight work. Reaps terminal decisions, risks, and tasks out of the active directory into archive/ with full prose kept — run this on cadence, e.g. session start. Also compacts archived records the latest retrospective has already consumed into 3-5 line summaries. Idempotent and safe to run any time. Never changes status, dispositions, or supersession links.
---
> Provider note (opencode): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Steps that write records shell out to `~/.treenail` scripts and need file-write permission; in non-interactive runs approval must be granted up front.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

Two decoupled operations, both safe to run any time (idempotent). The
**reap** keeps the active read path bounded *within* a cycle; the
**compact** shrinks records a retrospective has already harvested. See
the ARCHIVAL section of CONVENTIONS-SPEC.md.

1. Scope. Project- or feature-level. Process `decisions/`, `risks/`,
   `tasks/` for the chosen scope. Do not cross scopes.

## Step 1 — Reap (run on cadence; keeps the active set bounded)

2. Find terminal records in the **active** directory:
   - **Decision**: Status ∈ {`superseded`, `deprecated`, `promoted`}.
   - **Risk**: no disposition reaps purely on its own state — an
     accepted, fixed, or deferred risk is still a standing concern that
     `challenge-me`/`red-team-me` (which read only the active INDEX)
     should keep seeing until it has been reviewed. So:
     - `accept` reaps once a **retrospective has reviewed it** — its
       `Date` is at or before the latest retrospective's `Boundary-end`
       (the same frontier `compact-select.py` reports; read it from the
       latest `retrospectives/*.md`) — or on explicit user confirmation.
       An accepted risk newer than the last retro stays active; it is live
       calibration signal the next cycle still wants.
     - `fix` and `defer` reap **only after user confirmation** — their
       eligibility turns on state the record does not carry. A `fix` is
       spent only once its superseding decision is actually *implemented*,
       and implementation status is **not stored** (it is derived by
       `reconcile-status`), so do not infer it from the record — optionally
       run/cite the `reconcile-status` skill for the fixing decision, then confirm.
       A `defer` is spent only once its trigger has passed without firing,
       which is a judgment.
     List every accept/fix/defer that is eligible-but-unconfirmed and
     confirm before reaping (accepts already past a retro boundary may be
     reaped without re-asking).
   - **Task**: Status ∈ {`done`, `dropped`}. No date gate.

3. Run the mechanical reap:

   ```
   python3 ~/.treenail/scripts/archive_cycle.py <scope-dir> --dry-run
   python3 ~/.treenail/scripts/archive_cycle.py <scope-dir> [--confirm-risk R-NNN,R-MMM]
   ```

   The script moves each eligible `<artifact>/<ID>.md` →
   `<artifact>/archive/<ID>.md` with full body retained, then rebuilds the
   affected active and archive indexes from the per-record files. Use
   `--confirm-risk` only for `fix`/`defer` risks the user explicitly
   confirmed are spent; the script fills `Date resolved` on those risks
   before moving them so compaction has a truthful terminal date.

## Step 2 — Compact (run at cycle boundary; shrinks consumed records)

4. Determine the eligible set deterministically:

   ```
   python3 ~/.treenail/scripts/compact-select.py <scope-dir>
   ```

   It finds the consumption frontier — the latest retrospective's
   machine-readable `Boundary-end` (never fuzzy `Cycle` prose) — and
   prints, per artifact, the uncompacted archive records eligible to
   compact (`COMPACT`), those still too new (`hold`), and those it had to
   `SKIP` (no parseable terminal date). **If it exits non-zero with NO
   BOUNDARY** — no retrospective carries a parseable `Boundary-end` — then
   skip compaction entirely: reaped records stay uncompacted in `archive/`
   (already off the hot path) until a retrospective harvests them. This
   fail-safe is what guarantees prose is never collapsed before a
   retrospective could read it. (Hand fallback if `python3` is
   unavailable: read the latest retro's `Boundary-end` field yourself and
   apply the same date test.)

5. For each record the selector marked **COMPACT** (an uncompacted
   `archive/` record — full body, no `Summary` — whose terminal date is
   at or before the frontier), compact in place — replace the body with
   these fields:
   - ID
   - Title
   - Terminal Status / Disposition (unchanged)
   - **Projection-required fields**, kept verbatim so the compacted record
     still yields a complete INDEX line and `reindex` does not flag it
     malformed: **Size** (tasks) and **Severity** (risks) — both appear in
     their artifact's INDEX line. Keep **Likelihood** on risks too.
     (Decisions need only Status, already above.)
   - Date / Date superseded / Date deprecated / Date promoted /
     Date resolved / Date done / Date dropped (unchanged)
   - **Date archived**: today, YYYY-MM-DD
   - Key links: `Superseded by` / `Supersedes` / `Promoted to` /
     `Promoted from` / `Implements` / `Mitigates` / `Action` /
     `Evidence` as applicable (preserve `Evidence` so `reconcile-status`
     can still drift-check archived `done` tasks)
   - **Summary**: 1-2 sentences condensing Context+Decision+Rationale
     (decisions) / Description+Disposition+Action (risks) /
     Acceptance+Notes (tasks). ≤5 lines of meaningful content total.

   The INDEX line already lives in `<artifact>/archive/INDEX.md` from the
   reap, and compaction does not touch it — an archive-index line is
   identical whether the body is full or compacted. Full prose remains in
   git history.

## Always

6. Never change Status, Disposition, or supersession links. Reap may add
   `Date resolved` only for explicitly confirmed `fix`/`defer` risks;
   otherwise both steps are path-and-body operations, never state
   transitions.

7. ID resolution. Cross-references (`Implements: D-019`,
   `Superseded by: D-023`, etc.) are by ID and must keep resolving.
   Skills resolving a link check both `<artifact>/<ID>.md` and
   `<artifact>/archive/<ID>.md` — `audit-artifacts` enforces this.

8. Output. Per artifact: IDs reaped (active → archive), IDs compacted,
   and a "skipped, awaiting confirmation" section for `fix`/`defer` risks
   and for `accept` risks not yet past a retrospective boundary. If
   nothing was eligible, say so — a no-op run is the normal steady state.

9. After running, recommend the `audit-artifacts` skill to verify cross-references
   still resolve, and the `reindex` skill on the scope if any INDEX line looks off.
