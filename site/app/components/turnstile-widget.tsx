'use client';

import { useEffect, useRef } from 'react';

// Cloudflare Turnstile widget (D-017, T-013). Explicitly rendered into a
// container inside the form so the hidden `cf-turnstile-response` token input
// it mints is collected by the form's FormData and posted to the endpoint,
// where it is verified server-side (lib/forms/turnstile.ts).
//
// R-014 (the un-themable Cloudflare chrome must not dilute the D-011 craft
// surface): rendered in appearance `interaction-only` so the widget is
// invisible for the common case and only surfaces when a challenge is
// actually required; theme `auto` tracks the dual light/dark theme (D-015);
// size `compact` is the smallest preset; and it is placed inside the form's
// own visual frame rather than front-and-center.
//
// R-013 / T-021 (blocked-widget fallback): privacy tooling run by the D-008
// audience blocks Cloudflare's script, so the widget must report its state to
// the parent form instead of silently dead-ending the user. It calls
// `onStatusChange`:
//   - 'loading'     — waiting for a token (submit disabled, explained).
//   - 'ready'       — a token was minted, or Turnstile is not in play here
//                     (no site key → preview/dev; server sandboxes per T-014).
//   - 'unavailable' — the script was blocked / failed to load / the challenge
//                     errored; the form surfaces its non-Turnstile fallback.

const SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
// If the widget script has not become usable within this budget, treat it as
// blocked and hand the user the fallback rather than a spinner forever.
const LOAD_TIMEOUT_MS = 8000;

export type TurnstileStatus = 'loading' | 'ready' | 'unavailable';

interface TurnstileApi {
  render: (el: HTMLElement, opts: Record<string, unknown>) => string;
  remove: (id: string) => void;
}
declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

export function TurnstileWidget({
  onStatusChange,
}: {
  onStatusChange?: (status: TurnstileStatus) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

  useEffect(() => {
    // No site key: Turnstile is not configured for this deploy (preview/dev,
    // where secrets are Production-only per T-014 and the server sandboxes).
    // Don't strand the user behind a widget that will never render.
    if (!siteKey) {
      onStatusChange?.('ready');
      return;
    }

    onStatusChange?.('loading');
    let widgetId: string | undefined;
    let settled = false; // ready/unavailable is terminal for this mount
    const done = (status: Exclude<TurnstileStatus, 'loading'>) => {
      if (settled) return;
      settled = true;
      onStatusChange?.(status);
    };

    function render() {
      if (widgetId || !window.turnstile || !containerRef.current) return;
      widgetId = window.turnstile.render(containerRef.current, {
        sitekey: siteKey,
        appearance: 'interaction-only', // managed/non-interactive (R-014)
        theme: 'auto', // tracks the dual theme (D-015 / R-014)
        size: 'compact', // most compact preset (R-014)
        callback: () => done('ready'), // token minted → submit allowed
        'error-callback': () => done('unavailable'), // challenge failed (R-013)
      });
    }

    const existing = document.querySelector(`script[src="${SCRIPT_SRC}"]`);
    if (!existing) {
      const script = document.createElement('script');
      script.src = SCRIPT_SRC;
      script.async = true;
      script.defer = true;
      script.addEventListener('load', render);
      // Script blocked or network error → immediate fallback (R-013).
      script.addEventListener('error', () => done('unavailable'));
      document.head.appendChild(script);
    } else {
      // A sibling form already injected the script (both forms share one).
      // Attach our own error listener so a blocked script fails THIS widget
      // fast too, instead of waiting on the timeout backstop below.
      existing.addEventListener('error', () => done('unavailable'));
      render();
    }
    // The script may already be present but the api not yet ready; poll
    // briefly until it is, then stop.
    const poll = setInterval(() => {
      if (window.turnstile) {
        render();
        clearInterval(poll);
      }
    }, 200);

    // Backstop for a proxy that neither loads nor errors the script: if the
    // widget never even rendered within the budget, fall back. Guarded on
    // "script never became usable" so a legitimately-rendered interactive
    // challenge the user is still solving is NOT misread as blocked — that
    // stays 'loading' until its callback fires.
    const timeout = setTimeout(() => {
      if (!window.turnstile || !widgetId) done('unavailable');
    }, LOAD_TIMEOUT_MS);

    return () => {
      clearInterval(poll);
      clearTimeout(timeout);
      if (widgetId && window.turnstile) window.turnstile.remove(widgetId);
    };
  }, [siteKey, onStatusChange]);

  // Contained within the form's own frame (R-014).
  return <div ref={containerRef} className="cf-turnstile-container" />;
}
