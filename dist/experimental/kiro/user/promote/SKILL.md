---
name: promote
description: Promote a feature-level decision or risk to project-level scope. Copies the record up, freezes the feature-level source with a cross-scope link, and surfaces related records as candidates. On-demand only — the user decides what to promote; this skill executes the mechanics correctly across files and indices.
---
> Provider note (Kiro experimental runtime adapter): this adapter is unvalidated and is installed only via `treenail install --experimental kiro`. For interviews, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Kiro supports Agent Skills and configurable permissions; scripted write steps depend on the active Kiro permission settings.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Promote one feature-level decision or risk to project scope, getting the mechanics right in both scopes.

**Reads:** the source record and its explicit links; optionally the Graphiti graph; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** a new project-level `D-MMM.md` / `R-MMM.md`, the source's promotion fields, and both scopes' INDEX files (via script).

## Steps

1. **Validate input.** `feature:<feature>/D-NNN` or `feature:<feature>/R-NNN`, one per run. Refuse if the source is project-level or already `promoted`, `superseded`, or `deprecated`.

2. **Load** the full source record.

3. **Mint the destination** in the *project* scope: `python3 ~/.treenail/scripts/mint_id.py docs/decisions D` (or `docs/risks R`).

4. **Write the destination.** Copy the source body and add `Promoted from: feature:<feature>/<ID>`. Decisions get `Status: accepted`; risks keep their Disposition. **Rewrite every bare ID in the copy to qualified form** (`feature:<feature>/D-003`, `feature:<feature>/T-007`). Left bare, a feature ID silently resolves to an unrelated project record (spec § SCOPE, qualified references). `audit-artifacts` warns about any that were copied bare.

5. **Freeze the source.** Add `Promoted to: project:<ID>`; a decision also gets `Status: promoted` and `Date promoted: <today>` (risks have no Status — the field is the marker). Leave the rest of the body untouched.

6. **Project** both scopes: `python3 ~/.treenail/scripts/reindex.py docs` and `python3 ~/.treenail/scripts/reindex.py docs/features/<feature>`.

7. **Suggest candidates** in two labelled sets, promoting none:
   - **Explicit** — the source's `Related decisions`, mitigating tasks, and `Supersedes` chain.
   - **Semantic (advisory)** — `python3 ~/.treenail/scripts/graph_query.py docs "<source title/description>" --scope all`. Silent if there's no graph.

## Never

- Migrate tasks. Existing tasks keep their feature-level references; new tasks target the project ID.
- Promote more than one record per run, or anything the user didn't ask for.

## Next

- `audit-artifacts` to verify promotion symmetry and qualified links.
