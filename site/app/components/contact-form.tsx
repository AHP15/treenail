'use client';

import { useState } from 'react';
import { TurnstileWidget, type TurnstileStatus } from './turnstile-widget';
import { contactFallback } from '@/lib/forms/fallback-config';

type Status = 'idle' | 'submitting' | 'success' | 'error';

export function ContactForm() {
  const [status, setStatus] = useState<Status>('idle');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [message, setMessage] = useState('');
  // R-013 / T-021: gate submit on the Turnstile widget's state and surface a
  // non-Turnstile fallback if it is blocked.
  const [turnstile, setTurnstile] = useState<TurnstileStatus>('loading');
  const fallback = contactFallback();

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus('submitting');
    setErrors({});
    setMessage('');

    const form = e.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(data),
      });
      const json = await res.json().catch(() => ({}));
      if (res.ok) {
        setStatus('success');
        setMessage('Thanks — your message is on its way.');
        form.reset();
        return;
      }
      if (json.errors) setErrors(json.errors);
      setStatus('error');
      setMessage(json.error ?? 'Please correct the errors and try again.');
    } catch {
      setStatus('error');
      setMessage('Network error. Please try again.');
    }
  }

  return (
    <form onSubmit={onSubmit} noValidate aria-describedby="contact-status">
      {/* Honeypot: hidden from humans (and AT), tempting to bots. A filled
          value is silently dropped server-side. */}
      <div aria-hidden="true" style={{ position: 'absolute', left: '-9999px' }}>
        <label htmlFor="contact-company">Company</label>
        <input
          id="contact-company"
          name="company"
          type="text"
          tabIndex={-1}
          autoComplete="off"
        />
      </div>
      <p>
        <label htmlFor="contact-name">Name</label>
        <br />
        <input id="contact-name" name="name" type="text" required maxLength={200} />
        {errors.name && <span role="alert">{errors.name}</span>}
      </p>
      <p>
        <label htmlFor="contact-email">Email</label>
        <br />
        <input id="contact-email" name="email" type="email" required maxLength={320} />
        {errors.email && <span role="alert">{errors.email}</span>}
      </p>
      <p>
        <label htmlFor="contact-message">Message</label>
        <br />
        <textarea id="contact-message" name="message" required maxLength={5000} rows={6} />
        {errors.message && <span role="alert">{errors.message}</span>}
      </p>
      <TurnstileWidget onStatusChange={setTurnstile} />
      <button
        type="submit"
        disabled={status === 'submitting' || turnstile !== 'ready'}
        aria-describedby="contact-turnstile-note"
      >
        {status === 'submitting' ? 'Sending…' : 'Send message'}
      </button>
      {/* Explain a disabled submit, and never dead-end a blocked-widget user
          (R-013 / T-021). */}
      <p id="contact-turnstile-note" role="status" aria-live="polite">
        {turnstile === 'loading' &&
          'Checking your browser before you can send…'}
        {turnstile === 'unavailable' && (
          <>
            Human verification couldn’t load — an ad or privacy blocker is the
            usual cause. You can still{' '}
            <a href={fallback.href}>{fallback.label}</a> instead.
          </>
        )}
      </p>
      <p id="contact-status" role="status" aria-live="polite">
        {message}
      </p>
    </form>
  );
}
