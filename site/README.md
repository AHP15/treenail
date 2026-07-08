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
without a real Cloudflare account.

Turnstile filters bots but does not bound *volume*, so the metered providers
also need a hard ceiling. Provider-side caps, volume alerting, and the dormant
global endpoint cap are specified in
[`docs/abuse-protection.md`](docs/abuse-protection.md) (R-016) — the
provider-dashboard caps there are required launch config.

## Secret scoping & preview safety (R-008 / T-014)

Every branch and PR gets a Vercel preview deploy (D-004). If those previews
inherited the production provider secrets, a single test submission against any
preview URL would send a **real** email to the owner's inbox and write a **real**
entry to the production newsletter list. To prevent that:

1. **Scope every secret to Production only.** In Vercel → Project → Settings →
   Environment Variables, set each of these for the **Production** environment
   *only* (leave Preview and Development unchecked):
   - Provider (D-006): `CONTACT_EMAIL_API_URL`, `CONTACT_EMAIL_API_KEY`,
     `CONTACT_TO_ADDRESS`, `CONTACT_FROM_ADDRESS`, `NEWSLETTER_API_URL`,
     `NEWSLETTER_API_KEY`, `NEWSLETTER_LIST_ID`.
   - Turnstile: `TURNSTILE_SECRET_KEY` (the public
     `NEXT_PUBLIC_TURNSTILE_SITE_KEY` is not a secret and may be set in Preview
     if you want the widget to render there — it is not required, since the
     sandbox skips verification).

2. **Endpoints fail safe when keys are absent.** With no provider keys (the
   preview/dev case), `handleContact` / `handleNewsletter` still validate input
   but short-circuit to a **sandbox no-op** — a `200 {ok:true}` with **no**
   provider call and no Turnstile call (`SANDBOX_RESULT` in
   `lib/forms/handlers.ts`). The forms stay demoable on a preview without any
   real write. In **Production**, missing keys are instead a loud `500`
   misconfiguration (`isProductionEnv()` in `lib/forms/providers.ts`) — never a
   silent sandbox that would drop real submissions.

3. **Forked-PR previews receive no secrets.** Vercel does not expose
   environment variables to preview deployments built from **forked** PRs by
   default; keep that default (do not opt forks into env vars). Combined with
   (1), a contributor fork can never read the provider or Turnstile secrets.

**Verify before launch:** open a preview deploy, submit both forms, and confirm
(a) you receive no email and the newsletter list gains no entry, and (b) the
submission returns success (the sandbox no-op). The automated proof of the
no-write behavior is in `test/forms.test.mjs` (the T-014 sandbox tests).
