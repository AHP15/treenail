---
name: promote
description: Promote a feature-level decision or risk to project-level scope. Copies the record up, freezes the feature-level source with a cross-scope link, and surfaces related records as candidates. On-demand only — the user decides what to promote; this skill executes the mechanics correctly across files and indices.
---

Promote one feature-level decision or risk to project scope, getting the mechanics right in both scopes.

**Reads:** the source record and its explicit links; optionally the Graphiti graph; the spec is `docs/CONVENTIONS-SPEC.md`.
**Writes:** a new project-level `D-MMM.md` / `R-MMM.md`, the source's promotion fields, and both scopes' INDEX files (via script).

## Steps

1. **Validate input.** `feature:<feature>/D-NNN` or `feature:<feature>/R-NNN`, one per run. Refuse if the source is project-level or already `promoted`, `superseded`, or `deprecated`.

2. **Load** the full source record.

3. **Mint the destination** in the *project* scope: `python3 ~/.claude/skills/_shared/scripts/mint_id.py docs/decisions D` (or `docs/risks R`).

4. **Write the destination.** Copy the source body and add `Promoted from: feature:<feature>/<ID>`. Decisions get `Status: accepted`; risks keep their Disposition. **Rewrite every bare ID in the copy to qualified form** (`feature:<feature>/D-003`, `feature:<feature>/T-007`). Left bare, a feature ID silently resolves to an unrelated project record (spec § SCOPE, qualified references). `audit-artifacts` warns about any that were copied bare.

5. **Freeze the source.** Add `Promoted to: project:<ID>`; a decision also gets `Status: promoted` and `Date promoted: <today>` (risks have no Status — the field is the marker). Leave the rest of the body untouched.

6. **Project** both scopes: `python3 ~/.claude/skills/_shared/scripts/reindex.py docs` and `python3 ~/.claude/skills/_shared/scripts/reindex.py docs/features/<feature>`.

7. **Suggest candidates** in two labelled sets, promoting none:
   - **Explicit** — the source's `Related decisions`, mitigating tasks, and `Supersedes` chain.
   - **Semantic (advisory)** — `python3 ~/.claude/skills/_shared/scripts/graph_query.py docs "<source title/description>" --scope all`. Silent if there's no graph.

## Never

- Migrate tasks. Existing tasks keep their feature-level references; new tasks target the project ID.
- Promote more than one record per run, or anything the user didn't ask for.

## Next

- `audit-artifacts` to verify promotion symmetry and qualified links.
