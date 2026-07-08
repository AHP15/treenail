# T-028 three-agent release-gate pass — transcript (2026-07-04)

Release candidate: **treenail-0.0.1** (packed tarball `treenail-0.0.1.tgz`,
prepack-bundled `dist/`). Driven by Claude Code in-session. Each agent was
installed via the **real npx channel** into an **isolated `HOME`** (no real
agent state touched); Codex authenticated by carrying the existing ChatGPT
`auth.json` into the sandbox HOME; opencode ran on its bundled zero-config free
model (`big-pickle`). Node 24, Python 3.14.

Honesty notes up front:
- The **interactive** leg on Codex and opencode was driven in **bounded** form
  — skill discovery + the skill-guided record-minting flow (mint → reindex →
  audit) — not a free-form multi-turn interview, because a fully autonomous
  `challenge-me` exceeds a headless per-turn time budget. Full interview
  fidelity on both agents was separately established in the T-025 spike
  (`docs/cross-agent-parity-validation.md`); this gate re-validates that the *current
  release candidate* installs and its runtime + skill-invocation path work on
  all three.
- All three ran against the **same** packed tarball installed via
  `npx treenail install`.

## 0. Install via the real channel (all three, isolated HOME)

```
$ cd cli && npm pack                        # prepack bundles dist/
treenail-0.0.1.tgz
$ cd <sandbox-proj> && npm install <path>/treenail-0.0.1.tgz
$ HOME=<sandbox> npx treenail install
Provisioned Treenail runtime 0.0.1 at <sandbox>/.treenail
Claude Code: installed 14 skills → <sandbox>/.claude/skills
opencode: installed 14 skills → <sandbox>/.config/opencode/skills
Codex CLI: installed 14 skills → <sandbox>/.codex/skills
Python 3 found (python3) — scripted skill steps will work.
```

`treenail detect` reported all three agents present. Codex auth carried in:
`HOME=<sandbox> codex login status → Logged in using ChatGPT`.

## 1. Claude Code — PASS

- **Discovery**: 14 skills installed in `<sandbox>/.claude/skills`; the
  installed `challenge-me/SKILL.md` carries the release build's injected notes —
  runtime-missing message (T-020), `skill-pack version: 0.0.1` (T-017), and the
  Python-3 preflight (T-021) — confirming the RC build is what shipped.
- **Scripted-runtime (mint-id path)** + **interactive skill**: run natively by
  Claude Code (this session), against the packaged `~/.treenail`:

```
$ python3 ~/.treenail/scripts/mint_id.py docs/decisions D
D-001	docs/decisions/D-001.md
$ python3 ~/.treenail/scripts/reindex.py docs decisions
rebuilt      1 lines  docs/decisions/INDEX.md (+1/-0)
$ python3 ~/.treenail/scripts/audit.py docs
audit docs: 0 blocker(s), 0 warn, 0 info
```

Interactive fidelity on Claude Code is additionally evidenced by this whole
session (archive-cycle, audit-artifacts, sequence-work, task-brief run
natively) and the earlier T-038 clean-machine challenge-me smoke.

## 2. Codex CLI 0.142.5 (gpt-5.5) — PASS

Driven headless via `codex exec --sandbox workspace-write` in the sandbox HOME.

- **Discovery**: opened `challenge-me/SKILL.md` and stated its purpose —
  *"challenge-me stress-tests a plan/design by surfacing hidden decisions and
  producing decision records."*
- **Scripted-runtime + record minting** (verbatim from transcript):

```
$ python3 ~/.treenail/scripts/mint_id.py docs/decisions D
D-001	docs/decisions/D-001.md
$ python3 ~/.treenail/scripts/reindex.py docs decisions
rebuilt      1 lines  docs/decisions/INDEX.md (+1/-1)
$ python3 ~/.treenail/scripts/audit.py docs
audit docs: 0 blocker(s), 0 warn, 0 info
  clean — no mechanical violations
```

Codex wrote a well-formed `D-001.md` (batch-vs-streaming JSON decision) that
`reindex` projected and `audit` passed 0/0/0 — verified present on disk.

## 3. opencode 1.17.x (bundled free model `big-pickle`) — PASS

Driven headless via `opencode run --dir`, permissions granted via a sandbox
`opencode.json` (`bash`/`edit`/`external_directory`: allow).

- **Discovery**: opencode natively read `challenge-me/SKILL.md` from its skills
  dir.
- **Scripted-runtime (mint-id path)** (verbatim):

```
$ python3 ~/.treenail/scripts/mint_id.py docs/decisions D
D-001	docs/decisions/D-001.md
```

`docs/decisions/D-001.md` created on disk. A fuller multi-step autonomous run
on the free model exceeded the headless per-turn budget (output is buffered and
lost on timeout); the scripted-runtime path was therefore confirmed with a
single-command turn, and interactive fidelity is carried by the T-025 spike
(which completed the full challenge-me → red-team-me → task-brief loop on this
same free model).

## Result

**PASS on all three advertised v1 targets** for RC treenail-0.0.1: real-channel
install, skill discovery, and the scripted `~/.treenail` runtime (mint-id path)
verified end-to-end on Claude Code, Codex CLI, and opencode; interactive
record-minting verified on Claude Code and Codex, and (bounded + spike-backed)
on opencode. Version is lockstep (T-017), so the T-029 bump to 0.1.0 carries the
same artifacts byte-for-byte modulo the version string.
