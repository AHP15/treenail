// Manifest for Treenail-managed installs (T-015/T-059, D-010/D-035). It records
// enough ownership metadata to avoid blindly overwriting or pruning user files:
// root label, install root, adapter id, package version, experimental status,
// relative path, and either the prior content hash or a Treenail marker.
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const MANIFEST_NAME = 'manifest.json';
const MANIFEST_SCHEMA = 2;
export const TREENAIL_MARKER = 'treenail-managed';

export function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

// Every regular file under root. Symlinks are skipped: a `--dev` install
// links skill dirs straight at the repo checkout, and there is no managed
// copy to protect (editing it edits the repo by design).
function walkFiles(root) {
  const out = [];
  const rec = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, e.name);
      if (e.isDirectory()) rec(full);
      else if (e.isFile()) out.push(full);
    }
  };
  if (fs.existsSync(root)) rec(root);
  return out;
}

// The managed roots Treenail owns: each present provider's skill dir plus the
// shared runtime home. Returns [{ label, root }] with a stable, readable label.
export function managedRoots(providers, home) {
  const roots = providers.map((p) => ({
    label: p.id,
    root: p.skillsDir,
    adapterId: p.id,
    experimental: Boolean(p.experimental),
  }));
  roots.push({
    label: 'treenail-home',
    root: home,
    adapterId: 'treenail-home',
    experimental: false,
  });
  return roots;
}

export function experimentalManagedRoots(adapters, projectRoot = process.cwd()) {
  return adapters.flatMap((adapter) => {
    const roots = [];
    if (adapter.skillsDir) {
      roots.push({
        label: `experimental:${adapter.id}:user`,
        root: adapter.skillsDir,
        adapterId: adapter.id,
        experimental: true,
      });
    }
    roots.push({
      label: `experimental:${adapter.id}:project`,
      root: projectRoot,
      adapterId: adapter.id,
      experimental: true,
    });
    return roots;
  });
}

function normalizeRoot(root) {
  return path.resolve(root);
}

function fileKey(label, rel) {
  return `${label}/${rel.split(path.sep).join('/')}`;
}

function entryForFile({ label, root, adapterId, experimental }, file, packageVersion) {
  const rel = path.relative(root, file).split(path.sep).join('/');
  return {
    rootLabel: label,
    installRoot: normalizeRoot(root),
    adapterId: adapterId || label,
    packageVersion,
    experimental: Boolean(experimental),
    path: rel,
    sha256: sha256(file),
    marker: null,
  };
}

// Schema-v2 manifest over every managed file. The manifest file itself is
// excluded so it never checksums its own record.
export function computeManifest(roots, options = {}) {
  const manifest = {
    schema: MANIFEST_SCHEMA,
    generatedBy: 'treenail',
    packageVersion: options.packageVersion || null,
    files: {},
  };
  for (const { label, root } of roots) {
    for (const file of walkFiles(root)) {
      const rel = path.relative(root, file).split(path.sep).join('/');
      if (label === 'treenail-home' && rel === MANIFEST_NAME) continue;
      manifest.files[fileKey(label, rel)] = entryForFile(
        roots.find((r) => r.label === label),
        file,
        manifest.packageVersion
      );
    }
  }
  return manifest;
}

export function computeManifestForFiles(files, options = {}) {
  const manifest = {
    schema: MANIFEST_SCHEMA,
    generatedBy: 'treenail',
    packageVersion: options.packageVersion || null,
    files: {},
  };
  for (const file of files) {
    const root = {
      label: file.label,
      root: normalizeRoot(file.root),
      adapterId: file.adapterId,
      experimental: file.experimental,
    };
    const rel = file.rel.split(path.sep).join('/');
    const abs = path.resolve(root.root, rel);
    if (!abs.startsWith(root.root + path.sep) && abs !== root.root) {
      throw new Error(`managed file escapes install root: ${file.label}/${rel}`);
    }
    manifest.files[fileKey(root.label, rel)] = entryForFile(
      root,
      abs,
      manifest.packageVersion
    );
  }
  return manifest;
}

export function manifestPath(home) {
  return path.join(home, MANIFEST_NAME);
}

export function writeManifest(home, manifest) {
  fs.writeFileSync(
    manifestPath(home),
    JSON.stringify(normalizeManifest(manifest), null, 2) + '\n'
  );
}

export function readManifest(home) {
  try {
    return normalizeManifest(JSON.parse(fs.readFileSync(manifestPath(home), 'utf8')));
  } catch {
    return null; // no prior manifest (first update, or pre-T-015 install)
  }
}

