R-001 | mitigate | medium | Site tooling and build artifacts leak into the published npm product tarball [tasks: T-016]
R-002 | mitigate | medium | Single-sourcing fails silently on intra-file structure drift, not just loudly on path moves [tasks: T-004]
R-003 | fix | high | Server-side rate-limiting is ineffective on stateless serverless, and fixing it reintroduces the datastore D-006 rejected
R-004 | mitigate | medium | The published "zero PII / no consent banner required" claim is contradicted by IP capture in the limiter, platform logs, and analytics [tasks: T-015]
R-005 | mitigate | high | The site publishes agent-support tiers and a quickstart as public promises while the underlying product risks are unresolved [tasks: T-018]
R-006 | mitigate | medium | The pipeline centerpiece hides its explanatory content behind hover, losing it on touch, keyboard, and assistive tech [tasks: T-008]
R-007 | mitigate | medium | Launching on the vercel.app subdomain bakes a throwaway public URL into README, npm, SEO, and backlinks [tasks: T-019,T-020]
R-008 | mitigate | medium | Preview deployments run live form endpoints against real providers with real secrets [tasks: T-014]
R-009 | mitigate | medium | Docs track main while npm ships the last release, so the site documents behavior users can't yet install [tasks: T-017]
R-010 | fix | high | D-016's "hashed truncated IP is not PII" premise is unsound, so it never actually resolves the D-006 tension it was minted to fix
R-011 | fix | medium | Truncating the IP for privacy coarsens the limiter key, so shared-egress users get throttled for a stranger's submissions
R-012 | fix | medium | The KV/Upstash store D-016 adds becomes an unbudgeted dependency in the request path, with fail-open/closed and quota behavior unspecified
R-013 | mitigate | medium | The Turnstile client widget is a third-party script that privacy tooling blocks, making the forms unsubmittable for the exact target audience [tasks: T-021]
R-014 | mitigate | medium | The Cloudflare-branded Turnstile widget can't be themed to the craft-meets-engineering bar and lands on the highest-craft surface [tasks: T-013]
R-015 | mitigate | medium | Turnstile adds an undisclosed Cloudflare data flow that the "cookieless / no-consent-banner / zero-PII" claim omits [tasks: T-015]
R-016 | mitigate | high | With the per-client limiter removed and the global cap deferred, nothing rate-limits token-solved abuse of the metered providers [tasks: T-022]
R-017 | mitigate | medium | The server-side Turnstile siteverify call is an unbudgeted third-party dependency in the request path with unspecified fail-open/closed behavior [tasks: T-013]
