// prepack (T-033, R-017): bundle the built dist/ trees the installer
// reads into cli/dist so the published tarball is self-contained —
// distRoot() must resolve with no repo checkout anywhere. The
// claude-plugin tree is the marketplace channel's, not the CLI's, so it
// stays out of the package.
import fs from 'node:fs';
import path from 'node:path';

const pkgRoot = path.join(import.meta.dirname, '..');
const repoDist = path.join(pkgRoot, '..', 'dist');
const out = path.join(pkgRoot, 'dist');

const BUNDLED = ['claude', 'opencode', 'codex', 'treenail-home'];
const OPTIONAL_BUNDLED = ['experimental'];

if (!fs.existsSync(path.join(repoDist, 'treenail-home', 'VERSION'))) {
  console.error(
    'prepack: built dist/ not found at the repo root — run `python3 build.py` first.'
  );
  process.exit(1);
}

fs.rmSync(out, { recursive: true, force: true });
for (const name of BUNDLED) {
  fs.cpSync(path.join(repoDist, name), path.join(out, name), {
    recursive: true,
  });
}
const optional = [];
for (const name of OPTIONAL_BUNDLED) {
  if (fs.existsSync(path.join(repoDist, name))) {
    fs.cpSync(path.join(repoDist, name), path.join(out, name), {
      recursive: true,
    });
    optional.push(name);
  }
}
console.log(
  `prepack: bundled dist/{${[...BUNDLED, ...optional].join(',')}} into the package`
);
