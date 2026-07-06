'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

// Small theme switch for the bespoke landing (D-015 dual theme). The docs
// shell has its own switch; this proves both themes on the marketing side.
export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const isDark = resolvedTheme === 'dark';

  return (
    <button
      type="button"
      aria-label={mounted ? `Switch to ${isDark ? 'light' : 'dark'} theme` : 'Toggle theme'}
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="tn-ticks"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.72rem',
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        color: 'var(--tn-muted)',
        background: 'var(--tn-surface)',
        border: '1px solid var(--tn-border)',
        borderRadius: '2px',
        padding: '0.4rem 0.7rem',
        cursor: 'pointer',
      }}
    >
      <span
        aria-hidden
        style={{
          width: '0.5rem',
          height: '0.5rem',
          borderRadius: '50%',
          background: 'var(--tn-accent)',
          boxShadow: '0 0 0 3px var(--tn-accent-wash)',
        }}
      />
      {mounted ? (isDark ? 'dark' : 'light') : 'theme'}
    </button>
  );
}
