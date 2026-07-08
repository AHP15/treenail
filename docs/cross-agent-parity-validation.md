# Cross-agent parity validation: flagship interactive skills on opencode and Codex (T-025, R-004)

**Cross-agent parity, validated end-to-end.** The finding of this
document is that all three agents — Claude Code, Codex CLI, and
opencode — run the complete Treenail pipeline (challenge-me →
red-team-me → task-brief) with full fidelity, records auditing clean.
What differs is only the *interview surface*: Claude Code renders
selectable options, the other two use prose — the same interview
protocol either way. The sections below are the original dated
observations, preserved verbatim as the evidence base for R-004/R-005;
this reframe leads with parity but changes none of them. This document
also serves as the reusable template for validating a new agent against
the support bar (D-031).

## Re-validation — 2026-07-08 (T-052, R-031): current release candidate

Fresh end-to-end run against the **current build** (the one the parity
claim will ship with), because the 2026-07-03 spike below predates the
functional-parity wording and the archived T-028 gate does not validate
it. The current `dist/` was installed via the real `treenail install`
into `~/.codex/skills`, `~/.config/opencode/skills`, and `~/.treenail`.

**What was exercised — the full pipeline, both non-Claude agents.** Each
agent drove the same greenfield scenario in an isolated scratch project (a
markdown `linkcheck` CLI) whose feature pitch planted a deliberate flaw (a
20-character-prefix cache key that collides distinct URLs), to test
pushback:

- **Codex CLI 0.142.5**, model `gpt-5.5`, reasoning effort `medium`,
  driven headless via `codex exec` (`--sandbox workspace-write`).
  - *challenge-me*: recommendation-first prose interview (the per-provider
    preamble fired — "ask in prose, state your recommended answer"), minted
    D-001–D-006, `reindex`, audit **0 blockers / 0 warn / 0 info**.
    **Pushed back** on the planted prefix-key flaw with a correct
    correctness argument, and noted in-memory caching doesn't solve
    cross-process CI reuse.
  - *red-team-me*: minted 4 well-formed `pending` risks; correctly treated
    the resulting audit blockers as the by-design triage-risks handoff.
  - *task-brief*: flipped a seeded T-001 to `in_progress`, implemented a
    URL-keyed cache to Acceptance with `node --test` (2 tests pass,
    including "keeps URLs with the same 20-character prefix separate"),
    wrote Evidence anchors **verified to resolve** before landing, marked
    `done` + Date done.
- **opencode 1.17.15**, bundled **free** default model (0 credentials
  configured), driven headless via `opencode run --auto`.
  - *challenge-me*: native skill execution, recommendation-first prose
    interview, minted D-001–D-006, audit **0/0/0**. **Pushed back** on the
    prefix-key flaw *and* caught that the fetch layer doesn't exist yet;
    expanded the tree with a child URL-normalization decision.
  - *red-team-me*: 6 well-formed `pending` risks; explicitly explained the
    blockers are the expected pre-triage handoff state.
  - *task-brief*: implemented the seeded T-001 (`lib/cache.js` +
    `test/test-cache.js`, 4 tests pass), Evidence anchors **verified to
    resolve**, landed `done`.
- **Claude Code**: the dogfood baseline — the full pipeline runs on it in
  daily use (this validation was itself driven from Claude Code); not
  re-run as a separate isolated scenario.

All audits independently re-run from `~/.treenail/scripts/audit.py`, not
trusted from the agents' self-reports.

**What was NOT exercised (limits of this re-validation).** Driven headless
(`codex exec` / `opencode run`), **not** the interactive TUIs — the same
channel caveat the spike carries. One scenario per agent; the interview
user was simulated (agents answered their own clarifying questions).
Codex ran at `medium` reasoning effort, not its `xhigh` default; opencode
ran on the bundled free model, not a user's configured provider (which can
only improve on this floor). `triage-risks`/`decompose-plan`/
`sequence-work` were not run, so the `pending`-risk audit blockers are
expected, not failures. The interview *surface* difference is real and
disclosed: Claude Code renders selectable options, Codex and opencode use
prose — the same one-question-at-a-time, recommendation-first protocol
either way.

**Conclusion.** On the current build, all three agents run the complete
pipeline (challenge-me → red-team-me → task-brief) to full fidelity —
pushback intact, records auditing clean, the evidence-hygiene loop
(anchors verified before a task lands) holding on a third-party agent.
Functional parity holds; only the interview surface differs. This retires
the "stale-evidence" concern of R-031 for the current claim, within the
headless-channel limits stated above.

---

Date: 2026-07-03. Owner task: T-025 (mitigates R-004). This is the
written findings record its Acceptance names: per-agent behavior of
challenge-me, red-team-me, and task-brief run end-to-end, and what
degrades relative to Claude Code — sufficient to decide the T-027
support-tier matrix and the T-026 per-provider notes.

## Method

