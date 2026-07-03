T-001 | done | S | D-012 | Scaffold the repo layout: skills/, cli/, dist/, docs/ | 2026-07-02
T-002 | done | M | D-003 | Migrate the 14 skills, _shared, and _templates from ~/.claude/skills into skills/ | 2026-07-02
T-003 | done | S | D-002 | Add the MIT license | 2026-07-02
T-004 | done | S | D-001,D-007,R-009 | Publish a placeholder keel-skills 0.0.x to npm | 2026-07-03
T-005 | done | S | D-009,R-010 | Port mint-id.sh to Python so no bash-only scripts remain | 2026-07-02
T-006 | done | M | D-009,R-010 | Audit _shared scripts for POSIX assumptions and fix Windows portability | 2026-07-02
T-007 | todo | L | D-005,R-006 | Rewrite the 14 skill bodies to agent-neutral phrasing in tagged, dogfooded batches |
T-008 | done | M | D-004,D-005 | Build pipeline core with the Claude adapter emitting dist/claude | 2026-07-02
T-009 | done | M | D-004 | opencode build adapter emitting dist/opencode | 2026-07-02
T-010 | done | M | D-004 | Codex build adapter emitting dist/codex | 2026-07-02
T-011 | done | M | D-006 | Build rewrites _shared references to KEEL_HOME-resolved ~/.keel paths | 2026-07-03
T-012 | done | S | D-007 | keel-skills detect command | 2026-07-02
T-013 | done | M | D-006,D-007,D-008,D-009 | keel-skills install: user-level per-provider install plus ~/.keel provisioning | 2026-07-03
T-014 | todo | M | D-010,D-014 | keel-skills update: wholesale overwrite of Keel-managed dirs with version stamp |
T-015 | todo | M | D-010,R-003,R-011 | Checksum manifest at install; update warns and backs up locally modified files |
T-016 | done | S | D-003,R-003 | Dev-mode install symlinks provider skill dirs to the repo checkout | 2026-07-03
T-017 | todo | S | D-014,R-008 | Lockstep version wiring: one semver stamped into the package, ~/.keel/VERSION, and built skill output |
T-018 | todo | S | D-014,R-008 | Runtime version handshake: scripts fail fast on skill-text / ~/.keel version mismatch |
T-019 | in_progress | M | D-007,R-007 | Claude plugin-marketplace channel with the shared runtime bundled inside the plugin |
T-020 | todo | S | D-006,R-007 | Scripted-invocation failures state "Keel runtime missing — run npx keel-skills install" |
T-021 | todo | S | D-009,R-015 | Scripted-write skills preflight the Python interpreter before interview work starts |
T-022 | todo | M | D-010,R-012 | Stamp a spec-version marker into project-copied conventions; scripts refuse unknown versions |
T-023 | done | M | D-012 | CI runs the _shared script tests and verifies dist/ is in sync with source | 2026-07-03
T-024 | in_progress | M | D-009,D-015,R-010 | Windows CI runner: _shared script tests plus installer smoke test, green gates v1 |
T-025 | todo | M | R-004 | Spike: run the flagship interactive skills end-to-end on opencode and Codex and record what degrades |
T-026 | todo | S | D-005,R-004 | Build injects per-provider notes adapting interview phrasing to each agent's capabilities |
T-027 | todo | M | D-007,D-013,D-015,R-004 | README: quickstart, manual copy, per-agent support-tier matrix, optional Graphiti setup, pipeline guide |
T-028 | todo | M | D-015,R-005 | Define and pass the three-agent release-gate smoke checklist |
T-029 | todo | S | D-001,D-014,D-015 | Cut v1: repo public under MIT, keel-skills 0.1.0 published, release tagged |
T-030 | done | S | D-016,D-018 | Convert cli/ to native ESM and fix the published files list | 2026-07-03
T-031 | done | S | D-020 | Startup Node-version gate in the bin plus engines >=22 | 2026-07-03
T-032 | in_progress | S | D-019 | CI smoke step runs the CLI on Node 22 |
T-033 | done | M | D-018,R-017 | Publish packaging: prepack bundles dist/ into the package, verified from the packed tarball | 2026-07-03
T-034 | in_progress | S | R-017 | Release-gate checklist gains an install-from-packed-tarball smoke in a clean environment |
