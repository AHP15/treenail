// Framework-agnostic endpoint cores for the forms (D-006). The Next route
// handlers under app/api/*/route.ts are thin adapters over these; keeping
// the logic here (with relative imports, no next/server) makes it unit
// testable under the node test runner and keeps the trust-boundary logic
// in one place.
//
// Seams: honeypot + Turnstile verification (T-013) wraps ahead of
// validation here; the ProviderConfigError branch becomes a preview/dev
// sandbox no-op under T-014.

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
} from './providers.ts';

export interface HandlerResult {
  status: number;
  json: { ok: true } | { error: string } | { errors: FieldErrors };
}

const CONFIG_ERROR = (what: string): HandlerResult => ({
  status: 500,
  json: { error: `${what} is not configured.` },
});
const DELIVERY_ERROR = (msg: string): HandlerResult => ({
  status: 502,
  json: { error: msg },
});

export async function handleContact(body: unknown): Promise<HandlerResult> {
  const result = validateContact(body);
  if (!result.ok) return { status: 400, json: { errors: result.errors } };

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

export async function handleNewsletter(body: unknown): Promise<HandlerResult> {
  const result = validateNewsletter(body);
  if (!result.ok) return { status: 400, json: { errors: result.errors } };

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
