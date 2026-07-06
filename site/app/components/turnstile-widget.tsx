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
// R-013's blocked-widget fallback is deliberately NOT here — that is T-021.

const SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js';

interface TurnstileApi {
  render: (el: HTMLElement, opts: Record<string, unknown>) => string;
  remove: (id: string) => void;
}
declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

export function TurnstileWidget() {
  const containerRef = useRef<HTMLDivElement>(null);
  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

  useEffect(() => {
    if (!siteKey) return;
    let widgetId: string | undefined;

    function render() {
      if (widgetId || !window.turnstile || !containerRef.current) return;
      widgetId = window.turnstile.render(containerRef.current, {
        sitekey: siteKey,
        appearance: 'interaction-only', // managed/non-interactive (R-014)
        theme: 'auto', // tracks the dual theme (D-015 / R-014)
        size: 'compact', // most compact preset (R-014)
      });
    }

    if (!document.querySelector(`script[src="${SCRIPT_SRC}"]`)) {
      const script = document.createElement('script');
      script.src = SCRIPT_SRC;
      script.async = true;
      script.defer = true;
      script.addEventListener('load', render);
      document.head.appendChild(script);
    } else {
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

    return () => {
      clearInterval(poll);
      if (widgetId && window.turnstile) window.turnstile.remove(widgetId);
    };
  }, [siteKey]);

  // Contained within the form's own frame (R-014).
  return <div ref={containerRef} className="cf-turnstile-container" />;
}
