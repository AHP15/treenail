// Provider handoff — the "hand off" half of D-006. All submissions are
// offloaded to managed third-party providers; the site keeps no PII and
// no datastore. Vendor selection is a deliberate follow-up (D-006), so
// this is a configurable HTTP seam driven entirely by env, not a
// hard-coded vendor SDK: point CONTACT_/NEWSLETTER_ env at whichever
// transactional-email and hosted-list provider is chosen.
//
// Seam notes for later tasks:
//  - T-014 turns "keys absent" into a safe no-op sandbox response so
//    preview/dev deploys never hit real providers. Until then a missing
//    key is a hard configuration error (never a silent real send).
//  - No request/response bodies are logged here; email + message content
//    must not leak into platform logs beyond what the platform itself
//    records (tracked as R-004 by T-015).

import type { ContactPayload } from './validation.ts';

export class ProviderConfigError extends Error {}
export class ProviderDeliveryError extends Error {}

function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new ProviderConfigError(`Missing required env var: ${name}`);
  return v;
}

// The env vars each provider needs — single-sourced so the "is it configured?"
// checks (T-014) can't drift from the requireEnv() calls below.
const CONTACT_ENV_KEYS = [
  'CONTACT_EMAIL_API_URL',
  'CONTACT_EMAIL_API_KEY',
  'CONTACT_TO_ADDRESS',
  'CONTACT_FROM_ADDRESS',
] as const;
const NEWSLETTER_ENV_KEYS = [
  'NEWSLETTER_API_URL',
  'NEWSLETTER_API_KEY',
  'NEWSLETTER_LIST_ID',
] as const;

function allPresent(keys: readonly string[]): boolean {
  return keys.every((k) => Boolean(process.env[k]));
}

// R-008 / T-014: the secrets are scoped to the Vercel Production environment
// only, so on preview/dev deploys these return false and the endpoints enter a
// sandbox no-op instead of hitting real providers. Production, where the keys
// live, returns true and does a real send.
export function contactConfigured(): boolean {
  return allPresent(CONTACT_ENV_KEYS);
}
export function newsletterConfigured(): boolean {
  return allPresent(NEWSLETTER_ENV_KEYS);
}

// True only on a real Vercel Production deploy. Used so that a missing key in
// Production is a LOUD misconfiguration (never a silent sandbox that would drop
// real submissions and fail open), while the same absence on preview/dev is the
// expected sandbox trigger.
export function isProductionEnv(): boolean {
  return process.env.VERCEL_ENV === 'production';
}

// Contact-form messages are delivered as email to the owner's inbox via a
// transactional-email API (D-006). Generic bearer-auth JSON POST.
export async function deliverContactEmail(payload: ContactPayload): Promise<void> {
  const url = requireEnv('CONTACT_EMAIL_API_URL');
  const key = requireEnv('CONTACT_EMAIL_API_KEY');
  const to = requireEnv('CONTACT_TO_ADDRESS');
  const from = requireEnv('CONTACT_FROM_ADDRESS');

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({
      from,
      to,
      reply_to: payload.email,
      subject: `Treenail contact form — ${payload.name}`,
      text: `From: ${payload.name} <${payload.email}>\n\n${payload.message}`,
    }),
  });

  if (!res.ok) {
    throw new ProviderDeliveryError(
      `Transactional-email provider responded ${res.status}`
    );
  }
}

// Newsletter signups go to a hosted list provider (D-006). Generic
// bearer-auth JSON POST of the subscriber email to a configured list.
export async function subscribeToNewsletter(email: string): Promise<void> {
  const url = requireEnv('NEWSLETTER_API_URL');
  const key = requireEnv('NEWSLETTER_API_KEY');
  const listId = requireEnv('NEWSLETTER_LIST_ID');

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({ email, list_id: listId }),
  });

  // Treat an already-subscribed conflict as success — idempotent from the
  // user's perspective, and the provider owns dedupe/state, not us.
  if (!res.ok && res.status !== 409) {
    throw new ProviderDeliveryError(
      `Hosted-list provider responded ${res.status}`
    );
  }
}
