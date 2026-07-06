// Server-side Cloudflare Turnstile verification (D-017, T-013). Turnstile is
// the day-one bot filter that replaced the IP-keyed rate-limit store D-017
// removed: it resists bots WITHOUT our storing or keying on any client
// identifier, so D-006's zero-PII posture holds. Nothing here reads or
// forwards an IP, cookie, or any other client identifier — only the opaque
// Turnstile response token the widget mints.
//
// R-017 (this call is a hard dependency on the form's critical path):
//   - Bounded timeout: the siteverify request is aborted after
//     VERIFY_TIMEOUT_MS so a slow/hung Cloudflare endpoint cannot hang a
//     submission indefinitely.
//   - Deliberate FAIL-CLOSED: a token that cannot be verified — missing,
//     malformed, rejected, timed out, or unreachable — is treated as a
//     verification failure and the submission is rejected with a retryable
//     error. Fail-open would leak spam to the metered providers exactly when
//     verification is degraded. There is intentionally NO retry or queue.

const SITEVERIFY_URL =
  'https://challenges.cloudflare.com/turnstile/v0/siteverify';

// Short, explicit budget for the request-path dependency (R-017). Kept well
// under a typical serverless function timeout so a Cloudflare stall surfaces
// as a fast, retryable rejection rather than a platform-level timeout.
export const VERIFY_TIMEOUT_MS = 3000;

export interface TurnstileVerifier {
  (token: unknown): Promise<boolean>;
}

// Verify a Turnstile response token against Cloudflare's siteverify endpoint.
// Returns true only on an affirmative success from Cloudflare; every other
// outcome (no secret configured, no/blank token, non-200, success:false,
// timeout, network error) resolves to false — the fail-closed contract.
export const verifyTurnstileToken: TurnstileVerifier = async (token) => {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  // No secret configured is a misconfiguration, not a pass: fail closed.
  if (!secret) return false;
  if (typeof token !== 'string' || token.length === 0) return false;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), VERIFY_TIMEOUT_MS);
  try {
    const body = new URLSearchParams({ secret, response: token });
    const res = await fetch(SITEVERIFY_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body,
      signal: controller.signal,
    });
    if (!res.ok) return false;
    const data = (await res.json()) as { success?: boolean };
    return data.success === true;
  } catch {
    // Timeout (abort) or network failure — fail closed.
    return false;
  } finally {
    clearTimeout(timer);
  }
};
