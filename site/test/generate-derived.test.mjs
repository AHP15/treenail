// Derived-page generator tests (T-003) and its intra-file drift hardening
// (T-004, R-002). Run: node --test  (Node strips the imported TS/MJS).
//
// The load-bearing assertion of T-004: single-sourcing must degrade to a
// LOUD build failure on intra-file drift, not a silently truncated page.
// These drive that via fixtures — an empty description, a renamed spec
// heading, an empty skills dir — and assert generate() throws.

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { promises as fs } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import {
  parseSkillFrontmatter,
  extractSpecSection,
  generate,
  DerivedDriftError,
} from '../scripts/generate-derived.mjs';

// A minimal spec carrying the three record-schema anchors the generator needs.
const SPEC_OK = `## DECISIONS

### \`D-NNN.md\` fields (in order)

- **Status**: accepted

## RISKS

### \`R-NNN.md\` fields (in order)

- **Severity**: low

## TASKS

### \`T-NNN.md\` fields (in order)

- **Status**: todo
`;

const goodSkill = (name) =>
  `---\nname: ${name}\ndescription: Does ${name} things.\n---\n\nBody prose.`;

async function mkFixture({ skills, spec }) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'gen-derived-'));
  const skillsDir = path.join(root, 'skills');
  await fs.mkdir(skillsDir, { recursive: true });
  for (const [slug, body] of Object.entries(skills)) {
    await fs.mkdir(path.join(skillsDir, slug), { recursive: true });
    await fs.writeFile(path.join(skillsDir, slug, 'SKILL.md'), body);
  }
  const specPath = path.join(root, 'spec.md');
  await fs.writeFile(specPath, spec);
  return { root, skillsDir, specPath, outRoot: path.join(root, 'out') };
}

// --- extraction helpers (T-003) ---

test('parseSkillFrontmatter reads name + description, empty when absent', () => {
  const ok = parseSkillFrontmatter(goodSkill('promote'));
  assert.equal(ok.name, 'promote');
  assert.match(ok.description, /Does promote things/);
  const noDesc = parseSkillFrontmatter('---\nname: x\n---\nbody');
  assert.equal(noDesc.name, 'x');
  assert.equal(noDesc.description, '', 'missing description resolves empty');
  assert.equal(parseSkillFrontmatter('no frontmatter').name, '');
});

test('extractSpecSection returns the section body, empty when the anchor is gone', () => {
  assert.match(extractSpecSection(SPEC_OK, '### `D-NNN.md` fields (in order)'), /Status/);
  assert.equal(
    extractSpecSection(SPEC_OK, '### `Q-NNN.md` fields (in order)'),
    '',
    'absent anchor resolves empty'
  );
});

// --- happy path (T-003) ---

test('generate writes one page per skill + the record-schema pages', async () => {
  const fx = await mkFixture({
    skills: { alpha: goodSkill('alpha'), beta: goodSkill('beta') },
    spec: SPEC_OK,
  });
  const { skills, records } = await generate(fx);
  assert.equal(skills.length, 2);
  assert.equal(records.length, 3);
  const pages = (await fs.readdir(path.join(fx.outRoot, 'skills'))).sort();
  assert.deepEqual(pages, ['alpha.mdx', 'beta.mdx', 'meta.json']);
  assert.ok(
    (await fs.readdir(path.join(fx.outRoot, 'records'))).includes('decisions.mdx')
  );
});

test('generate on the real repo produces the derived tree', async () => {
  const { skills, records } = await generate();
  assert.ok(skills.length >= 1, 'enumerates real skills');
  assert.equal(records.length, 3);
});

// --- fail loud on intra-file drift (T-004, R-002) ---

test('empty frontmatter description fails the build', async () => {
  const fx = await mkFixture({
    skills: { alpha: goodSkill('alpha'), broken: '---\nname: broken\n---\nbody' },
    spec: SPEC_OK,
  });
  await assert.rejects(
    generate(fx),
    (e) => e instanceof DerivedDriftError && /broken.*description/s.test(e.message)
  );
});

test('a renamed / missing spec section anchor fails the build', async () => {
  const specNoRisks = SPEC_OK.replace('### `R-NNN.md` fields (in order)', '### Risk fields, renamed');
  const fx = await mkFixture({ skills: { alpha: goodSkill('alpha') }, spec: specNoRisks });
  await assert.rejects(
    generate(fx),
    (e) => e instanceof DerivedDriftError && /R-NNN\.md.*fields/.test(e.message)
  );
});

test('an empty skills directory fails the build', async () => {
  const fx = await mkFixture({ skills: {}, spec: SPEC_OK });
  await assert.rejects(
    generate(fx),
    (e) => e instanceof DerivedDriftError && /no SKILL\.md/.test(e.message)
  );
});
