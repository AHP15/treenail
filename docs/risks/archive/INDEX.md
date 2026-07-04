R-001 | defer | medium | Brand collision with keel.sh / keel.so forces a rename after adoption
R-003 | accept | medium | Dogfooding friction reinstates shadow editing in ~/.claude, recreating drift
R-004 | accept | high | The pipeline's interactive core degrades badly on opencode/Codex and the product is judged by its weakest port
R-005 | accept | high | No end-to-end behavioral validation exists for any agent; v1 can ship broken on advertised targets
R-006 | accept | medium | The agent-neutral rewrite is a mass edit of 14 working prompts with no regression harness
R-007 | accept | high | Plugin-marketplace installs bypass the installer, so ~/.keel is never provisioned
R-008 | accept | medium | Multi-channel installs create version skew between skill text and the ~/.keel runtime
R-009 | accept | low | The keel-skills npm name is unreserved until first publish
R-010 | accept | high | Windows is claimed officially supported without Windows CI or a path-portability audit
R-011 | accept | medium | Update silently destroys user edits to installed skills
R-012 | accept | medium | Frozen per-project conventions require scripts to stay backward-compatible forever, with no version marker to dispatch on
R-014 | accept | low | Public docs/ exposes the monetization strategy and internal planning
R-015 | accept | low | Skills fail mid-run when Python 3 is absent despite the install-time warning
R-016 | fix | medium | On Node 18/20 the installer half-works, then crashes cryptically instead of stating the version requirement
R-017 | accept | high | Prepack/dist bundling has no owning task, so every published package fails at distRoot()
R-018 | accept | medium | The `treenail` npm name is sniped before the placeholder publish, voiding the rename's premise
R-019 | accept | low | "Treenail" is traditionally pronounced "trunnel", splitting the verbal brand and re-colliding with Tor's DSL
R-020 | accept | high | The rename is a 73-file mass edit with hard-cutover semantics and no regression harness — one missed reference fails at runtime with no fallback
R-022 | fix | medium | The rename dangles machine-resolvable Evidence anchors in seven done tasks — immutable-records policy collides with anchor hygiene
R-023 | fix | medium | Name-bearing anchors have no meaning-preserving repoint — the evidenced fact is abolished, not moved
R-024 | accept | low | The repoint duty exists only in D-024's prose — no skill or check enforces "in the same edit", so future refactors silently recreate dangling anchors
