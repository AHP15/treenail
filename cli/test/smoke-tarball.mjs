#!/usr/bin/env node
// Clean-environment tarball smoke (T-034, R-017): pack the CLI, install
// the tarball into a temp project with no repo checkout anywhere near it,
// and run the full installer smoke against the *installed* bin. This is
// the one environment where a missing bundled dist/ actually fails —
// distRoot() cannot fall back to the repo's dist/ here.
//
// Usage: node cli/test/smoke-tarball.mjs

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const cliRoot = path.join(here, '..');
const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';

function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, {
    encoding: 'utf8',
    shell: process.platform === 'win32',
    ...opts,
  });
  if (r.status !== 0) {
    process.stdout.write(r.stdout || '');
    process.stderr.write(r.stderr || '');
    console.error(`smoke-tarball: \`${cmd} ${args.join(' ')}\` exited ${r.status}`);
    process.exit(1);
  }
  return r;
}

const work = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-tarball-'));
try {
  console.log('packing treenail...');
  run(npm, ['pack', '--pack-destination', work], { cwd: cliRoot });
  const tgz = fs.readdirSync(work).filter((n) => n.endsWith('.tgz'));
  if (tgz.length !== 1) {
    console.error(`smoke-tarball: expected one packed .tgz, found ${tgz.length}`);
    process.exit(1);
  }
  const tarball = path.join(work, tgz[0]);

  // R-001: the site (D-004 puts it under repo-root site/) must never enter
  // the product tarball. The package is published from cli/ with a files
  // allowlist, so site/ is already a sibling of the package — this asserts
  // that invariant so a future files/root change fails loud here instead of
  // shipping website bloat to every `npx treenail install` user.
  const list = run('tar', ['-tzf', tarball]);
  const entries = list.stdout
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
    // tarball entries are prefixed `package/`; compare on the repo-relative path.
    .map((l) => l.replace(/^package\//, ''));
  const siteEntries = entries.filter(
    (p) => p === 'site' || p.startsWith('site/')
  );
  if (siteEntries.length > 0) {
    console.error(
      `smoke-tarball: R-001 — ${siteEntries.length} site/** path(s) leaked into the tarball:\n  ` +
        siteEntries.join('\n  ')
    );
    process.exit(1);
  }

  // R-001: size ceiling — a leaked site/ (node_modules, .next, Fumadocs
  // assets) would be megabytes. The current tarball is ~0.13 MB; 1 MiB gives
  // ample room for dist/ growth while still catching website bloat loudly.
  const SIZE_CEILING = 1024 * 1024;
  const size = fs.statSync(tarball).size;
  if (size > SIZE_CEILING) {
    console.error(
      `smoke-tarball: R-001 — tarball is ${size} bytes, over the ${SIZE_CEILING}-byte ceiling`
    );
    process.exit(1);
  }
  console.log(
    `tarball ok: ${entries.length} entries, ${size} bytes, no site/** paths`
  );

  const proj = path.join(work, 'proj');
  fs.mkdirSync(proj);
  console.log('installing the tarball into a clean temp project...');
  run(npm, ['install', '--no-audit', '--no-fund', tarball], { cwd: proj });

  const installedBin = path.join(
    proj, 'node_modules', 'treenail', 'bin', 'treenail.js'
  );
  console.log('running the installer smoke against the installed bin...\n');
  const r = spawnSync(
    process.execPath,
    [path.join(here, 'smoke-install.mjs'), installedBin],
    { stdio: 'inherit' }
  );
  if (r.status !== 0) process.exit(r.status ?? 1);
} finally {
  fs.rmSync(work, { recursive: true, force: true });
}
console.log('\nsmoke-tarball: passed');
