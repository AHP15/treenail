// Non-Turnstile fallback paths (R-013 / T-021). When the Cloudflare Turnstile
// widget is blocked by privacy tooling (uBlock / Brave / Privacy Badger /
// NoScript / corporate proxies — exactly the D-008 audience) it never mints a
// token, and D-017 makes server-side verification mandatory, so the form's API
// path is closed to that user. These give them an escape that needs no
// third-party script.
//
// All values are PUBLIC (NEXT_PUBLIC_ / hard-coded repo URL) — never a secret.
// Each degrades to a GitHub path that is always reachable without the widget,
// so the fallback is useful even before the deployment sets its own values.

const GITHUB_URL = 'https://github.com/AHP15/treenail';

export interface Fallback {
  href: string;
  label: string;
}

// Contact fallback: the owner's direct email as a mailto: when configured,
// else a GitHub issue — either way a human the visitor can reach.
export function contactFallback(): Fallback {
  const email = process.env.NEXT_PUBLIC_CONTACT_EMAIL;
  return email
    ? { href: `mailto:${email}`, label: `email ${email}` }
    : { href: `${GITHUB_URL}/issues/new`, label: 'open a GitHub issue' };
}

// Newsletter fallback: the hosted-list provider's own signup URL when
// configured (that page runs the provider's script, not Cloudflare's), else
// watching releases on GitHub.
export function newsletterFallback(): Fallback {
  const url = process.env.NEXT_PUBLIC_NEWSLETTER_SIGNUP_URL;
  return url
    ? { href: url, label: 'subscribe on our signup page' }
    : { href: `${GITHUB_URL}/releases`, label: 'watch releases on GitHub' };
}
