'use client';

import { useState } from 'react';
import { TurnstileWidget, type TurnstileStatus } from './turnstile-widget';
import { newsletterFallback } from '@/lib/forms/fallback-config';

type Status = 'idle' | 'submitting' | 'success' | 'error';

export function NewsletterForm() {
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');
  // R-013 / T-021: gate submit on the Turnstile widget's state and surface a
  // non-Turnstile fallback if it is blocked.
  const [turnstile, setTurnstile] = useState<TurnstileStatus>('loading');
  const fallback = newsletterFallback();

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus('submitting');
    setMessage('');

    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());

    try {
      const res = await fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(data),
      });
      const json = await res.json().catch(() => ({}));
      if (res.ok) {
        setStatus('success');
        setMessage('You’re subscribed — thanks!');
        form.reset();
        return;
      }
      setStatus('error');
      setMessage(json.errors?.email ?? json.error ?? 'Please try again.');
    } catch {
      setStatus('error');
      setMessage('Network error. Please try again.');
    }
  }

  return (
    <form onSubmit={onSubmit} noValidate aria-describedby="newsletter-status">
      {/* Honeypot: hidden from humans (and AT), tempting to bots. A filled
          value is silently dropped server-side. */}
      <span aria-hidden="true" style={{ position: 'absolute', left: '-9999px' }}>
        <label htmlFor="newsletter-company">Company</label>
        <input
          id="newsletter-company"
          name="company"
          type="text"
          tabIndex={-1}
          autoComplete="off"
        />
      </span>
      <label htmlFor="newsletter-email">Email</label>{' '}
      <input
        id="newsletter-email"
        name="email"
        type="email"
        required
        maxLength={320}
        placeholder="you@example.com"
      />{' '}
      <TurnstileWidget onStatusChange={setTurnstile} />{' '}
      <button
        type="submit"
        disabled={status === 'submitting' || turnstile !== 'ready'}
        aria-describedby="newsletter-turnstile-note"
      >
        {status === 'submitting' ? 'Subscribing…' : 'Subscribe'}
      </button>
      {/* Explain a disabled submit, and never dead-end a blocked-widget user
          (R-013 / T-021). */}
      <span id="newsletter-turnstile-note" role="status" aria-live="polite">
        {turnstile === 'loading' && ' Checking your browser…'}
        {turnstile === 'unavailable' && (
          <>
            {' '}
            Human verification couldn’t load (often an ad or privacy blocker).
            You can still <a href={fallback.href}>{fallback.label}</a>.
          </>
        )}
      </span>
      <span id="newsletter-status" role="status" aria-live="polite">
        {' '}
        {message}
      </span>
    </form>
  );
}
