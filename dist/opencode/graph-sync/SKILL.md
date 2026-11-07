---
name: graph-sync
description: Project the planning artifacts (decisions, risks, tasks) of a scope into the optional Graphiti knowledge graph as a one-way, derived, advisory semantic index. Use to (re)sync the graph after records change, so the retrieval skills (challenge-me, red-team-me, promote) can surface semantically-related prior art across scopes. Never edits records; the graph is rebuildable and never a source of truth.
---
> Provider note (opencode): when a step calls for interviewing the user, ask each question in plain prose — state your recommended answer, ask if it works, and wait for the reply; there is no option-picker UI. When writing multiple Evidence anchors, comma-separate them and backtick each one. Steps that write records shell out to `~/.treenail` scripts and need file-write permission; in non-interactive runs approval must be granted up front.

> Treenail shared runtime: paths under `~/.treenail` are the installed Treenail runtime. If the `TREENAIL_HOME` environment variable is set, read every `~/.treenail/...` path as `$TREENAIL_HOME/...` instead. If a scripted step fails because that runtime is absent (a `~/.treenail/...` path does not exist), do not surface the raw path error — tell the user plainly that the Treenail runtime is missing and to run `npx treenail install`, then stop.

> Treenail skill-pack version: 0.1.0. When you run a `~/.treenail/scripts/*.py` command, append `--skill-version 0.1.0` so the runtime can catch a skill-text / runtime version mismatch and tell you to run `npx treenail update` (T-018).

> Python 3 preflight: this skill runs Treenail scripts, which need Python 3 (there is no by-hand fallback). Before any interview or analysis work, confirm Python 3 runs (`python3 --version`, or `py -3 --version` on Windows). If it does not, stop immediately and tell the user "Python 3 required — see install docs"; do not begin the work, so nothing completed is lost to a script failure.

Project records one way into Graphiti (files → graph). The graph is the semantic sibling of INDEX: derived, advisory, and rebuildable from the files at any time. That means a bad LLM extraction is only noise, and a re-sync fixes it.

It is **optional**. It adds cross-scope semantic recall ("have we decided something like this elsewhere?") at the cost of LLM extraction tokens per sync. With no backend configured, everything here is a clean no-op.

**Reads:** the scope's records; `<scope>/.graph-sync.json`.
**Writes:** the graph and `<scope>/.graph-sync.json` only — never a record.

## Steps

1. **Prerequisites.** You need `graphiti-core` installed and a backend in the environment: `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD`, or `FALKORDB_URI` with `GRAPHITI_BACKEND=falkordb`, plus Graphiti's LLM and embedder key. If none is set, say so and stop. That's fine.

2. **Scope.** One per run: `docs` (group `project`) or `docs/features/<name>` (group `feature:<name>`).

3. **Dry run (offline).** `python3 ~/.treenail/scripts/graph_sync.py <scope-dir> --dry-run` prints one episode per record with its reference date. Check that the set looks right.

4. **Sync.** `python3 ~/.treenail/scripts/graph_sync.py <scope-dir>` sends only records whose content hash changed. `--rebuild` re-sends everything (use it after a graph wipe or a projection change). If the backend is down, the script says so, leaves the state file alone, and exits 0.

5. **Cadence.** Sync after skills that mint or mutate records (`challenge-me`, `red-team-me`, `triage-risks`, `decompose-plan`), or at session start. Reaping and compaction change paths, not bodies, so they need no re-sync.

## Never

- Treat graph results as authoritative, write graph content into a record, or block the pipeline on the graph. Audit, minting, INDEX, and reconcile stay file-only.

## Next

- Retrieval happens inside `challenge-me`, `red-team-me`, `extract-decisions`, and `promote` via `graph_query.py`.
