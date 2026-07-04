import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

import readline from 'node:readline';

import { detectProviders, treenailHome } from './providers.js';
import {
  managedRoots,
  computeManifest,
  writeManifest,
  readManifest,
  locallyModified,
  backupModified,
} from './manifest.js';

// The built trees ship inside the published package (cli/dist, copied by
// prepack); in a repo checkout they live at the repo root.
function distRoot() {
  for (const candidate of [
    path.join(import.meta.dirname, '..', 'dist'),
    path.join(import.meta.dirname, '..', '..', 'dist'),
  ]) {
    if (fs.existsSync(path.join(candidate, 'treenail-home', 'VERSION'))) {
      return candidate;
    }
  }
  throw new Error(
    'built dist/ not found — run `python3 build.py` in the repo first'
  );
}

// D-009: Python 3 is the one scripted runtime the skills need. Detect the
// per-platform command; the installer only warns, it never blocks.
const PYTHON_CANDIDATES = process.platform === 'win32'
  ? [['py', ['-3', '--version']], ['python', ['--version']], ['python3', ['--version']]]
  : [['python3', ['--version']], ['python', ['--version']]];

function findPython() {
  for (const [cmd, args] of PYTHON_CANDIDATES) {
    try {
      const r = spawnSync(cmd, args, { encoding: 'utf8' });
      const out = `${r.stdout || ''}${r.stderr || ''}`;
      if (r.status === 0 && /Python 3\./.test(out)) return cmd;
    } catch { /* try next */ }
  }
  return null;
}