Each agent drove the same greenfield scenario in an isolated scratch
project (a 14-line `linkcheck` CLI): challenge-me over a deliberately
flawed feature pitch (the pitch contained a bad idea — "closest by
path distance" tiebreaking — to test pushback), then red-team-me over
the resulting decisions, then task-brief working one seeded task to
completion. Skills were installed via the real installer
(`keel-skills install`) from the current build; `~/.keel` runtime
0.0.1. The interview user was simulated turn-by-turn.

- **Codex CLI 0.142.3** (app-bundled binary), model gpt-5.5, driven via
  `codex exec` + `codex exec resume --last`, sandbox workspace-write.
  Reasoning effort overridden to `medium` for turnaround (the machine's
  default `xhigh` made single turns take 5+ minutes).
- **opencode 1.17.13**, driven via `opencode run` / `run -c`, with
  `--auto` (headless permission approval). No credentials configured —
  ran on opencode's bundled free default model ("big-pickle").

## Codex CLI findings

- **Discovery**: all 14 skills visible by name (flat names coexist with
  namespaced plugin skills; no collision behavior triggered).
- **challenge-me**: full-fidelity run. Read the codebase first,
  detected greenfield (no docs/, no retrospectives), proposed a
  leverage-ordered branch list, asked one question at a time with a
  recommendation, and pushed back unprompted on the planted
  path-distance idea with a correct safety argument. On wrap-up it
  copied conventions from `~/.keel`, minted D-001..D-007 via
  `mint_id.py`, ran `reindex.py`, then ran `audit.py` unprompted:
  0 blockers, 0 warns.
- **red-team-me**: read the skill, *chained into audit-artifacts on its
  own initiative* before red-teaming, minted six well-formed `pending`
  risks via `mint_id.py`, rebuilt the index, and correctly explained
  that the resulting audit blockers are the by-design handoff state for
  triage-risks. Risk quality was substantive, not ceremonial.
- **task-brief**: flipped the task to `in_progress`, implemented to
  Acceptance with tests (passing), verified Evidence anchors resolve
  before writing them, set `done` + `Date done`, updated INDEX, ran the
  audit, and recommended reconcile-status next. One cosmetic deviation:
  Evidence anchors written space-separated on one line rather than the
  house comma-separated backtick style (parses and audits clean).
- **Multi-turn**: `codex exec resume --last` continues the interview
  with full state. In the interactive TUI this is ordinary conversation.
- **Automation quirks** (not user-facing): `codex exec` blocks reading
  stdin unless redirected from /dev/null; global flags must precede the
  `resume` subcommand.

## opencode findings

- **Discovery**: all 14 skills visible by name.
- **challenge-me**: full-fidelity run, natively invoked via opencode's
  skill tool. Spawned an Explore subagent for the codebase pass,
  checked `~/.keel` and the Node version itself, leverage-ordered the
  branches, one question at a time with recommendations. Wrap-up minted
  D-001..D-007 via `mint_id.py` + `reindex.py`: audit 0/0/0.
- **red-team-me**: seven substantive `pending` risks, correctly formed,
  index rebuilt; correctly left dispositions for triage-risks.
- **task-brief**: the standout result. The seeded task record was
  (accidentally) contaminated: marked `done` with Evidence anchors for
  code that did not exist. opencode *detected the drift* — "T-001 is
  marked done but the Evidence anchors don't resolve — the code doesn't
  exist yet" — re-opened it to `in_progress`, implemented to Acceptance
  with its own test fixtures (passing), verified anchors, and re-landed
  it. The pipeline's core hygiene loop held on a third-party agent.
- **Free-tier caveat**: all of the above ran on the bundled free
  default model with zero configuration. A user's configured provider
  (Anthropic/OpenAI/etc. via `opencode auth login`) can only improve on
  this floor; it was not exercised in this spike.
- **Automation quirks**: headless runs need `--auto` to approve file
  writes; multi-turn needs `-c`/`--session`. In the TUI both are
  ordinary interactive behavior.

## What actually degrades (vs Claude Code)

1. **Structured multi-option questions.** Claude Code renders
   selectable options (AskUserQuestion). Both other agents fall back to
   prose questions answered in free text. The interview *protocol*
   (one question at a time, recommendation-first) survived intact on
   both; only the selection UI is lost. Severity: cosmetic-to-minor.
2. **Skill-to-skill chaining is implicit.** Claude Code has a first-
   class Skill tool; Codex reads the referenced SKILL.md as a file and
   follows it (observed doing this unprompted); opencode has native
   skill invocation. No functional loss observed, but slash-style
   references (`/reindex`) in skill bodies are a Claude-ism the other
   agents interpret rather than execute — T-007 should neutralize the
   remaining 27 slash-style cross-references.
3. **Evidence anchor formatting drift.** Codex wrote anchors
   space-separated rather than comma-separated. Audits clean; worth a
   one-line formatting note in the built output (T-026) or an example
   in CONVENTIONS-SPEC.
4. **Nothing else material.** Scripted runtime (`mint_id.py`,
   `reindex.py`, `audit.py`, `graph_query.py` silent-fallback), record
   formats, INDEX discipline, greenfield bootstrap (conventions copy),
   interview pushback, and drift detection all worked end-to-end on
   both agents.

## Support-tier recommendation (input to T-027)

- **Claude Code — Best**: structured interview UI, native skill
  chaining, the environment the skills are dogfooded in daily.
- **Codex CLI — Full**: complete pipeline fidelity observed; interview
  arrives as prose questions.
- **opencode — Full**: complete pipeline fidelity observed, including
  on the zero-config free model; interview arrives as prose questions.

"Judged by its weakest port" (R-004): on this evidence the weakest port
still runs the whole pipeline correctly; the honest matrix claim is
"best on Claude Code, fully functional on Codex CLI and opencode."

## Per-provider notes candidates (input to T-026)

- Both non-Claude agents: phrase interview steps as "ask in prose and
  wait for the reply" (no option-list rendering); state Evidence anchor
  format explicitly (comma-separated, backticked).
- opencode: note that scripted-write steps require permission approval
  (or `--auto` in headless runs).
- Codex: no skill-body adaptation found necessary beyond the above.

## Limits of this spike

Non-interactive driving (exec/run) rather than each agent's TUI; one
scenario per skill; simulated user; Codex at medium reasoning effort
(not its default); opencode on its free model. T-028's release gate
re-validates on real channels interactively — this spike de-risks the
capability question, not the release.
