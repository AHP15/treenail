// Form validation + endpoint handoff tests (T-012, D-006).
// Run: node --test site/test/forms.test.mjs  (Node strips the imported TS)
//
// These assert the two things D-006 makes load-bearing: input is validated
// before handoff, and a valid submission hands off to the configured
// provider with the right shape — with NO own datastore in the path (the
// only outbound call is the stubbed provider fetch).

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFile } from 'node:fs/promises';

import {
  validateContact,
  validateNewsletter,
  validateEmail,
} from '../lib/forms/validation.ts';
import {
  handleContact,
  handleNewsletter,
  HONEYPOT_FIELD,
  TURNSTILE_TOKEN_FIELD,
} from '../lib/forms/handlers.ts';
import { verifyTurnstileToken } from '../lib/forms/turnstile.ts';
import {
  allowGlobalSubmission,
  __resetGlobalCap,
  GLOBAL_CAP_ENABLED,
  MAX_PER_WINDOW,
  WINDOW_MS,
} from '../lib/forms/global-rate-cap.ts';

const realFetch = globalThis.fetch;

// Injected Turnstile verifiers so handler tests exercise screening without a
// network or any client identifier (T-013). PASS/FAIL stand in for a
// verified / unverifiable token.
const PASS = { verifyToken: async () => true };
const FAIL = { verifyToken: async () => false };

function stubFetch() {
  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init, body: init?.body ? JSON.parse(init.body) : null });
    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  };
  return {
    calls,
    restore() {
      globalThis.fetch = realFetch;
    },
  };
}

const CONTACT_ENV = {
  CONTACT_EMAIL_API_URL: 'https://provider.test/send',
  CONTACT_EMAIL_API_KEY: 'test-key',
  CONTACT_TO_ADDRESS: 'owner@treenail.test',
  CONTACT_FROM_ADDRESS: 'noreply@treenail.test',
};
const NEWSLETTER_ENV = {
  NEWSLETTER_API_URL: 'https://list.test/subscribe',
  NEWSLETTER_API_KEY: 'test-key',
  NEWSLETTER_LIST_ID: 'list_123',
};

function withEnv(env, fn) {
  const saved = {};
  for (const [k, v] of Object.entries(env)) {
    saved[k] = process.env[k];
    process.env[k] = v;
  }
  return (async () => {
    try {
      return await fn();
    } finally {
      for (const k of Object.keys(env)) {
        if (saved[k] === undefined) delete process.env[k];
        else process.env[k] = saved[k];
      }
    }
  })();
}

test('validateEmail rejects malformed and over-long addresses', () => {
  assert.equal(validateEmail('nope').ok, false);
  assert.equal(validateEmail('').ok, false);
  assert.equal(validateEmail('a@b.co').ok, true);
  assert.equal(validateEmail('x'.repeat(320) + '@b.co').ok, false);
});

test('validateContact requires all fields', () => {
  assert.equal(validateContact({ email: 'a@b.co', message: 'hi' }).ok, false);
  const good = validateContact({ name: 'Ada', email: 'a@b.co', message: 'hi' });
  assert.equal(good.ok, true);
  assert.deepEqual(good.value, { name: 'Ada', email: 'a@b.co', message: 'hi' });
});

test('validateNewsletter requires a valid email', () => {
  assert.equal(validateNewsletter({}).ok, false);
  assert.equal(validateNewsletter({ email: 'a@b.co' }).ok, true);
});

test('contact handler rejects invalid input with 400 and no handoff', async () => {
  const stub = stubFetch();
  try {
    const res = await handleContact(
      { name: '', email: 'bad', message: '' },
      PASS
    );
    assert.equal(res.status, 400);
    assert.equal(stub.calls.length, 0, 'no provider call on invalid input');
  } finally {
    stub.restore();
  }
});

test('contact handler hands off a valid message to the provider', async () => {
  const stub = stubFetch();
  try {
    await withEnv(CONTACT_ENV, async () => {
      const res = await handleContact(
        {
          name: 'Ada',
          email: 'ada@dev.test',
          message: 'Hello',
        },
        PASS
      );
      assert.equal(res.status, 200);
      assert.deepEqual(res.json, { ok: true });
    });
    assert.equal(stub.calls.length, 1, 'exactly one outbound call: the provider');
    assert.equal(stub.calls[0].url, CONTACT_ENV.CONTACT_EMAIL_API_URL);
    assert.equal(stub.calls[0].body.to, CONTACT_ENV.CONTACT_TO_ADDRESS);
    assert.equal(stub.calls[0].body.reply_to, 'ada@dev.test');
  } finally {
    stub.restore();
  }
});

