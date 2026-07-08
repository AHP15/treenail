#!/usr/bin/env node
// Claim + support-surface gate (T-050, R-032/R-034). Three invariants over the
// public surfaces that carry the equal-support message:
//   1. No stale ranking fragment survives (Best/Full tier, "Best on Claude Code",
//      badge: 'Best', "never parity") — R-032's opposite-stance residue.
//   2. Any surface that makes the parity claim also carries the neutral surface
//      note — D-030 is only honest as claim+note together (R-032).
//   3. Every advertised supported agent resolves to a dated validation record
//      linked from the README supported list — the support bar has teeth (R-034).
// The advertised-agent set is read from page.tsx's SUPPORTED_AGENTS, so adding a
// new agent name without a record/link fails the build automatically.
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = path.join(import.meta.dirname, '..', '..');
const read = (p) => fs.readFileSync(path.join(repoRoot, p), 'utf8');

// The public surfaces that carry the parity claim (R-032).
const README = 'README.md';
const MDX = 'site/content/docs/reference/supported-agents.mdx';
const PAGE = 'site/app/page.tsx';
const RECORD_DOC = 'docs/cross-agent-parity-validation.md';
const CLAIM_SURFACES = [README, MDX, PAGE];

// GitHub heading slug: lowercase, drop chars outside [a-z0-9 -], spaces→hyphens.
const slug = (s) =>
  s.toLowerCase().replace(/[^a-z0-9 -]/g, '').trim().replace(/\s+/g, '-');

const failures = [];
const fail = (msg) => failures.push(msg);
const ok = (msg) => console.log(`ok: ${msg}`);

// --- Check 1: no stale ranking fragment on any surface (R-032). ---
const RANKING_FRAGMENTS = [
  /badge:\s*['"]Best['"]/i,
  /best on claude code/i,
  /never parity/i,
  /\|\s*\*\*Best\*\*\s*\|/, // a Best/Full tier-table cell
  /\|\s*Tier\s*\|/i, // a "| Tier |" ranking column header
];
for (const surface of CLAIM_SURFACES) {
  const text = read(surface);
  const hit = RANKING_FRAGMENTS.find((re) => re.test(text));
  if (hit) fail(`${surface}: stale ranking fragment ${hit} — D-030 dropped ranking`);
  else ok(`${surface}: no stale ranking fragment`);
}

// --- Check 2: parity claim never appears without the surface note (R-032). ---
const CLAIM = /functional parity|full pipeline on|complete pipeline|every supported agent runs/i;
const NOTE = /selectable options on Claude Code/i;
for (const surface of CLAIM_SURFACES) {
  const text = read(surface);
  if (CLAIM.test(text) && !NOTE.test(text))
    fail(`${surface}: makes the parity claim but is missing the surface note`);
  else ok(`${surface}: claim/note paired`);
}

// --- Check 3: every advertised agent resolves to a linked validation record (R-034). ---
const pageText = read(PAGE);
const arrayMatch = pageText.match(/SUPPORTED_AGENTS\s*=\s*\[([^\]]*)\]/);
if (!arrayMatch) {
  fail(`${PAGE}: could not locate the SUPPORTED_AGENTS list`);
} else {
  const agents = [...arrayMatch[1].matchAll(/['"]([^'"]+)['"]/g)].map((m) => m[1]);
  if (agents.length === 0) fail(`${PAGE}: SUPPORTED_AGENTS is empty`);
  const recordDoc = read(RECORD_DOC);
  const readme = read(README);
  for (const agent of agents) {
    const anchor = slug(agent);
    const hasRecord = new RegExp(`^###\\s+${agent.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`, 'm').test(recordDoc);
    const hasLink = readme.includes(`${RECORD_DOC}#${anchor}`) ||
      readme.includes(`cross-agent-parity-validation.md#${anchor}`);
    if (!hasRecord) fail(`agent "${agent}": no "### ${agent}" validation record in ${RECORD_DOC}`);
    if (!hasLink) fail(`agent "${agent}": README supported list does not link to its record (#${anchor})`);
    if (hasRecord && hasLink) ok(`agent "${agent}": validation record present and linked`);
  }
}

if (failures.length) {
  console.error('\ncheck-claim-surfaces: FAIL');
  for (const f of failures) console.error(`  - ${f}`);
  process.exit(1);
}
console.log('\ncheck-claim-surfaces: all claim + support-surface invariants hold');
