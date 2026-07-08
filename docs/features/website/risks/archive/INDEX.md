R-001 | accept | medium | Site tooling and build artifacts leak into the published npm product tarball
R-002 | accept | medium | Single-sourcing fails silently on intra-file structure drift, not just loudly on path moves
R-003 | fix | high | Server-side rate-limiting is ineffective on stateless serverless, and fixing it reintroduces the datastore D-006 rejected
R-004 | accept | medium | The published "zero PII / no consent banner required" claim is contradicted by IP capture in the limiter, platform logs, and analytics
R-005 | accept | high | The site publishes agent-support tiers and a quickstart as public promises while the underlying product risks are unresolved
R-006 | accept | medium | The pipeline centerpiece hides its explanatory content behind hover, losing it on touch, keyboard, and assistive tech
R-008 | accept | medium | Preview deployments run live form endpoints against real providers with real secrets
R-009 | accept | medium | Docs track main while npm ships the last release, so the site documents behavior users can't yet install
R-010 | fix | high | D-016's "hashed truncated IP is not PII" premise is unsound, so it never actually resolves the D-006 tension it was minted to fix
R-011 | fix | medium | Truncating the IP for privacy coarsens the limiter key, so shared-egress users get throttled for a stranger's submissions
R-012 | fix | medium | The KV/Upstash store D-016 adds becomes an unbudgeted dependency in the request path, with fail-open/closed and quota behavior unspecified
R-013 | accept | medium | The Turnstile client widget is a third-party script that privacy tooling blocks, making the forms unsubmittable for the exact target audience
R-014 | accept | medium | The Cloudflare-branded Turnstile widget can't be themed to the craft-meets-engineering bar and lands on the highest-craft surface
R-015 | accept | medium | Turnstile adds an undisclosed Cloudflare data flow that the "cookieless / no-consent-banner / zero-PII" claim omits
R-017 | accept | medium | The server-side Turnstile siteverify call is an unbudgeted third-party dependency in the request path with unspecified fail-open/closed behavior