export function normalizeManifest(manifest) {
  if (!manifest) return null;
  if (manifest.schema === MANIFEST_SCHEMA && manifest.files) return manifest;

  // Legacy T-015 manifest: { "<label>/<relpath>": "<sha256>" }.
  const files = {};
  for (const [key, value] of Object.entries(manifest)) {
    if (typeof value !== 'string') continue;
    const slash = key.indexOf('/');
    if (slash === -1) continue;
    const label = key.slice(0, slash);
    const rel = key.slice(slash + 1);
    files[key] = {
      rootLabel: label,
      installRoot: null,
      adapterId: label,
      packageVersion: null,
      experimental: false,
      path: rel,
      sha256: value,
      marker: null,
    };
  }
  return {
    schema: MANIFEST_SCHEMA,
    generatedBy: 'treenail',
    packageVersion: null,
    files,
  };
}

function rootByLabel(roots) {
  return Object.fromEntries(
    roots.map((r) => [r.label, { ...r, root: normalizeRoot(r.root) }])
  );
}

function entryPath(root, entry) {
  if (!entry.path || path.isAbsolute(entry.path) || entry.path.includes('..')) {
    return null;
  }
  const abs = path.resolve(root.root, entry.path);
  return abs.startsWith(root.root + path.sep) || abs === root.root ? abs : null;
}

function markerMatches(abs, entry) {
  if (!entry.marker) return false;
  try {
    return fs.readFileSync(abs, 'utf8').includes(entry.marker);
  } catch {
    return false;
  }
}

function ownershipMatches(abs, entry) {
  if (!fs.existsSync(abs)) return false;
  if (entry.sha256 && sha256(abs) === entry.sha256) return true;
  return markerMatches(abs, entry);
}

// Managed files whose current ownership witness differs from the recorded
// manifest — i.e. locally edited since install. A missing file is not
// "modified" (a clean overwrite restores it); a root no longer present is
// skipped.
export function locallyModified(roots, manifest) {
  manifest = normalizeManifest(manifest);
  const rootsByLabel = rootByLabel(roots);
  const changed = [];
  for (const [key, entry] of Object.entries(manifest?.files || {})) {
    const root = rootsByLabel[entry.rootLabel];
    if (!root) continue;
    const abs = entryPath(root, entry);
    if (!abs) continue;
    if (!fs.existsSync(abs)) continue;
    if (!ownershipMatches(abs, entry)) {
      changed.push({
        key,
        label: entry.rootLabel,
        rel: entry.path,
        abs,
        adapterId: entry.adapterId,
        experimental: entry.experimental,
      });
    }
  }
  return changed;
}

export function mergeManifests(...manifests) {
  const out = {
    schema: MANIFEST_SCHEMA,
    generatedBy: 'treenail',
    packageVersion: null,
    files: {},
  };
  for (const manifest of manifests.map(normalizeManifest).filter(Boolean)) {
    out.packageVersion = manifest.packageVersion || out.packageVersion;
    Object.assign(out.files, manifest.files);
  }
  return out;
}

export function pruneRemovedManagedFiles(roots, oldManifest, newManifest, options = {}) {
  oldManifest = normalizeManifest(oldManifest);
  newManifest = normalizeManifest(newManifest);
  if (!oldManifest || !newManifest) return { pruned: [], blocked: [] };

  const rootsByLabel = rootByLabel(roots);
  const pruned = [];
  const blocked = [];
  for (const [key, oldEntry] of Object.entries(oldManifest.files)) {
    if (newManifest.files[key]) continue;
    const root = rootsByLabel[oldEntry.rootLabel];
    if (!root) continue;
    const abs = entryPath(root, oldEntry);
    if (!abs || !fs.existsSync(abs)) continue;

    if (ownershipMatches(abs, oldEntry) || options.allowModified) {
      fs.rmSync(abs, { force: true });
      pruned.push({ key, abs });
    } else {
      blocked.push({
        key,
        label: oldEntry.rootLabel,
        rel: oldEntry.path,
        abs,
        adapterId: oldEntry.adapterId,
        experimental: oldEntry.experimental,
      });
    }
  }
  return { pruned, blocked };
}

// Copy the modified files into a fresh timestamped backup dir, preserving the
// <label>/<relpath> layout, so a user's edits survive the overwrite. Returns
// the backup dir path.
export function backupModified(changed) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const dir = path.join(os.homedir(), '.treenail-backups', ts);
  for (const { label, rel, abs } of changed) {
    const dest = path.join(dir, label, rel);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(abs, dest);
  }
  return dir;
}
