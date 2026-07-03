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
2. **Verify skill discovery** — the agent lists/loads the 14 Keel skills.
3. **Run one scripted-runtime skill** — a skill that shells out to the
   ~/.keel runtime (mint-id path), proving the provisioned runtime works.
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
the *installed* bin: `keel-skills install` must provision ~/.keel and
all 14 skills end to end from package-bundled assets only.

Pass bar: the script exits 0 (`smoke-tarball: passed`).

## Recorded passes

_None yet — the first recorded pass lands with the v1 release candidate
(T-028/T-029)._
