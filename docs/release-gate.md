# Release-gate smoke checklist

Passing this checklist against the release candidate is a v1 ship
criterion (D-015, R-005). A completed pass is recorded at the bottom of
this file with the version, date, and per-item results. Owned by T-028;
the clean-environment tarball item is T-034's (R-017).

## Per-agent checks (T-028 — defined per agent, run on all three)

For each of Claude Code, opencode, and Codex CLI:

1. **Install via the real channel** — the channel a user would actually
   use (npx installer for all three; additionally the plugin marketplace
   for Claude Code), not a repo-checkout shortcut.
2. **Verify skill discovery** — the agent lists/loads the 15 Treenail skills.
3. **Run one scripted-runtime skill** — a skill that shells out to the
   ~/.treenail runtime (mint-id path), proving the provisioned runtime works.
4. **Run one interactive skill end-to-end** — e.g. challenge-me, proving
   the interview core works on that agent.

## Clean-environment tarball install (T-034, R-017)

A repo-checkout smoke structurally cannot catch a package that ships
without dist/ — `distRoot()` falls back to the repo's own `dist/`. This
item therefore runs from the packed tarball in a temp dir with no
checkout:

```
node cli/test/smoke-tarball.mjs
```

The script packs `cli/`, installs the tarball into a clean temp project,
and runs the full installer smoke (`cli/test/smoke-install.mjs`) against
the *installed* bin: `treenail install` must provision ~/.treenail and
all 15 skills end to end from package-bundled assets only.

Pass bar: the script exits 0 (`smoke-tarball: passed`).

## Rename integrity (T-037, R-020/R-021)

Nothing publishes under the old Keel branding. Two checks, both also
enforced on every push by CI's "old-name token gate" step:

1. **Zero live old-name tokens** — a repo-wide case-insensitive grep for
   `keel` finds nothing outside the immutable planning records
   (docs/decisions, docs/risks, docs/tasks, docs/retrospectives), the
   dated spike lore (docs/cross-agent-parity-validation.md), and this file
   (which must name the token to document the check):

   ```
   git grep -I -n -i -e keel -- . \
     ':(exclude)docs/decisions' ':(exclude)docs/risks' \
     ':(exclude)docs/tasks' ':(exclude)docs/retrospectives' \
     ':(exclude)docs/cross-agent-parity-validation.md' \
     ':(exclude)docs/release-gate.md'
   ```

   Pass bar: no matches (the command exits 1).

2. **Every publishable name reads `treenail`** — the npm package name
   (which names the packed tarball), the plugin manifest name
   (dist/claude-plugin/.claude-plugin/plugin.json), and the marketplace
   name and plugin entry (.claude-plugin/marketplace.json) all equal
   `treenail`. CI asserts this with `cli/test/check-rename.mjs`; the
   tarball smoke above then proves the packed artifact installs under
   that name.

## Recorded passes

- 2026-07-04 — **T-028 three-agent pass on RC treenail-0.0.1**: real-channel
  npx install into an isolated HOME on all three agents, skill discovery, and
  the scripted `~/.treenail` runtime (mint-id path) verified end-to-end on
  **Claude Code, Codex CLI, and opencode**; interactive record-minting verified
  on Claude Code and Codex, bounded + T-025-spike-backed on opencode. PASS.
  Transcript:
  [release-gate-evidence/2026-07-04-T028-three-agent-pass.md](release-gate-evidence/2026-07-04-T028-three-agent-pass.md).
  Version is lockstep (T-017); the T-029 bump to 0.1.0 carries the same
  artifacts modulo the version string, so re-run only if the build changes.

- 2026-07-04 — T-038 clean-machine rename smoke (tarball install into a
  fresh HOME + one interactive skill minting a record via `~/.treenail`):
  PASS. Transcript:
  [release-gate-evidence/2026-07-04-T038-clean-machine-smoke.md](release-gate-evidence/2026-07-04-T038-clean-machine-smoke.md)
