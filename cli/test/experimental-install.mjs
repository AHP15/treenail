#!/usr/bin/env node
// Experimental adapter packaging/install guard (T-058, D-034/D-035): an
// experimental payload present in dist/ must not affect default installs, and
// explicit `--experimental <agent>` installs must be manifest-owned so update
// can prune removed managed files.

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.join(here, '..', '..');
const bin = path.join(repoRoot, 'cli', 'bin', 'treenail.js');
const piDist = path.join(repoRoot, 'dist', 'experimental', 'pi');
const cursorDist = path.join(repoRoot, 'dist', 'experimental', 'cursor');
const kimiDist = path.join(repoRoot, 'dist', 'experimental', 'kimi-code-cli');
const kiroDist = path.join(repoRoot, 'dist', 'experimental', 'kiro');
const experimentalDist = path.dirname(piDist);

const failures = [];
function check(ok, what) {
  console.log(`${ok ? 'ok' : 'FAIL'}: ${what}`);
  if (!ok) failures.push(what);
}

function run(fakeHome, args) {
  const env = { ...process.env, HOME: fakeHome, USERPROFILE: fakeHome };
  delete env.TREENAIL_HOME;
  const r = spawnSync(process.execPath, [bin, ...args], {
    env,
    encoding: 'utf8',
  });
  process.stdout.write(r.stdout || '');
  process.stderr.write(r.stderr || '');
  return r;
}

function writePiPayload(names) {
  fs.rmSync(piDist, { recursive: true, force: true });
  for (const name of names) {
    const file = path.join(piDist, 'user', name, 'SKILL.md');
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, `# ${name}\n`, 'utf8');
  }
}

const originalExists = fs.existsSync(piDist);
const originalBackup = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-pi-dist-'));
if (originalExists) {
  fs.cpSync(piDist, path.join(originalBackup, 'pi'), { recursive: true });
}

