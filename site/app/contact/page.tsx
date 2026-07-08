import type { Metadata } from 'next';
import Link from 'next/link';
import { ContactForm } from '@/app/components/contact-form';
import { NewsletterForm } from '@/app/components/newsletter-form';

export const metadata: Metadata = {
  title: 'Contact — Treenail',
  description: 'Get in touch or subscribe to updates.',
  alternates: { canonical: '/contact' }, // self-referential (R-007, T-019)
};

// Provisional host for the forms so they are reachable and testable now.
// Final placement/styling belongs to the design system (T-005) and landing
// page (T-007).
export default function ContactPage() {
  return (
    <main style={{ maxWidth: '40rem', margin: '0 auto', padding: '2rem' }}>
      <h1>Contact</h1>
      <ContactForm />

      <hr style={{ margin: '2.5rem 0' }} />

      <h2>Newsletter</h2>
      <p>Occasional updates. No spam.</p>
      <NewsletterForm />

      <p style={{ marginTop: '2.5rem', fontSize: '0.85rem', color: 'var(--tn-muted)' }}>
        These forms use Cloudflare Turnstile for spam protection and store no
        submission data in a datastore of our own. See our{' '}
        <Link href="/privacy">privacy note</Link>.
      </p>
    </main>
  );
}
