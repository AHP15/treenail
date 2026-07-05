import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { RootProvider } from 'fumadocs-ui/provider/next';
import { Analytics } from '@vercel/analytics/next';
import { fontSans, fontMono } from './fonts';
import './globals.css';

export const metadata: Metadata = {
  title: 'Treenail',
  description:
    'Treenail — a planning-skills pack that gives your coding agent a durable decision, risk, and task record.',
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
        {/* Cookieless Vercel Analytics (D-015) — no consent banner needed
            (that claim is verified in T-015). */}
        <Analytics />
      </body>
    </html>
  );
}