function listSkillDirs(providerDist) {
  return fs.readdirSync(providerDist, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
}

function replaceWithCopy(src, dest) {
  fs.rmSync(dest, { recursive: true, force: true });
  fs.cpSync(src, dest, { recursive: true });
}

function replaceWithSymlink(target, dest) {
  fs.rmSync(dest, { recursive: true, force: true });
  // 'junction' is what Windows allows without elevation; ignored elsewhere.
  fs.symlinkSync(target, dest, 'junction');
}

function provisionTreenailHome(dist) {
  const home = treenailHome();
  replaceWithCopy(path.join(dist, 'treenail-home'), home);
  return home;
}

// The managed-overwrite core shared by `install` and `update` (D-010):
// wholesale-replace ~/.treenail (which restamps VERSION from the shipped
// dist) and each provider's built skill dirs. Touches only Treenail-managed
// locations — never a per-project docs/ path. Returns the stamped version.
function overwriteManaged(dist, providers, verb) {
  const home = provisionTreenailHome(dist);
  const version = fs.readFileSync(path.join(home, 'VERSION'), 'utf8').trim();
  console.log(`${verb} Treenail runtime ${version} at ${home}`);

  for (const p of providers) {
    const providerDist = path.join(dist, p.id);
    fs.mkdirSync(p.skillsDir, { recursive: true });
    const skills = listSkillDirs(providerDist);
    for (const name of skills) {
      replaceWithCopy(
        path.join(providerDist, name),
        path.join(p.skillsDir, name)
      );
    }
    console.log(
      `${p.name}: ${skills.length} skills → ${p.skillsDir}`
    );
  }
  return version;
}

// `treenail install [--dev]` — user-level install for every detected
// agent (D-007/D-008) plus one shared ~/.treenail runtime (D-006).
//
// --dev (T-016): instead of copying built files, symlink each skill dir to
// the canonical source in the repo checkout, so editing the installed copy
// edits the repo. Claude also gets a _shared link because the canonical
// (unbuilt) bodies still reference ~/.claude/skills/_shared.
export function install(args = []) {
  const dev = args.includes('--dev');
  const dist = distRoot();
  const repoSkills = path.join(dist, '..', 'skills');

  if (dev && !fs.existsSync(path.join(repoSkills, '_shared'))) {
    console.error('install --dev requires a repo checkout (skills/ not found).');
    return 1;
  }

  const providers = detectProviders().filter((p) => p.present);
  if (!providers.length) {
    console.error(
      'No supported agents detected (Claude Code, opencode, Codex CLI); nothing to install.'
    );
    return 1;
  }

  const home = provisionTreenailHome(dist);
  const version = fs
    .readFileSync(path.join(home, 'VERSION'), 'utf8')
    .trim();
  console.log(`Provisioned Treenail runtime ${version} at ${home}`);

  for (const p of providers) {
    const providerDist = path.join(dist, p.id);
    fs.mkdirSync(p.skillsDir, { recursive: true });
    const skills = listSkillDirs(providerDist);
    for (const name of skills) {
      const dest = path.join(p.skillsDir, name);
      if (dev) {
        replaceWithSymlink(path.join(repoSkills, name), dest);
      } else {
        replaceWithCopy(path.join(providerDist, name), dest);
      }
    }
    if (dev && p.id === 'claude') {
      for (const support of ['_shared']) {
        replaceWithSymlink(
          path.join(repoSkills, support),
          path.join(p.skillsDir, support)
        );
      }
    }
    console.log(
      `${p.name}: ${dev ? 'linked' : 'installed'} ${skills.length} skills → ${p.skillsDir}`
    );
  }

  // Record a checksum manifest of everything just installed (T-015), so a
  // later `update` can tell a user's edits from a clean install. Skipped for
  // --dev symlink installs: there is no managed copy to protect.
  if (!dev) {
    writeManifest(home, computeManifest(managedRoots(providers, home)));
  }

  const python = findPython();
  if (python) {
    console.log(`Python 3 found (${python}) — scripted skill steps will work.`);
  } else {
    console.warn(
      'WARNING: no working Python 3 found (tried: ' +
        PYTHON_CANDIDATES.map(([c]) => c).join(', ') +
        '). Treenail skills need Python 3 for their scripted steps — install it from https://python.org.'
    );
  }
  return 0;
}

// Ask the user to confirm overwriting locally-edited files. Auto-confirms on
// --yes/-y/--force; refuses (returns false) in a non-interactive run so a
// scripted update can never silently clobber edits; otherwise prompts.
async function confirmOverwrite(changed, args) {
  console.warn(`WARNING: ${changed.length} installed file(s) have local edits:`);
  for (const c of changed) console.warn(`  ${c.key}`);
  if (args.includes('--yes') || args.includes('-y') || args.includes('--force')) {
    return true;
  }
  if (!process.stdin.isTTY) {
    console.error(
      'Refusing to overwrite local edits in a non-interactive run. ' +
        'Re-run `treenail update --yes` to back them up and overwrite.'
    );
    return false;
  }
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  const answer = await new Promise((resolve) =>
    rl.question('Back these up and overwrite? [y/N] ', resolve)
  );
  rl.close();
  return /^y(es)?$/i.test(answer.trim());
}

// `treenail update` — refresh an existing install to the version shipped in
// this package (D-010, D-014). Overwrites the Treenail-managed dirs wholesale
// (each detected provider's skill dir and ~/.treenail) and restamps
// ~/.treenail/VERSION; per-project docs/ is user data and is never read or
// written. Users who customized an install fork it rather than editing in
// place; the silent-overwrite guard for local edits is layered on by T-015.
export async function update(args = []) {
  const dist = distRoot();
  const providers = detectProviders().filter((p) => p.present);
  if (!providers.length) {
    console.error(
      'No supported agents detected (Claude Code, opencode, Codex CLI); nothing to update.'
    );
    return 1;
  }

  // Guard local edits before the wholesale overwrite (T-015, R-003/R-011):
  // diff the current install against the manifest written at install/update
  // time; if anything was edited, warn, confirm, and back it up first.
  const home = treenailHome();
  const roots = managedRoots(providers, home);
  const manifest = readManifest(home);
  if (manifest) {
    const changed = locallyModified(roots, manifest);
    if (changed.length) {
      if (!(await confirmOverwrite(changed, args))) return 1;
      const backup = backupModified(changed);
      console.log(`Backed up ${changed.length} modified file(s) → ${backup}`);
    }
  }

  overwriteManaged(dist, providers, 'Updated');
  // Restamp the manifest to match the freshly-installed content.
  writeManifest(home, computeManifest(roots));
  return 0;
}
