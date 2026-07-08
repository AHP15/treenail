# Treenail

**Treenail** is a planning-skills pack for agent-driven development. It gives
your coding agent a durable planning spine — append-only **decision** records
laid down first, with every **risk** and **task** hanging off them — plus the
skills that drive the pipeline: challenge a plan, red-team it, triage risks,
decompose into tasks, sequence the work, build it, and reconcile what shipped
against what was decided.

The records live in your repo under `docs/` and are the source of truth. The
skills read `O(active work)`, not `O(all history)`, so the planning record
stays fast as the project grows.

Supported agents: **Claude Code**, **Codex CLI**, and **opencode** (user-level
installs). Requires **Node ≥ 22** and **Python 3** for the scripted steps.

---

## Quickstart (npx)

The installer detects which supported agents are present and installs the
per-provider skill files for each, then provisions the shared runtime into
`~/.treenail` (overridable via `$TREENAIL_HOME`):

```sh
npx treenail detect     # report which supported agents are present
npx treenail install    # install skills for detected agents + provision ~/.treenail
npx treenail update      # overwrite Treenail-managed dirs with this version
```

That's the whole install story for most users. Restart your agent so it
re-scans its skills directory, then invoke a skill (e.g. `challenge-me`) to
start planning.

### Claude plugin marketplace

Claude Code users can instead install Treenail as a plugin from the
marketplace manifest at the repo root
([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)). The
plugin bundles the shared runtime and provisions `~/.treenail` on first
session, so plugin-managed and CLI-managed installs share one runtime.

---

## Manual copy (no npx)

Every provider build is committed under [`dist/`](dist/), so you can install by
copying — no Node tooling required:

```sh
git clone https://github.com/AHP15/treenail.git
```

Then copy the tree for your agent into its skills directory, and copy the
shared runtime into `~/.treenail`:

| Agent        | Copy skills from        | Into                            |
| ------------ | ----------------------- | ------------------------------- |
| Claude Code  | `dist/claude/`          | `~/.claude/skills/`             |
| Codex CLI    | `dist/codex/`           | `~/.codex/skills/`              |
| opencode     | `dist/opencode/`        | `~/.config/opencode/skills/`    |
| *(all)*      | `dist/treenail-home/`   | `~/.treenail/`                  |

The skill bodies read the shared scripts, templates, and conventions from
`~/.treenail`, so the runtime copy is required for the scripted steps
(`mint_id.py`, `reindex.py`, `audit.py`, …) to work.

---

## Per-agent support tiers

Treenail's flagship skills are built around structured interviews and
agentic multi-step sessions. All three agents run the **complete pipeline
correctly**; what differs is the interview surface. This matrix is honest
about that — it is validated end-to-end, not aspirational (see the
[cross-agent parity validation](docs/cross-agent-parity-validation.md)).

| Agent           | Tier     | What to expect                                                                 |
| --------------- | -------- | ------------------------------------------------------------------------------ |
| **Claude Code** | **Best** | Structured selectable-option interviews, native skill-to-skill chaining; the environment Treenail is dogfooded in daily. |
| **Codex CLI**   | **Full** | Complete pipeline fidelity. Interview questions arrive as prose (answer in free text) rather than a selectable option list. |
| **opencode**    | **Full** | Complete pipeline fidelity, verified even on the zero-config free model. Interview questions arrive as prose. Headless runs need `--auto` to approve file writes. |

The one-line claim: **best on Claude Code, fully functional on Codex CLI and
opencode.** The record formats, INDEX discipline, greenfield bootstrap,
interview pushback, and drift detection all hold on every agent.

---

## Optional: Graphiti semantic index

