// Form validation + endpoint handoff tests (T-012, D-006).
// Run: node --test site/test/forms.test.mjs  (Node strips the imported TS)
//
// These assert the two things D-006 makes load-bearing: input is validated
// before handoff, and a valid submission hands off to the configured
// provider with the right shape — with NO own datastore in the path (the
// only outbound call is the stubbed provider fetch).

import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  validateContact,
  validateNewsletter,
  validateEmail,
} from '../lib/forms/validation.ts';
import { handleContact, handleNewsletter } from '../lib/forms/handlers.ts';

const realFetch = globalThis.fetch;

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
    const res = await handleContact({ name: '', email: 'bad', message: '' });
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
      const res = await handleContact({
        name: 'Ada',
        email: 'ada@dev.test',
        message: 'Hello',
      });
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

test('contact handler returns 500 when the provider is unconfigured', async () => {
  const stub = stubFetch();
  try {
    const res = await handleContact({
      name: 'Ada',
      email: 'ada@dev.test',
      message: 'Hello',
    });
    assert.equal(res.status, 500);
    assert.equal(stub.calls.length, 0, 'no send attempted without config');
  } finally {
    stub.restore();
  }
});

test('newsletter handler hands off a valid email to the list provider', async () => {
  const stub = stubFetch();
  try {
    await withEnv(NEWSLETTER_ENV, async () => {
      const res = await handleNewsletter({ email: 'ada@dev.test' });
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
