D-001 | superseded | Keep the Keel brand; publish the installer as `keel-skills` on npm (→ D-021)
D-002 | accepted | MIT license
D-003 | accepted | The repo is the canonical source; ~/.claude/skills becomes an install target
D-004 | accepted | Single canonical skill source compiled per provider by a build step
D-005 | accepted | Claude-style SKILL.md is the canonical authoring format, written agent-neutrally
D-006 | accepted | Shared runtime lives in an agent-neutral ~/.keel home (overridable via KEEL_HOME)
D-007 | accepted | Distribution channels — npx installer, manual copy, and Claude plugin marketplace
D-008 | accepted | User-level installs only in v1
D-009 | accepted | Python 3 is the one scripted-runtime dependency; Windows, macOS, and Linux all officially supported
D-010 | accepted | Updates overwrite Keel-managed dirs; per-project docs are never touched
D-011 | accepted | Keep flat skill names in v1; record collision risk
D-012 | accepted | Repo layout skills/ + cli/ + committed dist/ + public dogfooded docs/
D-013 | accepted | Graphiti stays optional; skills ship as-is and setup is the user's job
D-014 | accepted | Single semver for the whole repo, starting at 0.1.0
D-015 | accepted | v1 cut line
D-016 | accepted | The installer CLI is native ESM — `"type": "module"`, static imports, named exports
D-017 | superseded | Node engine floor for the installer is >=22 (→ D-020)
D-018 | accepted | Fix `files` to include `lib/` now; prepack/dist bundling stays with the publish task
D-019 | accepted | CI smoke-runs the installer CLI on Node 22
D-020 | accepted | Node >=22 enforced by a startup version gate in the bin, not just advisory engines
D-021 | accepted | Rename the project to Treenail
D-022 | accepted | One name across every surface — brand, npm, CLI, env var, home dir, plugin
D-023 | superseded | Rename migration — reserve `treenail` on npm now; hard cutover, no old-name compat (→ D-024)
D-024 | superseded | Rename migration — reserve `treenail` now, hard cutover, prose immutable but Evidence anchors maintained as live pointers (→ D-025)
D-025 | accepted | Anchor maintenance has two modes — repoint moved targets, pin abolished ones to git history
