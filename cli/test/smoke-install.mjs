#!/usr/bin/env node
// Installer smoke test (T-024, R-010): run `treenail install` against a
// throwaway home directory and verify the ~/.treenail runtime and the provider
// skill dirs land where they should. Cross-platform by construction — CI
// runs it on ubuntu, macos, and windows runners.
//
// Usage: node cli/test/smoke-install.mjs [path/to/treenail.js]
// The optional arg lets the release gate point it at the bin inside an
// installed (packed-tarball) copy of the package instead of the checkout.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const bin = path.resolve(
  process.argv[2] || path.join(here, '..', 'bin', 'treenail.js')
);

// Same resolution the CLI itself uses: dist/ ships next to the package's
// bin (published layout) or at the repo root (checkout layout).
function distRoot() {
  for (const candidate of [
    path.join(path.dirname(bin), '..', 'dist'),
    path.join(path.dirname(bin), '..', '..', 'dist'),
  ]) {
    if (fs.existsSync(path.join(candidate, 'treenail-home', 'VERSION'))) {
      return candidate;
    }
  }
  throw new Error(`no built dist/ found near ${bin}`);
}

const failures = [];
function check(ok, what) {
  console.log(`${ok ? 'ok' : 'FAIL'}: ${what}`);
  if (!ok) failures.push(what);
}

const dist = distRoot();
const expectedSkills = fs
  .readdirSync(path.join(dist, 'claude'), { withFileTypes: true })
  .filter((e) => e.isDirectory())
  .map((e) => e.name)
  .sort();

const fakeHome = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-smoke-'));
try {
  // Make exactly one provider (Claude Code) "present" via its config dir;
  // PATH detection is irrelevant inside the fake home.
  fs.mkdirSync(path.join(fakeHome, '.claude'), { recursive: true });

  const env = { ...process.env, HOME: fakeHome, USERPROFILE: fakeHome };
  delete env.TREENAIL_HOME; // must default to <home>/.treenail

  const r = spawnSync(process.execPath, [bin, 'install'], {
    env,
    encoding: 'utf8',
  });
  process.stdout.write(r.stdout || '');
  process.stderr.write(r.stderr || '');
  check(r.status === 0, `install exits 0 (got ${r.status})`);

  const treenailHome = path.join(fakeHome, '.treenail');
  const version = fs.existsSync(path.join(treenailHome, 'VERSION'))
    ? fs.readFileSync(path.join(treenailHome, 'VERSION'), 'utf8').trim()
    : '';
  check(version.length > 0, `~/.treenail/VERSION provisioned (got '${version}')`);
  for (const asset of ['scripts', 'conventions-spec.md']) {
    check(
      fs.existsSync(path.join(treenailHome, asset)),
      `~/.treenail/${asset} provisioned`
    );
  }

  const skillsDir = path.join(fakeHome, '.claude', 'skills');
  for (const name of expectedSkills) {
    check(
      fs.existsSync(path.join(skillsDir, name, 'SKILL.md')),
      `claude skill installed: ${name}/SKILL.md`
    );
  }

  const extras = fs.existsSync(skillsDir)
    ? fs.readdirSync(skillsDir).filter((n) => !expectedSkills.includes(n))
    : [];
  check(
    extras.length === 0,
    `no unexpected entries in claude skills dir (got: ${extras.join(', ') || 'none'})`
  );
} finally {
  fs.rmSync(fakeHome, { recursive: true, force: true });
}

if (failures.length) {
  console.error(`\nsmoke-install: ${failures.length} check(s) failed`);
  process.exit(1);
}
console.log(`\nsmoke-install: all checks passed (${expectedSkills.length} skills)`);
