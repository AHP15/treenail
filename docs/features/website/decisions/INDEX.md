D-001 | accepted | Website planning records live at feature scope, not project scope
D-002 | accepted | Build the site as Next.js on Vercel with a live server runtime, not a static export
D-003 | accepted | Fumadocs as the documentation layer on top of Next.js
D-004 | accepted | Site lives in this repo under `site/`, with Vercel root set to that subdirectory
D-005 | accepted | Hybrid docs source-of-truth — derive reference from canonical files, author narrative fresh
D-006 | accepted | Form submissions go to managed providers; the site stores zero PII itself
D-007 | superseded | Spam protection is honeypot + server-side rate-limit, with Turnstile held in reserve (→ D-016)
D-008 | accepted | Landing leads with the pain, aimed at the individual developer
D-009 | accepted | Landing page follows an eight-section narrative arc
D-010 | accepted | Documentation is reference-complete across five top-level sections
D-011 | accepted | Visual art direction is "craft-meets-engineering", executed via the impeccable skill
D-012 | accepted | Animated interactive pipeline centerpiece; no live in-browser playground in v1
D-013 | accepted | Launch on a Vercel subdomain; adopt a custom domain later as a separate task
D-014 | accepted | Docs are single "latest", unversioned, tracking main
D-015 | accepted | Ancillary v1 defaults — built-in search, cookieless analytics, English-only, dual theme
D-016 | superseded | Spam protection is honeypot + edge rate-limit over ephemeral hashed-IP counters, reconciled with zero-durable-PII (→ D-017)
D-017 | accepted | Spam protection is honeypot + Cloudflare Turnstile day-one, with no client-identifier store
