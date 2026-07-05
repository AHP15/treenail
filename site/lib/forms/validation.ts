// Pure, dependency-free validation for the form payloads (D-006). The
// site's only responsibility on the trust boundary is "validate → hand
// off"; this module is the validate half and stores nothing.

export type FieldErrors = Record<string, string>;

export type ValidationResult<T> =
  | { ok: true; value: T }
  | { ok: false; errors: FieldErrors };

export interface ContactPayload {
  name: string;
  email: string;
  message: string;
}

export interface NewsletterPayload {
  email: string;
}

// Deliberately conservative: enough to reject obvious garbage without
// pretending to fully validate deliverability (the provider does that).
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const LIMITS = {
  name: 200,
  email: 320, // RFC 5321 max
  message: 5000,
} as const;

function asString(v: unknown): string {
  return typeof v === 'string' ? v.trim() : '';
}

export function validateEmail(raw: unknown): ValidationResult<string> {
  const email = asString(raw);
  if (!email) return { ok: false, errors: { email: 'Email is required.' } };
  if (email.length > LIMITS.email)
    return { ok: false, errors: { email: 'Email is too long.' } };
  if (!EMAIL_RE.test(email))
    return { ok: false, errors: { email: 'Enter a valid email address.' } };
  return { ok: true, value: email };
}

export function validateContact(input: unknown): ValidationResult<ContactPayload> {
  const data = (input ?? {}) as Record<string, unknown>;
  const errors: FieldErrors = {};

  const name = asString(data.name);
  if (!name) errors.name = 'Name is required.';
  else if (name.length > LIMITS.name) errors.name = 'Name is too long.';

  const emailResult = validateEmail(data.email);
  if (!emailResult.ok) Object.assign(errors, emailResult.errors);

  const message = asString(data.message);
  if (!message) errors.message = 'Message is required.';
  else if (message.length > LIMITS.message)
    errors.message = 'Message is too long.';

  if (Object.keys(errors).length > 0) return { ok: false, errors };
  return {
    ok: true,
    value: { name, email: (emailResult as { value: string }).value, message },
  };
}

export function validateNewsletter(
  input: unknown
): ValidationResult<NewsletterPayload> {
  const data = (input ?? {}) as Record<string, unknown>;
  const emailResult = validateEmail(data.email);
  if (!emailResult.ok) return { ok: false, errors: emailResult.errors };
  return { ok: true, value: { email: emailResult.value } };
}
