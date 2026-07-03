# Spike: flagship interactive skills on opencode and Codex (T-025, R-004)

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
