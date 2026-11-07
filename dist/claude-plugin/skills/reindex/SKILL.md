---
name: reindex
description: Rebuild one or more INDEX.md files from scratch as a pure deterministic projection of the per-record files. Use to repair INDEX drift surfaced by audit-artifacts, after a partial skill failure, after a manual edit to records, or any time you want to guarantee the index matches the authoritative per-record files. Never edits record bodies.
---
> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

INDEX is a derived projection, not a source of truth. This skill
discards the existing INDEX content and regenerates it from the
per-record files. It writes only INDEX.md files; it never touches a
record body, status, disposition, or link.

The projection is mechanical and must be byte-identical across runs, so
**run the script rather than hand-projecting** — an LLM re-typing pipe
lines cannot guarantee determinism, the script can.

1. Scope. One artifact (`decisions`, `risks`, or `tasks`) or all three,
   at project- or feature-level. Each artifact has **two** indexes —
   `<artifact>/INDEX.md` (active records) and `<artifact>/archive/INDEX.md`
   (archived records) — and `reindex` rebuilds both. Invoked with no
   argument, it rebuilds every index in the current scope. Retrospectives have
   an INDEX too (no archive) — rebuild it the same way when asked.

2. Run the projector against the scope's docs root:

   ```
   python3 ~/.treenail/scripts/reindex.py <scope-dir> [artifact ...]
   ```

   `<scope-dir>` is the docs root for the scope — `docs` for project
   level, `docs/features/<feature>` for feature level. Omit the artifact
   list to rebuild all of `decisions risks tasks retrospectives`, or pass
   a subset (e.g. `... docs decisions`). The script reads the
   authoritative `<ID>.md` files (active dir → `<artifact>/INDEX.md`,
   `archive/` → `<artifact>/archive/INDEX.md`), ignores existing INDEX
   content entirely, and writes both indexes sorted ascending by numeric
   ID (date for retrospectives), with no blank lines and no trailing
   whitespace. Re-running on an unchanged source set is a byte-identical
   no-op.

3. Read the script's report. Per index it prints `rebuilt`/`unchanged`,
   the line count, and a `(+added/-removed)` diff against the prior
   INDEX. It exits non-zero and lists **malformed records** — bodies
   missing a field the line format requires (the line is still emitted,
   with that field blank). These are the real drift; `reindex` cannot fix
   a record body, only the index. Hand the malformed list to the owning
   skill to fix the body, then re-run.

4. The projection the script implements (for reference; also in
   CONVENTIONS-SPEC.md "INDEX projection"). Identical line format for
   active and archive indexes — no `[archived]` marker; the index a line
   lives in is the archived signal:
   - **decisions**: `D-NNN | <status> | <title>`. Appends `(→ D-MMM)` if
     the body has `Superseded by: D-MMM`; `(→ project:D-MMM)` if it has
     `Promoted to: project:D-MMM`.
   - **risks**: `R-NNN | <disposition> | <severity> | <title>`. If
     disposition is `mitigate` and the Action cites task IDs, appends
     `[tasks: T-NNN,...]` (the exact set the body references).
   - **tasks**: `T-NNN | <status> | <size> | <implements/mitigates> | <title> | <terminal date>`.
     `<implements/mitigates>` is the comma-joined union of the body's
     `Implements` then `Mitigates` IDs. `<terminal date>` is status-gated:
     `Date done` for a `done` task, `Date dropped` for a `dropped` task,
     empty for `todo`/`in_progress`.
   - **retrospectives**: `YYYY-MM-DD | <cycle name>`, one per file,
     filename is the date.

5. If `python3` is unavailable, fall back to projecting by hand per the
   format in step 4 — but treat that as a degraded path and re-run the
   script as soon as it is available, since only it guarantees the
   byte-identical projection `audit-artifacts` checks against.

6. Do not modify record bodies, statuses, dispositions, or links. Do
   not mint, archive, or promote. If a record looks wrong, report it;
   fixing the body is the owning skill's job. Recommend the `audit-artifacts`
   skill afterward to confirm zero Blockers.

7. Conventions. Reference `docs/CONVENTIONS-SPEC.md` for the exact line
   formats and the "INDEX projection" section.
