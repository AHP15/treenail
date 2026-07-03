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

const work = fs.mkdtempSync(path.join(os.tmpdir(), 'keel-tarball-'));
try {
  console.log('packing keel-skills...');
  run(npm, ['pack', '--pack-destination', work], { cwd: cliRoot });
  const tgz = fs.readdirSync(work).filter((n) => n.endsWith('.tgz'));
  if (tgz.length !== 1) {
    console.error(`smoke-tarball: expected one packed .tgz, found ${tgz.length}`);
    process.exit(1);
  }
  const tarball = path.join(work, tgz[0]);

  const proj = path.join(work, 'proj');
  fs.mkdirSync(proj);
  console.log('installing the tarball into a clean temp project...');
  run(npm, ['install', '--no-audit', '--no-fund', tarball], { cwd: proj });

  const installedBin = path.join(
    proj, 'node_modules', 'keel-skills', 'bin', 'keel-skills.js'
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
