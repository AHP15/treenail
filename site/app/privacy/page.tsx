import type { Metadata } from 'next';
import Link from 'next/link';
import { ThemeToggle } from '../components/theme-toggle';

export const metadata: Metadata = {
  title: 'Privacy — Treenail',
  description:
    'What Treenail’s site collects, what it does not store, and why it runs without a cookie consent banner.',
  alternates: { canonical: '/privacy' }, // self-referential (R-007, T-019)
};

const GITHUB_URL = 'https://github.com/AHP15/treenail';
const TURNSTILE_ADDENDUM_URL = 'https://www.cloudflare.com/turnstile-privacy-policy/';
const VERCEL_ANALYTICS_PRIVACY_URL = 'https://vercel.com/docs/analytics/privacy-policy';

// The public privacy disclosure note (T-015, mitigates R-004 + R-015). Its
// job is truthfulness: it must state exactly what the deployed site does, no
// more (the "zero-PII" marketing posture must not outrun the page). The
// "cookieless / no consent banner required" conclusion was verified before
// launch against Vercel Analytics' and Cloudflare Turnstile's actual data
// handling and EU ePrivacy/GDPR guidance — see the Notes on T-015:
//   - Vercel Web Analytics is genuinely cookieless (a per-request hash,
//     discarded within 24h, aggregate only, no stored/associated IP). Used
//     alone it needs no consent banner.
//   - Our Turnstile widget is standalone (appearance interaction-only), NOT
//     proxied behind a Cloudflare WAF zone, with Pre-Clearance left at its
//     default (false). Under Cloudflare's own docs a standalone widget in
//     that configuration sets NO cookie — it mints only a one-time token — so
//     the "cookieless" wording holds. It is conditional on never enabling
//     Pre-Clearance; doing so would issue a cf_clearance cookie and this note
//     (and the consent posture) must be revisited.
//   - Turnstile still sends the visitor's IP + browser signals to Cloudflare
//     on load of any form-bearing page, making Cloudflare a third-party
//     processor. That processing is disclosed below (R-015), with the
//     required reference to the Turnstile Privacy Addendum. No cookie means no
//     ePrivacy consent trigger, so no banner — but the flow is disclosed.

export default function PrivacyPage() {
  return (
    <main className="tn-blueprint-grid">
      <div className="tn-shell">
        <header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            paddingBlock: '1.5rem',
          }}
        >
          <Link href="/" className="tn-brand" style={{ textDecoration: 'none' }}>
            <span className="tn-brand-peg" aria-hidden />
            Treenail
          </Link>
          <nav className="tn-nav">
            <Link href="/docs" style={{ color: 'var(--tn-muted)' }}>
              Docs
            </Link>
            <a href={GITHUB_URL} style={{ color: 'var(--tn-muted)' }} rel="noreferrer">
              GitHub
            </a>
            <Link href="/contact" style={{ color: 'var(--tn-muted)' }}>
              Contact
            </Link>
            <ThemeToggle />
          </nav>
        </header>

        <article className="tn-section" style={{ maxWidth: '44rem' }}>
          <p className="tn-eyebrow">Privacy</p>
          <h1 className="tn-h2">What this site collects — and what it doesn’t.</h1>
          <p className="tn-lead">
            Treenail is a plain-text planning-skills pack; this site exists to
            explain it and to let you reach us. We keep the data footprint
            deliberately small. This note describes exactly what happens when
            you visit or use the forms — no more than the site actually does.
          </p>

          <section style={{ marginTop: '2.5rem' }}>
            <h2 className="tn-h3">Form submissions</h2>
            <p className="tn-body">
              The contact and newsletter forms relay what you type to managed
              third-party providers — a transactional-email service for contact
              messages and a hosted-list service for newsletter sign-ups. We
              store <strong>no submission data in a datastore of our own</strong>:
              your message or email address lives with those providers under
              their terms, not in a Treenail-operated database. We ask only for
              what a reply or a subscription needs.
            </p>
          </section>

          <section style={{ marginTop: '2rem' }}>
            <h2 className="tn-h3">Analytics</h2>
            <p className="tn-body">
              We use{' '}
              <a href={VERCEL_ANALYTICS_PRIVACY_URL} rel="noreferrer">
                Vercel Web Analytics
              </a>
              , which is cookieless. It counts page views without setting a
              cookie and without storing or associating your IP address: a
              visitor is identified only by a short-lived per-request hash that
              is discarded within 24 hours, and only aggregate figures are
              retained. It sets nothing on your device and tracks you across no
              other site.
            </p>
          </section>

          <section style={{ marginTop: '2rem' }}>
            <h2 className="tn-h3">Spam protection (Cloudflare Turnstile)</h2>
            <p className="tn-body">
              Pages that carry a form (this site’s contact and newsletter
              pages) load{' '}
              <a href="https://www.cloudflare.com/products/turnstile/" rel="noreferrer">
                Cloudflare Turnstile
              </a>{' '}
              to tell humans from bots without a puzzle. Turnstile is a
              third-party script, which makes{' '}
              <strong>Cloudflare a data processor</strong> for those pages: on
              load, it sends the visitor’s IP address and browser signals (such
              as user-agent and device/browser characteristics) to Cloudflare so
              it can score the request. It runs only where a form is present.
            </p>
            <p className="tn-body">
              In our configuration Turnstile <strong>sets no cookie</strong> — it
              returns a one-time verification token, nothing more. Your use of
              Turnstile here is also subject to the{' '}
              <a href={TURNSTILE_ADDENDUM_URL} rel="noreferrer">
                Cloudflare Turnstile Privacy Addendum
              </a>
              .
            </p>
          </section>

          <section style={{ marginTop: '2rem' }}>
            <h2 className="tn-h3">Cookies and consent</h2>
            <p className="tn-body">
              This site sets <strong>no cookies</strong> and shows no consent
              banner. Both of the tools above are cookieless in the way we run
              them — cookieless analytics and a standalone Turnstile widget with
              pre-clearance disabled — so there is no non-essential cookie for
              you to consent to. We still disclose the Cloudflare and analytics
              data flows above rather than hide them behind their absence of a
              cookie. If that ever changes — for example if Turnstile were
              reconfigured to issue a clearance cookie — this note and the
              consent posture would be updated first.
            </p>
          </section>

          <section style={{ marginTop: '2rem' }}>
            <h2 className="tn-h3">Contact</h2>
            <p className="tn-body">
              Questions about any of this? Reach us via the{' '}
              <Link href="/contact">contact form</Link> or on{' '}
              <a href={GITHUB_URL} rel="noreferrer">
                GitHub
              </a>
              .
            </p>
          </section>
        </article>

        <footer
          style={{
            paddingBlock: '1.5rem',
            marginTop: 'clamp(2rem, 6vw, 4rem)',
            borderTop: '1px solid var(--tn-border)',
            display: 'flex',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.5rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            letterSpacing: '0.03em',
            color: 'var(--tn-muted)',
          }}
        >
          <span>TREENAIL · PRIVACY</span>
          <Link href="/" style={{ color: 'var(--tn-muted)' }}>
            ← Home
          </Link>
        </footer>
      </div>
    </main>
  );
}
