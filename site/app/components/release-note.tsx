import { releaseTrackingNote } from '@/lib/published-version';

// Release-tracking disclosure for install-critical surfaces (R-009, T-017).
// Rendered on the quickstart, install steps, and CLI reference so a first-run
// user is told the docs describe the last published release and that main may
// be ahead — closing R-009's silent first-run mismatch without introducing
// versioned docs (D-014). Single-sourced from lib/published-version.ts so the
// version string lives in exactly one place. Exposed to MDX via
// mdx-components.tsx and used directly on the landing page.
export function ReleaseNote() {
  return (
    <p
      role="note"
      style={{
        margin: '1rem 0',
        padding: '0.6rem 0.85rem',
        borderLeft: '2px solid var(--tn-accent)',
        background: 'var(--tn-accent-wash)',
        borderRadius: '2px',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.78rem',
        lineHeight: 1.5,
        letterSpacing: '0.01em',
        color: 'var(--tn-muted)',
      }}
    >
      {releaseTrackingNote}
    </p>
  );
}