// --- T-014: preview/dev sandbox fail-safe (R-008) ---

test('preview/dev sandbox: unconfigured + non-production short-circuits to a no-op with no provider call and no verify', async () => {
  const stub = stubFetch();
  let verifyCalled = false;
  const deps = {
    verifyToken: async () => {
      verifyCalled = true;
      return true;
    },
  };
  // No provider env and not production => sandbox. Ensure VERCEL_ENV is not
  // 'production' for this case.
  const savedVercel = process.env.VERCEL_ENV;
  delete process.env.VERCEL_ENV;
  try {
    const res = await handleContact(
      { name: 'Ada', email: 'ada@dev.test', message: 'Hello' },
      deps
    );
    assert.equal(res.status, 200, 'sandbox returns a success no-op');
    assert.deepEqual(res.json, { ok: true });
    assert.equal(stub.calls.length, 0, 'no real provider write on preview/dev');
    assert.equal(verifyCalled, false, 'sandbox skips Turnstile (secret is prod-only)');
  } finally {
    if (savedVercel !== undefined) process.env.VERCEL_ENV = savedVercel;
    stub.restore();
  }
});

test('sandbox still validates: invalid input is a 400 with no provider call', async () => {
  const stub = stubFetch();
  const savedVercel = process.env.VERCEL_ENV;
  delete process.env.VERCEL_ENV;
  try {
    const res = await handleContact({ name: '', email: 'bad', message: '' }, PASS);
    assert.equal(res.status, 400, 'validation runs even in sandbox');
    assert.equal(stub.calls.length, 0);
  } finally {
    if (savedVercel !== undefined) process.env.VERCEL_ENV = savedVercel;
    stub.restore();
  }
});

test('production + unconfigured is a loud 500 misconfiguration, never a silent sandbox', async () => {
  const stub = stubFetch();
  try {
    // Production but provider keys absent: must NOT fail open to a sandbox
    // that silently drops the submission (R-008).
    await withEnv({ VERCEL_ENV: 'production' }, async () => {
      const res = await handleContact(
        { name: 'Ada', email: 'ada@dev.test', message: 'Hello' },
        PASS
      );
      assert.equal(res.status, 500, 'loud misconfiguration in production');
    });
    assert.equal(stub.calls.length, 0, 'no send attempted');
  } finally {
    stub.restore();
  }
});

test('newsletter preview/dev sandbox: unconfigured + non-production is a no-op with no list write', async () => {
  const stub = stubFetch();
  const savedVercel = process.env.VERCEL_ENV;
  delete process.env.VERCEL_ENV;
  try {
    const res = await handleNewsletter({ email: 'ada@dev.test' }, PASS);
    assert.equal(res.status, 200);
    assert.equal(stub.calls.length, 0, 'no real list write on preview/dev');
  } finally {
    if (savedVercel !== undefined) process.env.VERCEL_ENV = savedVercel;
    stub.restore();
  }
});

test('newsletter handler hands off a valid email to the list provider', async () => {
  const stub = stubFetch();
  try {
    await withEnv(NEWSLETTER_ENV, async () => {
      const res = await handleNewsletter({ email: 'ada@dev.test' }, PASS);
      assert.equal(res.status, 200);
    });
    assert.equal(stub.calls.length, 1);
    assert.equal(stub.calls[0].url, NEWSLETTER_ENV.NEWSLETTER_API_URL);
    assert.equal(stub.calls[0].body.email, 'ada@dev.test');
    assert.equal(stub.calls[0].body.list_id, NEWSLETTER_ENV.NEWSLETTER_LIST_ID);
  } finally {
    stub.restore();
  }
});

// --- T-013: honeypot + server-side Turnstile screening (D-017) ---

