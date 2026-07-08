// Framework-agnostic endpoint cores for the forms (D-006). The Next route
// handlers under app/api/*/route.ts are thin adapters over these; keeping
// the logic here (with relative imports, no next/server) makes it unit
// testable under the node test runner and keeps the trust-boundary logic
// in one place.
//
// Trust-boundary order on every submission (T-013, D-017):
//   1. screenSubmission — honeypot + server-side Turnstile, ahead of
//      validation, keying/storing NO client identifier.
//   2. validate (validation.ts).
//   3. hand off to the managed provider (providers.ts).
// The Turnstile verifier is injected (default = the real siteverify call) so
// unit tests exercise screening without a network or a client identifier.
// The ProviderConfigError branch becomes a preview/dev sandbox no-op under
// T-014.

import {
  validateContact,
  validateNewsletter,
  type FieldErrors,
} from './validation.ts';
import {
  deliverContactEmail,
  subscribeToNewsletter,
  ProviderConfigError,
  ProviderDeliveryError,
  contactConfigured,
  newsletterConfigured,
  isProductionEnv,
} from './providers.ts';
import { verifyTurnstileToken, type TurnstileVerifier } from './turnstile.ts';

export interface HandlerResult {
  status: number;
  json: { ok: true } | { error: string } | { errors: FieldErrors };
}

// A hidden field no human ever fills; bots that fill every field trip it.
export const HONEYPOT_FIELD = 'company';
// The response token minted by the Turnstile widget (Cloudflare's field name).
export const TURNSTILE_TOKEN_FIELD = 'cf-turnstile-response';

export interface HandlerDeps {
  verifyToken: TurnstileVerifier;
}
const DEFAULT_DEPS: HandlerDeps = { verifyToken: verifyTurnstileToken };

const CONFIG_ERROR = (what: string): HandlerResult => ({
  status: 500,
  json: { error: `${what} is not configured.` },
});
// Preview/dev sandbox no-op (R-008 / T-014): provider secrets are scoped to
// Production only, so on preview/dev deploys the endpoints take this path —
// input is still validated, but NOTHING is handed off to a real provider. The
// success shape keeps the form demoable on a preview without any real
// email/list write.
const SANDBOX_RESULT: HandlerResult = { status: 200, json: { ok: true } };
const DELIVERY_ERROR = (msg: string): HandlerResult => ({
  status: 502,
  json: { error: msg },
});
// Fail-closed rejection for an unverifiable Turnstile token (R-017): a
// user-facing, retryable error. No retry or queue on our side.
const VERIFY_ERROR: HandlerResult = {
  status: 403,
  json: { error: 'Verification failed. Please try again.' },
};

type ScreenResult = { ok: true } | { ok: false; result: HandlerResult };

// Honeypot + server-side Turnstile, ahead of validation. Reads only the
// honeypot field and the opaque Turnstile token from the body — never an IP,
// cookie, or any other client identifier (D-017 / D-006 zero-PII posture).
async function screenSubmission(
  body: unknown,
  verifyToken: TurnstileVerifier
): Promise<ScreenResult> {
  const data = (body ?? {}) as Record<string, unknown>;

  // Honeypot: a filled hidden field means a bot. Silently drop it — return a
  // success shape but never hand off — so the bot gets no signal to adapt.
  const honey = data[HONEYPOT_FIELD];
  if (typeof honey === 'string' && honey.trim() !== '') {
    return { ok: false, result: { status: 200, json: { ok: true } } };
  }

  // Server-side Turnstile: fail-closed on any non-affirmative result (R-017).
  const verified = await verifyToken(data[TURNSTILE_TOKEN_FIELD]);
  if (!verified) return { ok: false, result: VERIFY_ERROR };

  return { ok: true };
}

export async function handleContact(
  body: unknown,
  deps: HandlerDeps = DEFAULT_DEPS
): Promise<HandlerResult> {
  // R-008 / T-014: keys absent = preview/dev sandbox. In Production the keys
  // are present; if they are not, that is a loud misconfiguration, never a
  // silent sandbox that would drop real submissions (no fail-open in prod).
  const sandbox = !contactConfigured();
  if (sandbox && isProductionEnv()) return CONFIG_ERROR('Contact form');

  // Turnstile secret is Production-scoped too, so screening runs only when we
  // are configured for a real send; sandbox skips it (no secret to verify).
  if (!sandbox) {
    const screen = await screenSubmission(body, deps.verifyToken);
    if (!screen.ok) return screen.result;
  }

  const result = validateContact(body);
  if (!result.ok) return { status: 400, json: { errors: result.errors } };

  if (sandbox) return SANDBOX_RESULT; // no real provider write on preview/dev

  try {
    await deliverContactEmail(result.value);
  } catch (err) {
    if (err instanceof ProviderConfigError) return CONFIG_ERROR('Contact form');
    if (err instanceof ProviderDeliveryError)
      return DELIVERY_ERROR(
        'Could not deliver your message. Please try again later.'
      );
    throw err;
  }
  return { status: 200, json: { ok: true } };
}

export async function handleNewsletter(
  body: unknown,
  deps: HandlerDeps = DEFAULT_DEPS
): Promise<HandlerResult> {
  // R-008 / T-014: same preview/dev sandbox posture as handleContact.
  const sandbox = !newsletterConfigured();
  if (sandbox && isProductionEnv()) return CONFIG_ERROR('Newsletter signup');

  if (!sandbox) {
    const screen = await screenSubmission(body, deps.verifyToken);
    if (!screen.ok) return screen.result;
  }

  const result = validateNewsletter(body);
  if (!result.ok) return { status: 400, json: { errors: result.errors } };

  if (sandbox) return SANDBOX_RESULT; // no real list write on preview/dev

  try {
    await subscribeToNewsletter(result.value.email);
  } catch (err) {
    if (err instanceof ProviderConfigError)
      return CONFIG_ERROR('Newsletter signup');
    if (err instanceof ProviderDeliveryError)
      return DELIVERY_ERROR('Could not complete signup. Please try again later.');
    throw err;
  }
  return { status: 200, json: { ok: true } };
}
