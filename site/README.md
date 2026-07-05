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
```
