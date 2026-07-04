// Checksum manifest for the Treenail-managed install (T-015, D-010, R-003,
// R-011). install/update record a sha256 of every managed file; update diffs
// the on-disk files against that record so it can detect — and never silently
// discard — local edits before a wholesale overwrite. Per-project docs/ is
// user data and is never in scope here.
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const MANIFEST_NAME = 'manifest.json';

function sha256(file) {
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
  const roots = providers.map((p) => ({ label: p.id, root: p.skillsDir }));
  roots.push({ label: 'treenail-home', root: home });
  return roots;
}

// { "<label>/<relpath>": sha256 } over every managed file. The manifest file
// itself is excluded so it never checksums its own record.
export function computeManifest(roots) {
  const manifest = {};
  for (const { label, root } of roots) {
    for (const file of walkFiles(root)) {
      const rel = path.relative(root, file);
      if (label === 'treenail-home' && rel === MANIFEST_NAME) continue;
      manifest[`${label}/${rel}`] = sha256(file);
    }
  }
  return manifest;
}

export function manifestPath(home) {
  return path.join(home, MANIFEST_NAME);
}

export function writeManifest(home, manifest) {
  fs.writeFileSync(
    manifestPath(home),
    JSON.stringify(manifest, null, 2) + '\n'
  );
}

export function readManifest(home) {
  try {
    return JSON.parse(fs.readFileSync(manifestPath(home), 'utf8'));
  } catch {
    return null; // no prior manifest (first update, or pre-T-015 install)
  }
}

// Managed files whose current checksum differs from the recorded manifest —
// i.e. locally edited since install. A file the manifest lists but that is now
// missing is not "modified" (a clean overwrite restores it); a provider that
// is no longer present is skipped (nothing on disk to protect).
export function locallyModified(roots, manifest) {
  const rootByLabel = Object.fromEntries(roots.map((r) => [r.label, r.root]));
  const changed = [];
  for (const [key, recorded] of Object.entries(manifest)) {
    const slash = key.indexOf('/');
    const label = key.slice(0, slash);
    const rel = key.slice(slash + 1);
    const root = rootByLabel[label];
    if (!root) continue;
    const abs = path.join(root, rel);
    if (!fs.existsSync(abs)) continue;
    if (sha256(abs) !== recorded) changed.push({ key, label, rel, abs });
  }
  return changed;
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