Treenail works fully without it. If you want the retrieval skills
(`challenge-me`, `red-team-me`, `promote`) to surface semantically-related
prior art across scopes, the `graph-sync` skill can project your records into
an optional [Graphiti](https://github.com/getzep/graphiti) knowledge graph.
This is a one-way, derived, rebuildable index — never a source of truth.

Setup is entirely yours; the installer neither installs nor checks it. You need:

- `graphiti-core` installed, and
- a reachable backend via env — either Neo4j (`NEO4J_URI`, `NEO4J_USER`,
  `NEO4J_PASSWORD`) or FalkorDB (`FALKORDB_URI` with
  `GRAPHITI_BACKEND=falkordb`) — plus whatever LLM/embedder key Graphiti is
  configured for.

If none is configured, the graph skills detect that and no-op silently — no
error, nothing to sync.

---

## The pipeline

```
challenge-me → red-team-me → triage-risks → decompose-plan → sequence-work → task-brief
                                                                                    ↓
                                              reconcile-status ⇄ audit-artifacts ⇄ archive-cycle
```

Each skill is one step in the flow, reading the records the step before it
wrote and writing the ones the next step reads:

- **`challenge-me`** — interviews a plan into `accepted` **decision** records,
  surfacing the choices you hadn't noticed you were making.
- **`red-team-me`** — attacks those decisions and raises **risk** records; it
  proposes no fixes.
- **`triage-risks`** — assigns every risk a disposition: `fix` (supersede a
  decision), `mitigate` (spawn tasks), `accept`, or `defer`.
- **`decompose-plan`** — turns the decisions and mitigations into **task**
  records with machine-resolvable acceptance criteria.
- **`sequence-work`** — orders the open tasks into an ephemeral phased plan.
- **`task-brief`** — drives implementation one task at a time, assembling each
  task's brief and writing back its status plus the code **Evidence** anchors
  that prove it landed.
- **`reconcile-status`** — derives which decisions are *actually* implemented
  from task state and resolves their Evidence anchors against the working tree,
  flagging drift between "tasks done" and "decision built."
- **`audit-artifacts`** — a gate you can run any time: cross-checks each INDEX
  against its records and catches dangling links or malformed Evidence.
- **`retrospective`** — at a phase boundary, harvests what held, what broke,
  and which risks materialized into a dated cycle record.
- **`archive-cycle`** — reaps terminally-resolved records off the active read
  path and compacts the bodies a retrospective has harvested.

Supporting skills: **`extract-decisions`** (brownfield ingress —
reconstructs the decisions already embodied in existing code),
**`promote`** (lifts a feature-scoped record to project scope),
**`reindex`** (rebuilds an INDEX from its authoritative records), and
**`graph-sync`** (the optional one-way projection to Graphiti).

### What it writes into your repo

The records live under `docs/`, one file per record, split so day-to-day
skills read only the active set:

```
docs/
  CONVENTIONS-SPEC.md        # the record schema (source of truth for format)
  CONVENTIONS-EXAMPLES.md    # exemplars, loaded only when tailoring
  decisions/
    INDEX.md                 # one line per active decision (always loaded)
    D-001.md, D-002.md …     # full bodies, read on demand by ID
    archive/                 # terminal records + their INDEX line, off the hot path
  risks/     INDEX.md  R-NNN.md …  archive/
  tasks/     INDEX.md  T-NNN.md …  archive/
  retrospectives/  INDEX.md  YYYY-MM-DD.md
  features/<feature>/…       # same structure, feature-scoped
```

A record's ID is unique within its scope and never changes; moving to
`archive/` moves both the body and its INDEX line together. INDEX files are a
derived projection of the per-record files — if one drifts, `reindex` rebuilds
it; never hand-edit an INDEX to match.

### When to run what

| Trigger | Run |
|---|---|
| Session start (existing project) | `archive-cycle` (reap) → `audit-artifacts` → `reconcile-status` |
| A batch of tasks changed state | `archive-cycle` (reap) → `reconcile-status` |
| Before any downstream planning skill | `audit-artifacts` |
| Phase boundary, milestone, ≥3 done tasks | `retrospective` |
| After every retrospective | `archive-cycle` (now also compacts the harvested records) |
| `audit-artifacts` reports INDEX drift | `reindex <scope>` |
| A new cycle starts | `challenge-me` (auto-reads the latest retrospective's Watch-for) |

---

## License

[MIT](LICENSE).
