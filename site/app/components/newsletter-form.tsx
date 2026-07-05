'use client';

import { useState } from 'react';

type Status = 'idle' | 'submitting' | 'success' | 'error';

export function NewsletterForm() {
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');

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
      <label htmlFor="newsletter-email">Email</label>{' '}
      <input
        id="newsletter-email"
        name="email"
        type="email"
        required
        maxLength={320}
        placeholder="you@example.com"
      />{' '}
      <button type="submit" disabled={status === 'submitting'}>
        {status === 'submitting' ? 'Subscribing…' : 'Subscribe'}
      </button>
      <span id="newsletter-status" role="status" aria-live="polite">
        {' '}
        {message}
      </span>
    </form>
  );
}
