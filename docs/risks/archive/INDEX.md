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
R-021 | accept | medium | The rename races in-flight v1 distribution work — any artifact shipped under Keel branding first multiplies cutover cost
R-022 | fix | medium | The rename dangles machine-resolvable Evidence anchors in seven done tasks — immutable-records policy collides with anchor hygiene
R-023 | fix | medium | Name-bearing anchors have no meaning-preserving repoint — the evidenced fact is abolished, not moved
R-024 | accept | low | The repoint duty exists only in D-024's prose — no skill or check enforces "in the same edit", so future refactors silently recreate dangling anchors
R-026 | accept | low | Silent Graphiti degradation makes a broken optional setup undiagnosable — the user cannot tell "no prior art" from "my backend is down"
R-027 | accept | low | The CI CLI smoke pins Node 22 while engines allows any >=22, so a break on a newer Node major that users actually run is invisible to CI
R-028 | accept | medium | D-027 removes the guide that D-015's still-open v1-cut criterion says the README must cover, so the v1 gate has no referent at the publish moment
R-030 | accept | low | Removing the only conforming authoring scaffold risks the next interview-family skill being authored with malformed frontmatter or a missed build-injection assumption
R-031 | accept | high | The flat "full pipeline on all three" claim strengthens the public promise while its evidence stays explicitly caveated and R-005 is an unretired high risk
R-032 | accept | medium | The parity claim and its honesty-critical surface note propagate across four+ surfaces independently, so at least one ends up with the claim minus the note
R-033 | accept | medium | Renaming and reframing the spike breaks its inbound references and risks softening the raw observations R-004/R-005 rest on
R-034 | accept | medium | The support bar is an unenforced documentary norm — nothing stops an agent being advertised before it is validated
R-035 | accept | low | The support-bar pass criteria are weak and subjective, so a non-conforming agent can still pass
R-036 | accept | medium | D-032 treats a compliance problem as a wording problem, so the observed symptom can recur while the decision reads as done
R-037 | accept | low | Scoping the rationale rule to challenge-me leaves the same defect legal in other choice-surfacing skills, and its revisit trigger may never fire
