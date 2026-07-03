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