test('a filled honeypot is silently dropped with no handoff and no verify', async () => {
  const stub = stubFetch();
  let verifyCalled = false;
  const deps = {
    verifyToken: async () => {
      verifyCalled = true;
      return true;
    },
  };
  try {
    await withEnv(CONTACT_ENV, async () => {
      const res = await handleContact(
        {
          name: 'Ada',
          email: 'ada@dev.test',
          message: 'Hello',
          [HONEYPOT_FIELD]: 'ACME Corp',
        },
        deps
      );
      // Success shape (no signal to the bot) but never handed off.
      assert.equal(res.status, 200);
      assert.deepEqual(res.json, { ok: true });
    });
    assert.equal(stub.calls.length, 0, 'honeypot submission never reaches provider');
    assert.equal(verifyCalled, false, 'honeypot short-circuits before verify');
  } finally {
    stub.restore();
  }
});

test('an unverifiable Turnstile token is rejected fail-closed with no handoff', async () => {
  const stub = stubFetch();
  try {
    await withEnv(CONTACT_ENV, async () => {
      const res = await handleContact(
        {
          name: 'Ada',
          email: 'ada@dev.test',
          message: 'Hello',
          [TURNSTILE_TOKEN_FIELD]: 'bad-token',
        },
        FAIL
      );
      assert.equal(res.status, 403, 'fail-closed rejection (R-017)');
      assert.match(res.json.error, /verif/i, 'user-facing retryable error');
    });
    assert.equal(stub.calls.length, 0, 'unverified submission never reaches provider');
  } finally {
    stub.restore();
  }
});

test('newsletter screening also fails closed on an unverifiable token', async () => {
  const stub = stubFetch();
  try {
    await withEnv(NEWSLETTER_ENV, async () => {
      const res = await handleNewsletter({ email: 'ada@dev.test' }, FAIL);
      assert.equal(res.status, 403);
    });
    assert.equal(stub.calls.length, 0);
  } finally {
    stub.restore();
  }
});

// --- T-022: deferred global endpoint cap, specified but dormant (R-016) ---

test('the global cap ships dormant — disabled and unwired', async () => {
  // R-016: the escalation is specified, NOT enabled. Defaults off, and no
  // handler imports it into the request path.
  assert.equal(GLOBAL_CAP_ENABLED, false, 'global cap defaults off');
  const handlers = await readFile(
    new URL('../lib/forms/handlers.ts', import.meta.url),
    'utf8'
  );
  assert.doesNotMatch(
    handlers,
    /global-rate-cap|allowGlobalSubmission/,
    'screenSubmission must not call the dormant cap'
  );
});

test('the global cap allows up to MAX_PER_WINDOW then blocks, keying on no client identifier', () => {
  __resetGlobalCap();
  // It takes NO client identifier (R-010/R-011 guard) — a single global window.
  assert.equal(allowGlobalSubmission.length, 0, 'requires no argument — no client identifier can be passed');
  const t = 1_000_000;
  for (let i = 0; i < MAX_PER_WINDOW; i++) {
    assert.equal(allowGlobalSubmission(t), true, `submission ${i} under the ceiling`);
  }
  assert.equal(allowGlobalSubmission(t), false, 'ceiling exceeded within the window');
});

test('the global cap resets after the window elapses', () => {
  __resetGlobalCap();
  const t = 2_000_000;
  for (let i = 0; i < MAX_PER_WINDOW; i++) allowGlobalSubmission(t);
  assert.equal(allowGlobalSubmission(t), false, 'blocked at end of window');
  assert.equal(allowGlobalSubmission(t + WINDOW_MS), true, 'a fresh window allows again');
});

test('verifyTurnstileToken fails closed without a secret or a token', async () => {
  const stub = stubFetch(); // must never be reached
  try {
    // No TURNSTILE_SECRET_KEY configured -> misconfiguration fails closed.
    const savedSecret = process.env.TURNSTILE_SECRET_KEY;
    delete process.env.TURNSTILE_SECRET_KEY;
    try {
      assert.equal(await verifyTurnstileToken('some-token'), false);
    } finally {
      if (savedSecret !== undefined) process.env.TURNSTILE_SECRET_KEY = savedSecret;
    }
    // Secret present but no/blank token -> fails closed before any network.
    await withEnv({ TURNSTILE_SECRET_KEY: 'secret' }, async () => {
      assert.equal(await verifyTurnstileToken(undefined), false);
      assert.equal(await verifyTurnstileToken(''), false);
    });
    assert.equal(stub.calls.length, 0, 'no siteverify call when failing closed early');
  } finally {
    stub.restore();
  }
});