const fakeHome = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-exp-'));
const fakeCursorHome = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-cursor-exp-'));
const fakeKimiHome = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-kimi-exp-'));
const fakeKiroHome = fs.mkdtempSync(path.join(os.tmpdir(), 'treenail-kiro-exp-'));
try {
  check(
    fs.existsSync(path.join(cursorDist, 'user', 'task-brief', 'SKILL.md')),
    'Cursor adapter payload is generated from canonical skills'
  );
  check(
    fs.existsSync(path.join(piDist, 'user', 'task-brief', 'SKILL.md')),
    'Pi Coding Agent adapter payload is generated from canonical skills'
  );
  check(
    fs.existsSync(path.join(kimiDist, 'user', 'task-brief', 'SKILL.md')),
    'Kimi Code CLI adapter payload is generated from canonical skills'
  );
  check(
    fs.existsSync(path.join(kiroDist, 'user', 'task-brief', 'SKILL.md')),
    'Kiro adapter payload is generated from canonical skills'
  );

  const explicitCursorInstall = run(fakeCursorHome, ['install', '--experimental', 'cursor']);
  check(
    explicitCursorInstall.status === 0,
    `explicit Cursor experimental install exits 0 (got ${explicitCursorInstall.status})`
  );
  check(
    fs.existsSync(path.join(fakeCursorHome, '.cursor', 'skills', 'task-brief', 'SKILL.md')),
    'explicit install copies Cursor adapter payload to the Cursor skills directory'
  );
  const cursorManifest = JSON.parse(
    fs.readFileSync(path.join(fakeCursorHome, '.treenail', 'manifest.json'), 'utf8')
  );
  check(
    Object.values(cursorManifest.files || {}).some(
      (e) => e.adapterId === 'cursor' && e.experimental === true
    ),
    'manifest records Cursor experimental ownership metadata'
  );

  const explicitKimiInstall = run(fakeKimiHome, ['install', '--experimental', 'kimi']);
  check(
    explicitKimiInstall.status === 0,
    `explicit Kimi experimental install exits 0 (got ${explicitKimiInstall.status})`
  );
  check(
    fs.existsSync(path.join(fakeKimiHome, '.kimi-code', 'skills', 'task-brief', 'SKILL.md')),
    'explicit install copies Kimi Code CLI adapter payload to the Kimi skills directory'
  );
  const kimiManifest = JSON.parse(
    fs.readFileSync(path.join(fakeKimiHome, '.treenail', 'manifest.json'), 'utf8')
  );
  check(
    Object.values(kimiManifest.files || {}).some(
      (e) => e.adapterId === 'kimi-code-cli' && e.experimental === true
    ),
    'manifest records Kimi Code CLI experimental ownership metadata'
  );

  const explicitKiroInstall = run(fakeKiroHome, ['install', '--experimental', 'kiro']);
  check(
    explicitKiroInstall.status === 0,
    `explicit Kiro experimental install exits 0 (got ${explicitKiroInstall.status})`
  );
  check(
    fs.existsSync(path.join(fakeKiroHome, '.kiro', 'skills', 'task-brief', 'SKILL.md')),
    'explicit install copies Kiro adapter payload to the Kiro skills directory'
  );
  const kiroManifest = JSON.parse(
    fs.readFileSync(path.join(fakeKiroHome, '.treenail', 'manifest.json'), 'utf8')
  );
  check(
    Object.values(kiroManifest.files || {}).some(
      (e) => e.adapterId === 'kiro' && e.experimental === true
    ),
    'manifest records Kiro experimental ownership metadata'
  );

  fs.mkdirSync(path.join(fakeHome, '.claude'), { recursive: true });
  writePiPayload(['pi-test']);

  const missingExperimental = run(fakeHome, ['install', '--experimental', 'unknown-agent']);
  check(
    missingExperimental.status === 1,
    `unknown experimental adapter exits 1 (got ${missingExperimental.status})`
  );
  check(
    !fs.existsSync(path.join(fakeHome, '.treenail')),
    'unknown experimental adapter fails before provisioning runtime'
  );

  const defaultInstall = run(fakeHome, ['install']);
  check(defaultInstall.status === 0, `default install exits 0 (got ${defaultInstall.status})`);
  check(
    !fs.existsSync(path.join(fakeHome, '.pi', 'agent', 'skills', 'pi-test')),
    'default install skips experimental payloads'
  );

  const detect = run(fakeHome, ['detect', '--experimental']);
  check(detect.status === 0, `detect --experimental exits 0 (got ${detect.status})`);
  check(
    /Pi Coding Agent/.test(detect.stdout) && /Experimental runtime adapters \(unvalidated\)/.test(detect.stdout),
    'detect labels experimental adapters as unvalidated runtime adapters'
  );

  const explicitInstall = run(fakeHome, ['install', '--experimental', 'pi']);
  check(explicitInstall.status === 0, `explicit experimental install exits 0 (got ${explicitInstall.status})`);
  check(
    fs.existsSync(path.join(fakeHome, '.pi', 'agent', 'skills', 'pi-test', 'SKILL.md')),
    'explicit install copies selected experimental adapter payload'
  );

  const manifest = JSON.parse(
    fs.readFileSync(path.join(fakeHome, '.treenail', 'manifest.json'), 'utf8')
  );
  const entries = Object.values(manifest.files || {});
  check(manifest.schema === 2, 'manifest uses schema 2');
  check(
    entries.some((e) => e.adapterId === 'pi' && e.experimental === true && e.packageVersion),
    'manifest records experimental adapter ownership metadata'
  );

  const defaultUpdate = run(fakeHome, ['update']);
  check(defaultUpdate.status === 0, `default update exits 0 (got ${defaultUpdate.status})`);
  const defaultUpdateManifest = JSON.parse(
    fs.readFileSync(path.join(fakeHome, '.treenail', 'manifest.json'), 'utf8')
  );
  check(
    Object.values(defaultUpdateManifest.files || {}).some((e) => e.adapterId === 'pi'),
    'default update preserves unselected experimental manifest entries'
  );
  check(
    fs.existsSync(path.join(fakeHome, '.pi', 'agent', 'skills', 'pi-test', 'SKILL.md')),
    'default update leaves unselected experimental payload in place'
  );

  writePiPayload(['pi-next']);
  const update = run(fakeHome, ['update', '--experimental=pi']);
  check(update.status === 0, `experimental update exits 0 (got ${update.status})`);
  check(
    !fs.existsSync(path.join(fakeHome, '.pi', 'agent', 'skills', 'pi-test', 'SKILL.md')),
    'update prunes removed experimental managed files'
  );
  check(
    fs.existsSync(path.join(fakeHome, '.pi', 'agent', 'skills', 'pi-next', 'SKILL.md')),
    'update installs replacement experimental payload'
  );
} finally {
  fs.rmSync(fakeHome, { recursive: true, force: true });
  fs.rmSync(fakeCursorHome, { recursive: true, force: true });
  fs.rmSync(fakeKimiHome, { recursive: true, force: true });
  fs.rmSync(fakeKiroHome, { recursive: true, force: true });
  fs.rmSync(piDist, { recursive: true, force: true });
  if (originalExists) {
    fs.cpSync(path.join(originalBackup, 'pi'), piDist, { recursive: true });
  } else {
    try {
      fs.rmdirSync(experimentalDist);
    } catch {
      // Other experimental adapters may exist; leave the parent in place.
    }
  }
  fs.rmSync(originalBackup, { recursive: true, force: true });
}

if (failures.length) {
  console.error(`\nexperimental-install: ${failures.length} check(s) failed`);
  process.exit(1);
}
console.log('\nexperimental-install: passed');
