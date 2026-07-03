// postpack: drop the prepack-staged cli/dist once the tarball is built.
// distRoot() prefers cli/dist over the repo root, so a stale staged copy
// would silently shadow fresh builds in every checkout run.
import fs from 'node:fs';
import path from 'node:path';

fs.rmSync(path.join(import.meta.dirname, '..', 'dist'), {
  recursive: true,
  force: true,
});
