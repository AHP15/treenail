// Deferred global endpoint cap (R-016, D-017) — SPECIFIED BUT DORMANT.
//
// This is the "turn-on-fast, not design-under-fire" escalation R-016 asks
// for: the coarse *global* volume ceiling D-017 contemplated "later, gated on
// observed abuse." The real day-one ceiling is provider-side (see
// site/docs/abuse-protection.md); this exists so that when the alerting there
// observes abuse, enabling an endpoint-level cap is a one-line wiring change
// and an env flag — never a design task under fire.
//
// It is DORMANT: nothing imports it into the request path. `screenSubmission`
// in handlers.ts does NOT call it. To turn it on (only when abuse is observed):
//   1. set GLOBAL_CAP_ENABLED via env (below), and
//   2. add, as the first check in screenSubmission (handlers.ts), before the
//      honeypot:
//        if (!allowGlobalSubmission()) return { ok: false, result: CAP_ERROR };
//      where CAP_ERROR is a 429 retryable response.
//
// R-010/R-011 GUARD — why this is not the store D-017 removed:
//   `allowGlobalSubmission()` takes NO argument. It reads no IP, cookie, or
//   any other client identifier, and keys on nothing — it is a single global
//   counter for the whole endpoint. It therefore cannot be a per-client
//   PII-keyed store (that would reintroduce R-010's reversible-hash and
//   R-011's shared-egress over-block failures). The trade-off is deliberate:
//   a global cap throttles *everyone* once the window ceiling is hit, which is
//   acceptable for a break-glass abuse brake but is why it stays dormant
//   behind the provider-side ceiling rather than running day-one.
//
// SERVERLESS CAVEAT: the counter is per-instance in-memory, so across many
// concurrent lambda instances the effective ceiling is (instances ×
// MAX_PER_WINDOW). That is fine for a coarse break-glass brake whose job is to
// blunt a runaway loop, and it keeps us inside D-006/D-017's no-own-store
// posture. A precise global ceiling, if ever needed, is the provider-side cap.

// Dormant switch. Defaults OFF; nothing enables it in this task (R-016: the
// escalation is specified, not enabled). When abuse is observed, set
// GLOBAL_SUBMISSION_CAP_ENABLED=1 in the Production environment.
export const GLOBAL_CAP_ENABLED =
  process.env.GLOBAL_SUBMISSION_CAP_ENABLED === '1';

// Fixed per-window ceiling for the whole endpoint. Deliberately generous — it
// is a runaway/abuse brake, not a per-user quota.
export const WINDOW_MS = 60_000; // 1 minute
export const MAX_PER_WINDOW = 60; // global submissions per window

// The one and only piece of state: a global fixed-window counter. No map, no
// client key — a single window shared by the whole endpoint.
let windowStart = 0;
let count = 0;

// Returns true if a submission is under the global ceiling, false if the
// endpoint has exceeded MAX_PER_WINDOW in the current window. Takes NO client
// identifier by design (see R-010/R-011 guard above). Callers gate on
// GLOBAL_CAP_ENABLED — when dormant this is never invoked.
export function allowGlobalSubmission(now: number = Date.now()): boolean {
  if (now - windowStart >= WINDOW_MS) {
    windowStart = now;
    count = 0;
  }
  count += 1;
  return count <= MAX_PER_WINDOW;
}

// Test-only reset so the dormant cap's window logic can be exercised
// deterministically without leaking state between cases.
export function __resetGlobalCap(): void {
  windowStart = 0;
  count = 0;
}
