# Abuse protection — metered-provider ceilings (R-016)

Turnstile (D-017) filters bots; it does **not** bound volume. A solver farm, a
headless real browser, or a single legitimate-looking loop can still obtain
valid tokens and submit at will. With no cap in the request path, that traffic
flows straight to the metered transactional-email API and the hosted-list
provider — running up per-message cost, flooding the owner's inbox, and
polluting the newsletter list (the exact resources D-006 exists to protect).

Treenail stores **no client identifier** (D-006/D-017 zero-PII posture, held
after R-010/R-011 killed the IP-keyed store). So the volume ceiling lives where
cost is already metered: **at the providers**. This runbook is vendor-agnostic
— it specifies the caps to set on whichever transactional-email and hosted-list
provider is wired via the `CONTACT_*` / `NEWSLETTER_*` env seam
(`site/lib/forms/providers.ts`); vendor selection is a deferred follow-up
(D-006).

**These caps are launch config, not optional.** Configure them in the provider
dashboards before the forms go live in Production.

## 1. Hard provider-side ceilings (the volume cap)

**Transactional-email provider** (contact form → `CONTACT_EMAIL_API_*`):

- **Monthly send/spend cap** — a hard account-level ceiling that stops sends
  (or spend) for the billing period once hit. Set it to the most the project is
  willing to pay in a worst-case abuse month. This bounds the blast radius of
  cost even if every other layer is bypassed.
- **Per-window rate cap** — a sending rate limit (per-minute/per-hour) so a
  burst is throttled at the provider rather than delivered in full.

**Hosted-list provider** (newsletter → `NEWSLETTER_API_*`):

- **Signup rate cap** — a per-window ceiling on new subscribers so a scripted
  loop cannot pollute the list faster than it can be noticed and cleaned.

Set each ceiling deliberately (a number tied to expected legitimate volume),
not to the provider's plan maximum.

## 2. Volume alerting — fire *before* the ceilings

The point of alerting is that abuse is **observed early**, well before the hard
cap turns "gated on observed abuse" into a post-mortem.

- In each provider dashboard, set a usage/volume **alert threshold below the
  hard ceiling** from step 1 (e.g. alert at ~50–70% of the monthly send cap,
  and on any unusual per-hour spike). Route it to the owner's email/notification
  channel.
- The alert is the trigger to consider the escalation in step 3 — it turns the
  deferred "observed abuse" signal into an actionable one instead of a bill.

If a provider lacks native volume alerting, the equivalent signal is a
submission-count metric on the endpoints; keep it a bare count (no email/PII, to
hold R-004).

## 3. Deferred global endpoint cap — specified, dormant

If the provider ceilings and alerting are being tripped by sustained abuse, the
escalation is a coarse **global** endpoint cap. It is already designed and
written so it can be turned on fast, not designed under fire:

- Code: `site/lib/forms/global-rate-cap.ts` (`allowGlobalSubmission`).
- It is **dormant** — nothing in the request path calls it, and
  `GLOBAL_SUBMISSION_CAP_ENABLED` defaults off (R-016: specified, not enabled).
- It keys on **no client identifier** — a single global counter for the whole
  endpoint, taking no argument. It is deliberately *not* the per-client
  PII-keyed store D-017 removed (that would reintroduce R-010/R-011).

**To turn it on** (only when abuse is observed, per D-017's deferral):

1. Set `GLOBAL_SUBMISSION_CAP_ENABLED=1` in the Vercel Production environment.
2. In `screenSubmission` (`site/lib/forms/handlers.ts`), add as the first check,
   before the honeypot:

   ```ts
   if (GLOBAL_CAP_ENABLED && !allowGlobalSubmission()) {
     return { ok: false, result: { status: 429, json: { error: 'Too many submissions. Please try again shortly.' } } };
   }
   ```

3. Tune `MAX_PER_WINDOW` / `WINDOW_MS` in `global-rate-cap.ts` to the observed
   abuse profile. Note the serverless per-instance caveat documented in that
   file: the precise ceiling remains the provider-side cap in step 1.
