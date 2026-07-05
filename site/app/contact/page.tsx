import type { Metadata } from 'next';
import { ContactForm } from '@/app/components/contact-form';
import { NewsletterForm } from '@/app/components/newsletter-form';

export const metadata: Metadata = {
  title: 'Contact — Treenail',
  description: 'Get in touch or subscribe to updates.',
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
    </main>
  );
}
