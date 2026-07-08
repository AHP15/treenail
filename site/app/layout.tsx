import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { RootProvider } from 'fumadocs-ui/provider/next';
import { Analytics } from '@vercel/analytics/next';
import { fontSans, fontMono } from './fonts';
import { SITE_URL } from '@/lib/site-url';
import './globals.css';

export const metadata: Metadata = {
  // metadataBase pins every canonical/OG URL to the single origin constant
  // (D-013, R-007). T-020 repoints the whole site by editing SITE_URL alone.
  metadataBase: new URL(SITE_URL),
  title: 'Treenail',
  description:
    'Treenail — a planning-skills pack that gives your coding agent a durable decision, risk, and task record.',
  // Self-referential canonical for the landing page so SEO equity isn't
  // fragmented across the subdomain and the future custom domain (R-007).
  // Child routes that export metadata set their own canonical below.
  alternates: { canonical: '/' },
  openGraph: {
    title: 'Treenail',
    description:
      'Treenail — a planning-skills pack that gives your coding agent a durable decision, risk, and task record.',
    url: '/',
    siteName: 'Treenail',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // English-only for v1 (D-015): a single `lang="en"` root with no i18n
    // routing/scaffolding. Localization is a cheap later revisit.
    <html
      lang="en"
      suppressHydrationWarning
      className={`${fontSans.variable} ${fontMono.variable}`}
    >
      <body>
        {/* RootProvider powers Fumadocs' search, theme, and sidebar state.
            The bespoke landing route renders inside it but styles itself. */}
        <RootProvider>{children}</RootProvider>
        {/* Cookieless Vercel Analytics (D-015) — no consent banner needed.
            That claim was verified before launch (T-015) against Vercel
            Analytics' and Turnstile's actual data handling; the disclosure
            lives at /privacy (app/privacy/page.tsx). */}
        <Analytics />
      </body>
    </html>
  );
}
