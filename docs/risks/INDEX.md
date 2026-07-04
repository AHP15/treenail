R-001 | defer | medium | Brand collision with keel.sh / keel.so forces a rename after adoption
R-002 | defer | low | No CLA means outside contributions narrow future licensing options
R-003 | mitigate | medium | Dogfooding friction reinstates shadow editing in ~/.claude, recreating drift [tasks: T-016,T-015]
R-004 | mitigate | high | The pipeline's interactive core degrades badly on opencode/Codex and the product is judged by its weakest port [tasks: T-025,T-026,T-027]
R-005 | mitigate | high | No end-to-end behavioral validation exists for any agent; v1 can ship broken on advertised targets [tasks: T-028]
R-006 | accept | medium | The agent-neutral rewrite is a mass edit of 14 working prompts with no regression harness
R-007 | mitigate | high | Plugin-marketplace installs bypass the installer, so ~/.keel is never provisioned [tasks: T-019,T-020]
R-008 | mitigate | medium | Multi-channel installs create version skew between skill text and the ~/.keel runtime [tasks: T-017,T-018]
R-009 | accept | low | The keel-skills npm name is unreserved until first publish
R-010 | mitigate | high | Windows is claimed officially supported without Windows CI or a path-portability audit [tasks: T-005,T-006,T-024]
R-011 | mitigate | medium | Update silently destroys user edits to installed skills [tasks: T-015]
R-012 | mitigate | medium | Frozen per-project conventions require scripts to stay backward-compatible forever, with no version marker to dispatch on [tasks: T-022]
R-013 | defer | low | Flat generic skill names collide with other skill packs
R-014 | accept | low | Public docs/ exposes the monetization strategy and internal planning
R-015 | mitigate | low | Skills fail mid-run when Python 3 is absent despite the install-time warning [tasks: T-021]
R-016 | fix | medium | On Node 18/20 the installer half-works, then crashes cryptically instead of stating the version requirement
R-017 | mitigate | high | Prepack/dist bundling has no owning task, so every published package fails at distRoot() [tasks: T-033,T-034,T-028]
R-018 | mitigate | medium | The `treenail` npm name is sniped before the placeholder publish, voiding the rename's premise [tasks: T-035]
R-019 | accept | low | "Treenail" is traditionally pronounced "trunnel", splitting the verbal brand and re-colliding with Tor's DSL
R-020 | mitigate | high | The rename is a 73-file mass edit with hard-cutover semantics and no regression harness — one missed reference fails at runtime with no fallback [tasks: T-036,T-037,T-038]
R-021 | mitigate | medium | The rename races in-flight v1 distribution work — any artifact shipped under Keel branding first multiplies cutover cost [tasks: T-037,T-035,T-036,T-029]
R-022 | fix | medium | The rename dangles machine-resolvable Evidence anchors in seven done tasks — immutable-records policy collides with anchor hygiene
R-023 | fix | medium | Name-bearing anchors have no meaning-preserving repoint — the evidenced fact is abolished, not moved
R-024 | mitigate | low | The repoint duty exists only in D-024's prose — no skill or check enforces "in the same edit", so future refactors silently recreate dangling anchors [tasks: T-041]
