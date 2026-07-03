---
name: graph-sync
description: Project the planning artifacts (decisions, risks, tasks) of a scope into the optional Graphiti knowledge graph as a one-way, derived, advisory semantic index. Use to (re)sync the graph after records change, so the retrieval skills (challenge-me, red-team-me, promote) can surface semantically-related prior art across scopes. Never edits records; the graph is rebuildable and never a source of truth.
---

The graph is a **derived, advisory index** — the semantic sibling of
INDEX.md. The per-record `<ID>.md` files plus git history remain the
single source of truth. This skill projects records **one way** (files →
Graphiti) and never reads the graph back into a record. Because the graph
can be wiped and rebuilt from the files at any time, Graphiti's LLM-based
entity extraction can never corrupt the deterministic pipeline: a bad
extraction is advisory noise, fixed by a re-sync, exactly like INDEX drift
is fixed by the `reindex` skill.

It is **optional**. If no graph backend is configured the whole feature
is a clean no-op — sync skips, queries stay silent, and the deterministic
pipeline runs unchanged. Adopt it only when cross-scope semantic recall
("have we decided something like this before, in another feature?") is
worth a graph backend; it is a recall/intelligence play, not a token-saving
one (each sync costs LLM extraction tokens).

1. **Prereqstest.** The graph needs `graphiti-core` installed and a backend
   reachable via env (`NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`, or
   `FALKORDB_URI` with `GRAPHITI_BACKEND=falkordb`, plus whatever LLM/
   embedder key Graphiti is configured for). If none is set, say so and
   stop — there is nothing to sync, and that is fine.

2. **Scope.** One scope per invocation — project (`docs`) or a feature
   (`docs/features/<feature>`). The group_id is derived from the path
   (`docs` → `project`, a feature dir → `feature:<name>`), so each scope
   lands in its own graph partition and cross-scope queries can opt in
   explicitly.

3. **Validate the projection first (offline, no backend needed):**

   ```
   python3 ~/.claude/skills/_shared/scripts/graph_sync.py <scope-dir> --dry-run
   ```

   This parses the records (reusing `reindex.py`'s authoritative parser)
   and prints the episodes it *would* send — one per decision/risk/task,
   with the reference date it will use for Graphiti's bi-temporal model.
   Confirm the set looks right before sending.

4. **Sync incrementally:**

   ```
   python3 ~/.claude/skills/_shared/scripts/graph_sync.py <scope-dir>
   ```

   A per-scope state file `<scope>/.graph-sync.json` records the content
   hash last sent per record, so only changed records are re-sent (each
   `add_episode` costs tokens). Pass `--rebuild` to ignore the state and
   re-send everything (use after a graph wipe, or when you change the
   projection format). If the graph is unavailable the script prints a
   notice, does **not** advance the state file, and exits 0 — records will
   sync once the backend is up.

5. **Cadence.** Sync is advisory, so cadence is a convenience, not a
   correctness requirement. Reasonable triggers: after a `challenge-me` /
   `red-team-me` / `triage-risks` / `decompose-plan` run mints or mutates
   records, or at session start alongside `archive-cycle` reap. Reaping
   and compaction change a record's *path*, not its ID or body, so they
   need no re-sync; a supersede/disposition edit does (the body hash
   changes), and the incremental sync picks it up automatically.

6. **Do not** treat graph results as authoritative, write anything from
   the graph into a record, or block the pipeline on the graph. Audits,
   ID minting, INDEX projection, and reconcile remain file-only and
   deterministic. The graph only ever *suggests* — the retrieval skills
   (`challenge-me`, `red-team-me`, `promote`) query it via
   `graph_query.py` for prior-art candidates, which the user confirms.

7. **Conventions.** The record→episode projection lives in
   `_shared/scripts/graph_common.py` (`episode_body`). It leads each
   episode with the record's unique ID token and its explicit link IDs so
   Graphiti anchors to the IDs we already maintain rather than inventing
   its own.
