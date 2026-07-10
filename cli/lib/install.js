import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

import readline from 'node:readline';

import {
  detectProviders,
  normalizeExperimentalAdapter,
  parseExperimentalSelections,
  treenailHome,
} from './providers.js';
import {
  managedRoots,
  experimentalManagedRoots,
  computeManifest,
  computeManifestForFiles,
  writeManifest,
  readManifest,
  locallyModified,
  backupModified,
  mergeManifests,
  normalizeManifest,
  pruneRemovedManagedFiles,
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

function listFiles(root) {
  const out = [];
  const rec = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) rec(full);
      else if (e.isFile()) out.push(full);
    }
  };
  if (fs.existsSync(root)) rec(root);
  return out.sort();
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

function hasForce(args) {
  return args.includes('--yes') || args.includes('-y') || args.includes('--force');
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

function experimentalDistRoot(dist, adapter) {
  return path.join(dist, 'experimental', adapter.id);
}

function retainUnselectedExperimentalManifest(manifest, selectedAdapters) {
  manifest = normalizeManifest(manifest);
  if (!manifest) return null;
  const selected = new Set(selectedAdapters.map((a) => a.id));
  const retained = {
    schema: 2,
    generatedBy: 'treenail',
    packageVersion: manifest.packageVersion,
    files: {},
  };
  for (const [key, entry] of Object.entries(manifest.files || {})) {
    if (entry.experimental && !selected.has(entry.adapterId)) {
      retained.files[key] = entry;
    }
  }
  return retained;
}

function warnExperimentalProjectDivergence(manifest, dist, currentVersion) {
  manifest = normalizeManifest(manifest);
  if (!manifest) return;
  const seen = new Set();
  for (const entry of Object.values(manifest.files || {})) {
    if (!entry.experimental || !entry.rootLabel?.endsWith(':project')) continue;
    const key = `${entry.adapterId}:${entry.installRoot}`;
    if (seen.has(key)) continue;
    seen.add(key);
    if (entry.packageVersion && entry.packageVersion !== currentVersion) {
      console.warn(
        `WARNING: project experimental config for ${entry.adapterId} was written by ` +
          `Treenail ${entry.packageVersion}; this package is ${currentVersion}.`
      );
    }
    const adapter = normalizeExperimentalAdapter(entry.adapterId);
    if (!adapter || !fs.existsSync(experimentalDistRoot(dist, adapter))) {
      console.warn(
        `WARNING: project experimental config references unavailable adapter ` +
          `'${entry.adapterId}'.`
      );
    }
  }
}

function assertExperimentalDist(dist, adapter) {
  const adapterDist = experimentalDistRoot(dist, adapter);
  if (!fs.existsSync(adapterDist)) {
    throw new Error(
      `${adapter.name} is registered as an experimental runtime adapter, ` +
        `but this package does not include dist/experimental/${adapter.id} yet`
    );
  }
  return adapterDist;
}

function validateExperimentalAdapters(dist, adapters) {
  for (const adapter of adapters) assertExperimentalDist(dist, adapter);
}

function copyManagedTree(srcRoot, destRoot, claim, options = {}) {
  const claims = [];
  const manifest = normalizeManifest(options.manifest);
  const conflicts = [];
  const files = listFiles(srcRoot);
  for (const src of files) {
    const rel = path.relative(srcRoot, src);
    const dest = path.join(destRoot, rel);
    const key = `${claim.label}/${rel.split(path.sep).join('/')}`;
    if (fs.existsSync(dest) && !manifest?.files?.[key]) {
      conflicts.push({
        key,
        label: claim.label,
        rel,
        abs: dest,
        adapterId: claim.adapterId,
        experimental: true,
      });
    }
  }
  if (conflicts.length && !hasForce(options.args || [])) {
    throw new Error(
      `refusing to overwrite ${conflicts.length} unowned experimental file(s); ` +
        're-run with --force to back them up and overwrite'
    );
  }
  if (conflicts.length) {
    const backup = backupModified(conflicts);
    console.log(`Backed up ${conflicts.length} unowned file(s) → ${backup}`);
  }
  for (const src of files) {
    const rel = path.relative(srcRoot, src);
    const dest = path.join(destRoot, rel);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
    claims.push({ ...claim, root: destRoot, rel });
  }
  return claims;
}

function copyExperimentalTree(srcRoot, destRoot, claim, options) {
  const claims = copyManagedTree(srcRoot, destRoot, claim, options);
  if (claims.length === 0 && listFiles(srcRoot).length > 0) {
    throw new Error(`${claim.adapterId} experimental adapter copied no files`);
  }
  return claims;
}

function installExperimentalAdapters(dist, adapters, verb, options = {}) {
  const claims = [];
  for (const adapter of adapters) {
    const adapterDist = assertExperimentalDist(dist, adapter);
    const userSrc = path.join(adapterDist, 'user');
    const projectSrc = path.join(adapterDist, 'project');

    console.log(
      `${adapter.name}: ${verb.toLowerCase()} experimental runtime adapter (unvalidated)`
    );
    if (fs.existsSync(userSrc)) {
      claims.push(
        ...copyExperimentalTree(userSrc, adapter.skillsDir, {
          label: `experimental:${adapter.id}:user`,
          adapterId: adapter.id,
          experimental: true,
        }, options)
      );
      console.log(`  user files → ${adapter.skillsDir}`);
    }
    if (fs.existsSync(projectSrc)) {
      claims.push(
        ...copyExperimentalTree(projectSrc, process.cwd(), {
          label: `experimental:${adapter.id}:project`,
          adapterId: adapter.id,
          experimental: true,
        }, options)
      );
      console.log(`  project files → ${process.cwd()}`);
    }
    if (!fs.existsSync(userSrc) && !fs.existsSync(projectSrc)) {
      throw new Error(
        `${adapter.name} experimental adapter has no user/ or project/ payload`
      );
    }
  }
  return claims;
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
  const { adapters: experimentalAdapters, errors } = parseExperimentalSelections(args);

  if (dev && !fs.existsSync(path.join(repoSkills, '_shared'))) {
    console.error('install --dev requires a repo checkout (skills/ not found).');
    return 1;
  }
  if (errors.length) {
    for (const err of errors) console.error(err);
    return 1;
  }
  validateExperimentalAdapters(dist, experimentalAdapters);

  const providers = detectProviders().filter((p) => p.present);
  if (!providers.length && !experimentalAdapters.length) {
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

  const experimentalClaims = experimentalAdapters.length
    ? installExperimentalAdapters(dist, experimentalAdapters, 'Installed', { args })
    : [];

  // Record a manifest of everything just installed (T-015/T-059), so a later
  // `update` can tell a user's edits from a clean install. Skipped for --dev
  // symlink installs: there is no managed copy to protect.
  if (!dev) {
    writeManifest(
      home,
      mergeManifests(
        computeManifest(managedRoots(providers, home), {
          packageVersion: version,
        }),
        computeManifestForFiles(experimentalClaims, {
          packageVersion: version,
        })
      )
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
  const { adapters: experimentalAdapters, errors } = parseExperimentalSelections(args);
  if (errors.length) {
    for (const err of errors) console.error(err);
    return 1;
  }
  validateExperimentalAdapters(dist, experimentalAdapters);
  const providers = detectProviders().filter((p) => p.present);
  if (!providers.length && !experimentalAdapters.length) {
    console.error(
      'No supported agents detected (Claude Code, opencode, Codex CLI); nothing to update.'
    );
    return 1;
  }

  // Guard local edits before the wholesale overwrite (T-015, R-003/R-011):
  // diff the current install against the manifest written at install/update
  // time; if anything was edited, warn, confirm, and back it up first.
  const home = treenailHome();
  const roots = [
    ...managedRoots(providers, home),
    ...experimentalManagedRoots(experimentalAdapters, process.cwd()),
  ];
  const manifest = readManifest(home);
  let confirmedOverwrite = false;
  if (manifest) {
    const changed = locallyModified(roots, manifest);
    if (changed.length) {
      if (!(await confirmOverwrite(changed, args))) return 1;
      confirmedOverwrite = true;
      const backup = backupModified(changed);
      console.log(`Backed up ${changed.length} modified file(s) → ${backup}`);
    }
  }

  const version = overwriteManaged(dist, providers, 'Updated');
  warnExperimentalProjectDivergence(manifest, dist, version);
  const experimentalClaims = experimentalAdapters.length
    ? installExperimentalAdapters(dist, experimentalAdapters, 'Updated', {
        args,
        manifest,
      })
    : [];
  // Restamp the manifest to match the freshly-installed content.
  const newManifest = mergeManifests(
    computeManifest(managedRoots(providers, home), {
      packageVersion: version,
    }),
    computeManifestForFiles(experimentalClaims, {
      packageVersion: version,
    }),
    retainUnselectedExperimentalManifest(manifest, experimentalAdapters)
  );
  const prune = pruneRemovedManagedFiles(roots, manifest, newManifest, {
    allowModified: confirmedOverwrite || args.includes('--force'),
  });
  if (prune.blocked.length) {
    console.error(
      `Refusing to prune ${prune.blocked.length} locally edited managed file(s); ` +
        're-run `treenail update --force` to back them up and prune.'
    );
    return 1;
  }
  if (prune.pruned.length) {
    console.log(`Pruned ${prune.pruned.length} removed managed file(s).`);
  }
  writeManifest(home, newManifest);
  return 0;
}
