#!/usr/bin/env node
// Rename-integrity name assertions (T-037, R-020/R-021): every publishable
// name must read `treenail` — the npm package name (which names the packed
// tarball), the plugin manifest, and the marketplace entry. The token grep
// half of the gate lives in CI / docs/release-gate.md; this script owns the
// structured-name half.
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = path.join(import.meta.dirname, '..', '..');
const read = (p) => JSON.parse(fs.readFileSync(path.join(repoRoot, p), 'utf8'));

const marketplace = read('.claude-plugin/marketplace.json');
const checks = [
  ['npm package name (cli/package.json)', read('cli/package.json').name],
  [
    'plugin manifest name (dist/claude-plugin/.claude-plugin/plugin.json)',
    read('dist/claude-plugin/.claude-plugin/plugin.json').name,
  ],
  ['marketplace name (.claude-plugin/marketplace.json)', marketplace.name],
  [
    'marketplace plugin entry (.claude-plugin/marketplace.json)',
    marketplace.plugins?.[0]?.name,
  ],
];

let failed = false;
for (const [what, actual] of checks) {
  if (actual === 'treenail') {
    console.log(`ok: ${what} = "treenail"`);
  } else {
    console.error(`FAIL: ${what} = ${JSON.stringify(actual)}, expected "treenail"`);
    failed = true;
  }
}

if (failed) process.exit(1);
console.log('check-rename: all publishable names read treenail');
