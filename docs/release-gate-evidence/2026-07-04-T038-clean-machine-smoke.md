# T-038 clean-machine smoke — transcript (2026-07-04)

Environment: fresh temp `HOME` (no prior `~/.treenail`, no agent state),
temp npm project, macOS (darwin), Node 22+, Python 3. Driven by Claude
Code in-session against the installed artifacts; the interview leg ran
compressed with a scripted interviewee, noted inline.

## 1. Install via the real channel (packed tarball → npx)

```
$ cd cli && npm pack                       # prepack bundles dist/ in
treenail-0.0.1.tgz
$ cd <temp-proj> && npm install treenail-0.0.1.tgz
$ HOME=<temp-home> npx treenail install
Provisioned Treenail runtime 0.0.1 at <temp-home>/.treenail
Claude Code: installed 14 skills → <temp-home>/.claude/skills
opencode: installed 14 skills → <temp-home>/.config/opencode/skills
Python 3 found (python3) — scripted skill steps will work.
```

Verified: `~/.treenail/{VERSION,scripts,templates,conventions-spec.md,
conventions-examples.md,guide.md}` all present, VERSION = 0.0.1; all 14
skill dirs installed for the detected providers.

## 2. Interactive skill end-to-end (challenge-me, compressed)

The installed `challenge-me/SKILL.md` opens with the injected runtime
note ("Treenail shared runtime: paths under `~/.treenail` … If the
`TREENAIL_HOME` environment variable is set…") and references
`~/.treenail` paths throughout (5 occurrences).

Interview subject: a toy single-user notes app. One load-bearing branch
(embedded vs client-server store) was surfaced, resolved by the scripted
interviewee ("single user, no concurrent writers"), and recorded. The
record-minting tail of the skill then ran verbatim via the renamed
runtime, with `TREENAIL_HOME` pointed at the provisioned tree:

```
$ python3 $TREENAIL_HOME/scripts/mint_id.py docs/decisions D
D-001	docs/decisions/D-001.md
$ <wrote D-001: "Store the demo app's notes in SQLite">
$ python3 $TREENAIL_HOME/scripts/reindex.py docs decisions
rebuilt      1 lines  docs/decisions/INDEX.md (+1/-0)
$ python3 $TREENAIL_HOME/scripts/audit.py docs
audit docs: 0 blocker(s), 0 warn, 0 info
  clean — no mechanical violations
```

## Result

PASS — `npx treenail install` provisions `~/.treenail` on a clean
machine, installed skill text carries the renamed runtime note, and a
record was minted, indexed, and audited entirely through the provisioned
runtime with the `TREENAIL_HOME` override honored. (R-020: no runtime
failure from a missed rename token on the install → skill → script path.)
