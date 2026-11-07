---
name: graph-sync
description: Project the planning artifacts (decisions, risks, tasks) of a scope into the optional Graphiti knowledge graph as a one-way, derived, advisory semantic index. Use to (re)sync the graph after records change, so the retrieval skills (challenge-me, red-team-me, promote) can surface semantically-related prior art across scopes. Never edits records; the graph is rebuildable and never a source of truth.
---

Project records one way into Graphiti (files → graph). The graph is the semantic sibling of INDEX: derived, advisory, and rebuildable from the files at any time. That means a bad LLM extraction is only noise, and a re-sync fixes it.

It is **optional**. It adds cross-scope semantic recall ("have we decided something like this elsewhere?") at the cost of LLM extraction tokens per sync. With no backend configured, everything here is a clean no-op.

**Reads:** the scope's records; `<scope>/.graph-sync.json`.
**Writes:** the graph and `<scope>/.graph-sync.json` only — never a record.

## Steps

1. **Prerequisites.** You need `graphiti-core` installed and a backend in the environment: `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD`, or `FALKORDB_URI` with `GRAPHITI_BACKEND=falkordb`, plus Graphiti's LLM and embedder key. If none is set, say so and stop. That's fine.

2. **Scope.** One per run: `docs` (group `project`) or `docs/features/<name>` (group `feature:<name>`).

3. **Dry run (offline).** `python3 ~/.claude/skills/_shared/scripts/graph_sync.py <scope-dir> --dry-run` prints one episode per record with its reference date. Check that the set looks right.

4. **Sync.** `python3 ~/.claude/skills/_shared/scripts/graph_sync.py <scope-dir>` sends only records whose content hash changed. `--rebuild` re-sends everything (use it after a graph wipe or a projection change). If the backend is down, the script says so, leaves the state file alone, and exits 0.

5. **Cadence.** Sync after skills that mint or mutate records (`challenge-me`, `red-team-me`, `triage-risks`, `decompose-plan`), or at session start. Reaping and compaction change paths, not bodies, so they need no re-sync.

## Never

- Treat graph results as authoritative, write graph content into a record, or block the pipeline on the graph. Audit, minting, INDEX, and reconcile stay file-only.

## Next

- Retrieval happens inside `challenge-me`, `red-team-me`, `extract-decisions`, and `promote` via `graph_query.py`.
