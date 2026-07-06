# Treenail site

Marketing landing page + documentation for Treenail, built as a Next.js
(App Router) app deployed on Vercel (D-002). It lives in this repo under
`site/` (D-004) so the docs layer can single-source canonical repo files
(`README.md`, `docs/CONVENTIONS-SPEC.md`, `skills/*/SKILL.md`) at build
time without a submodule or sync step.

## Vercel configuration

This app is **not** at the repo root. When importing the repo into Vercel,
set the project's **Root Directory** to `site/` (Project → Settings →
Build & Deployment → Root Directory). Vercel then runs `install`/`build`
inside `site/` and serves this app. The rest of the repo (the `treenail`
CLI package under `cli/`, the built `dist/` trees, the skills) is ignored
by the site build.

The npm product package is published from `cli/`, so `site/` is a sibling
of the package and never enters the published tarball (R-001, asserted by
`cli/test/smoke-tarball.mjs`).

## Local development

```sh
cd site
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm test         # node --test (form validation + screening)
```

## Spam protection (Turnstile)

The contact and newsletter endpoints are gated by a hidden honeypot field and
server-side Cloudflare Turnstile verification, keying/storing no client
identifier (D-017). Two env vars drive it:

- `NEXT_PUBLIC_TURNSTILE_SITE_KEY` — client widget site key (public).
- `TURNSTILE_SECRET_KEY` — server-side siteverify secret.

Verification **fails closed**: with no secret configured, or a token that
can't be verified, submissions are rejected (never handed off to the metered
providers). For local development use Cloudflare's documented Turnstile
**test keys** (e.g. the always-passes sitekey `1x00000000000000000000AA` and
secret `1x0000000000000000000000000000000AA`) so the forms submit end-to-end
without a real Cloudflare account. Production/preview key scoping is T-014.
