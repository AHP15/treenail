'use client';

import { useState } from 'react';

type Status = 'idle' | 'submitting' | 'success' | 'error';

export function ContactForm() {
  const [status, setStatus] = useState<Status>('idle');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [message, setMessage] = useState('');

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
      <button type="submit" disabled={status === 'submitting'}>
        {status === 'submitting' ? 'Sending…' : 'Send message'}
      </button>
      <p id="contact-status" role="status" aria-live="polite">
        {message}
      </p>
    </form>
  );
}
