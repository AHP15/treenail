R-002 | defer | low | No CLA means outside contributions narrow future licensing options
R-013 | defer | low | Flat generic skill names collide with other skill packs
R-021 | mitigate | medium | The rename races in-flight v1 distribution work — any artifact shipped under Keel branding first multiplies cutover cost [tasks: T-037,T-035,T-036,T-029]
R-025 | defer | medium | User-level-only installs give a team no shared version pin, so teammates on different Treenail versions write divergent records into one committed docs/
R-026 | mitigate | low | Silent Graphiti degradation makes a broken optional setup undiagnosable — the user cannot tell "no prior art" from "my backend is down" [tasks: T-044]
R-027 | mitigate | low | The CI CLI smoke pins Node 22 while engines allows any >=22, so a break on a newer Node major that users actually run is invisible to CI [tasks: T-045]
R-028 | accept | medium | D-027 removes the guide that D-015's still-open v1-cut criterion says the README must cover, so the v1 gate has no referent at the publish moment
R-029 | defer | low | The guide→README migration dropped the scenario walkthroughs, leaving no in-repo end-to-end onboarding path for first external adopters
R-030 | accept | low | Removing the only conforming authoring scaffold risks the next interview-family skill being authored with malformed frontmatter or a missed build-injection assumption
