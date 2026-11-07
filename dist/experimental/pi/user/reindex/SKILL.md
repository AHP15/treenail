---
name: reindex
description: Rebuild one or more INDEX.md files from scratch as a pure deterministic projection of the per-record files. Use to repair INDEX drift surfaced by audit-artifacts, after a partial skill failure, after a manual edit to records, or any time you want to guarantee the index matches the authoritative per-record files. Never edits record bodies.
---
> Provider note (Pi Coding Agent experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental pi`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Pi's published surface says it does not show built-in permission popups, so scripted write steps depend on the runtime environment's shell and sandbox controls.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.2.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.2.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Regenerate INDEX files from the per-record files. INDEX is a derived projection (spec § INDEX projection), so the repair is always recomputing, never deciding. Byte-identical output is a property of the script, so always run it; never hand-type INDEX lines.

**Reads:** `<ID>.md` files in each artifact's active dir and `archive/`.
**Writes:** `<artifact>/INDEX.md` and `<artifact>/archive/INDEX.md` only.

## Steps

1. **Scope.** `docs` or `docs/features/<name>`, plus optionally a subset of `decisions risks tasks retrospectives` (default: all four).

2. **Run.** `python3 ~/.treenail/scripts/reindex.py <scope-dir> [artifact ...]`. It ignores the existing INDEX content and rebuilds both the active and archive index from the records. Re-running it on unchanged records is a no-op.

3. **Read the report.** For each index it prints `rebuilt` or `unchanged`, a line count, and `(+added/-removed)`. A non-zero exit lists **malformed records**: bodies missing a field the line format needs. That's real drift in a record body, which reindex cannot fix. Hand each one to the skill that owns it, then re-run.

## Never

- Touch a record body, status, disposition, or link, or mint, archive, or promote.

## Next

- `audit-artifacts`, to confirm zero Blockers.
