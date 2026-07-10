T-001 | done | S | D-012 | Scaffold the repo layout: skills/, cli/, dist/, docs/ | 2026-07-02
T-002 | done | M | D-003 | Migrate the 14 skills, _shared, and _templates from ~/.claude/skills into skills/ | 2026-07-02
T-003 | done | S | D-002 | Add the MIT license | 2026-07-02
T-004 | done | S | D-001,D-007,R-009 | Publish a placeholder keel-skills 0.0.x to npm | 2026-07-03
T-005 | done | S | D-009,R-010 | Port mint-id.sh to Python so no bash-only scripts remain | 2026-07-02
T-006 | done | M | D-009,R-010 | Audit _shared scripts for POSIX assumptions and fix Windows portability | 2026-07-02
T-007 | done | L | D-005,R-006 | Rewrite the 14 skill bodies to agent-neutral phrasing in tagged, dogfooded batches | 2026-07-03
T-008 | done | M | D-004,D-005 | Build pipeline core with the Claude adapter emitting dist/claude | 2026-07-02
T-009 | done | M | D-004 | opencode build adapter emitting dist/opencode | 2026-07-02
T-010 | done | M | D-004 | Codex build adapter emitting dist/codex | 2026-07-02
T-011 | done | M | D-006 | Build rewrites _shared references to KEEL_HOME-resolved ~/.keel paths | 2026-07-03
T-012 | done | S | D-007 | keel-skills detect command | 2026-07-02
T-013 | done | M | D-006,D-007,D-008,D-009 | keel-skills install: user-level per-provider install plus ~/.keel provisioning | 2026-07-03
T-014 | done | M | D-010,D-014 | keel-skills update: wholesale overwrite of Keel-managed dirs with version stamp | 2026-07-04
T-015 | done | M | D-010,R-003,R-011 | Checksum manifest at install; update warns and backs up locally modified files | 2026-07-04
T-016 | done | S | D-003,R-003 | Dev-mode install symlinks provider skill dirs to the repo checkout | 2026-07-03
T-017 | done | S | D-014,R-008 | Lockstep version wiring: one semver stamped into the package, ~/.keel/VERSION, and built skill output | 2026-07-04
T-018 | done | S | D-014,R-008 | Runtime version handshake: scripts fail fast on skill-text / ~/.keel version mismatch | 2026-07-04
T-019 | done | M | D-007,R-007 | Claude plugin-marketplace channel with the shared runtime bundled inside the plugin | 2026-07-03
T-020 | done | S | D-006,R-007 | Scripted-invocation failures state "Keel runtime missing — run npx keel-skills install" | 2026-07-04
T-021 | done | S | D-009,R-015 | Scripted-write skills preflight the Python interpreter before interview work starts | 2026-07-04
T-022 | done | M | D-010,R-012 | Stamp a spec-version marker into project-copied conventions; scripts refuse unknown versions | 2026-07-04
T-023 | done | M | D-012 | CI runs the _shared script tests and verifies dist/ is in sync with source | 2026-07-03
T-024 | done | M | D-009,D-015,R-010 | Windows CI runner: _shared script tests plus installer smoke test, green gates v1 | 2026-07-04
T-025 | done | M | R-004 | Spike: run the flagship interactive skills end-to-end on opencode and Codex and record what degrades | 2026-07-03
T-026 | done | S | D-005,R-004 | Build injects per-provider notes adapting interview phrasing to each agent's capabilities | 2026-07-03
T-027 | done | M | D-007,D-013,D-015,R-004 | README: quickstart, manual copy, per-agent support-tier matrix, optional Graphiti setup, pipeline guide | 2026-07-04
T-028 | done | M | D-015,R-005 | Define and pass the three-agent release-gate smoke checklist | 2026-07-04
T-029 | done | S | D-001,D-014,D-015 | Cut v1: repo public under MIT, treenail published, release tagged | 2026-07-08
T-030 | done | S | D-016,D-018 | Convert cli/ to native ESM and fix the published files list | 2026-07-03
T-031 | done | S | D-020 | Startup Node-version gate in the bin plus engines >=22 | 2026-07-03
T-032 | done | S | D-019 | CI smoke step runs the CLI on Node 22 | 2026-07-03
T-033 | done | M | D-018,R-017 | Publish packaging: prepack bundles dist/ into the package, verified from the packed tarball | 2026-07-03
T-034 | done | S | R-017 | Release-gate checklist gains an install-from-packed-tarball smoke in a clean environment | 2026-07-04
T-035 | done | S | D-021,D-025,R-018 | Reserve the treenail npm name with a placeholder publish | 2026-07-04
T-036 | done | M | D-021,D-022,R-020 | Rename sweep: all live keel tokens become treenail, dist regenerated via build.py | 2026-07-04
T-037 | done | S | D-022,R-020,R-021 | Release gate and CI assert zero old-name tokens and no keel-branded artifact | 2026-07-04
T-038 | done | S | D-021,R-020 | Clean-machine smoke: npx treenail install plus one full skill run against ~/.treenail | 2026-07-04
T-039 | done | S | D-025 | Repoint or pin the seven done-task Evidence anchors per D-025 | 2026-07-04
T-040 | done | S | D-025 | Anchor tooling resolves git:-pinned anchors against the named commit | 2026-07-04
T-041 | done | S | D-025,R-024 | Encode D-025's anchor-maintenance rule in the conventions spec and audit guidance | 2026-07-04
T-042 | done | S | D-022 | Rename the GitHub repo to treenail | 2026-07-04
T-043 | dropped | S | D-025 | Deprecate keel-skills on npm with a renamed-to-treenail pointer at v1 | 2026-07-08
T-044 | done | S | R-026 | Distinguish configured-but-unreachable Graphiti from unconfigured with a one-line stderr advisory | 2026-07-04
T-045 | done | S | R-027 | Add a newer-Node lane to the CI matrix so the open-ended `>=22` engines range is exercised at the ceiling | 2026-07-04
T-046 | done | S | D-026 | Remove the `skills/_templates/` scaffolds and their build/install/test coupling | 2026-07-04
T-047 | done | S | D-027 | Remove `skills/guide.md` and fold a curated subset into the README | 2026-07-04
T-048 | done | M | D-029,R-033 | Repurpose the degradation spike as a cross-agent parity validation doc | 2026-07-08
T-049 | done | L | D-028,D-030 | Restate the public support claim as functional parity plus a neutral surface note | 2026-07-08
T-050 | done | M | R-032,R-034 | Add a CI guard over the claim + support surfaces | 2026-07-08
T-051 | done | M | D-031,R-034 | Document the support bar and require a per-agent validation record | 2026-07-08
T-052 | done | L | R-031 | Re-exercise the three-agent release-gate smoke against the parity claim | 2026-07-08
T-053 | done | M | D-032,R-036 | Make the recommendation+rationale rule a standalone checkpoint in challenge-me | 2026-07-08
