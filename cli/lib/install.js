import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

import { detectProviders, treenailHome } from './providers.js';

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

// `treenail install [--dev]` — user-level install for every detected
// agent (D-007/D-008) plus one shared ~/.treenail runtime (D-006).
//
// --dev (T-016): instead of copying built files, symlink each skill dir to
// the canonical source in the repo checkout, so editing the installed copy
// edits the repo. Claude also gets _shared/_templates links because the
// canonical (unbuilt) bodies still reference ~/.claude/skills/_shared.
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
      for (const support of ['_shared', '_templates']) {
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
