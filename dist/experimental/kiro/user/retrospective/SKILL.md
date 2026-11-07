---
name: retrospective
description: Harvest calibration signal from a completed planning cycle by walking decisions, risks, and tasks for structural evidence of what the plan got right and wrong, then writing a dated retrospective entry with a watch-for list that seeds future challenge-me and red-team-me cycles. Run at phase boundaries, milestones, or on cadence.
---
> Provider note (Kiro experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental kiro`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Kiro supports Agent Skills and configurable permissions; scripted write steps depend on the active Kiro permission settings.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Grade the plan against what happened this cycle, and write a dated retrospective whose `Watch-for` list steers the next `challenge-me` and `red-team-me` runs.

**Reads:** the previous retrospective; `decisions/`, `risks/`, `tasks/` — both the active and the `archive/` INDEX files, plus the bodies you cite; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** `retrospectives/YYYY-MM-DD.md` + `retrospectives/INDEX.md`.

## Steps

1. **Scope.** Project (`docs/retrospectives/`) or one feature (`docs/features/<name>/retrospectives/`).

2. **Prior context.** Load the newest retrospective named in `retrospectives/INDEX.md`. Its `Watch-for` is what you will grade.

3. **Cycle boundary.** Confirm with the user what period this covers. Record it twice:
   - a human `Cycle` line;
   - a machine-readable **`Boundary-end: YYYY-MM-DD`** (today, for "since last retro").

   `Boundary-end` is load-bearing: `archive-cycle` compacts only records whose terminal date is on or before it, and does nothing without it.

4. **Gather evidence.** Records that went terminal this cycle may already be reaped into `archive/` with their full prose, so resolve every cited ID against both dirs. Load bodies only for what you cite.
   - **Risks materialized** — accepts that occurred, defers whose triggers tripped, mitigations that had to expand.
   - **Risks didn't** — defers far outside their trigger range, over-engineered guards.
   - **Decisions held** — still accepted and implemented, with no related risk materialized.
   - **Decisions broke** — superseded or deprecated this cycle. Cite the trigger from both bodies.
   - **Silent reversals** — from `reconcile-status`.
   - **Tasks dropped mid-cycle** — cite their Notes.
   - **Spikes** — did each resolve cleanly, or trigger cascades and re-splits?
   - **Prior watch-for** — each item marked hit, partial, or didn't, plus misses (things that hit but weren't on the list). Mandatory from the second retrospective on.

5. **Patterns.** Write 2-5 calibration claims about how this team mis-calibrates, each backed by at least 2 evidence items.

6. **Watch-for.** Write 3-7 concrete items for next cycle, each tied to a pattern.

7. **Write** `retrospectives/YYYY-MM-DD.md` per spec § RETROSPECTIVES, then `python3 ~/.treenail/scripts/reindex.py <scope-dir> retrospectives`.

## Never

- Modify decisions, risks, or tasks; recommendations go in Watch-for.
- Rewrite a prior retrospective. That would destroy calibration signal.

## Next

- `archive-cycle`, to compact the records this retrospective has now harvested.
