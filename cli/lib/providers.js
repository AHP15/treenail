// Provider table: the three v1 agents (D-007), their user-level skill
// directories (D-008: user-level only), and how presence is detected.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const HOME = os.homedir();

export const PROVIDERS = [
  {
    id: 'claude',
    name: 'Claude Code',
    bin: 'claude',
    configDir: path.join(HOME, '.claude'),
    skillsDir: path.join(HOME, '.claude', 'skills'),
  },
  {
    id: 'opencode',
    name: 'opencode',
    bin: 'opencode',
    configDir: path.join(HOME, '.config', 'opencode'),
    skillsDir: path.join(HOME, '.config', 'opencode', 'skills'),
  },
  {
    id: 'codex',
    name: 'Codex CLI',
    bin: 'codex',
    configDir: path.join(HOME, '.codex'),
    skillsDir: path.join(HOME, '.codex', 'skills'),
  },
];

// ~/.treenail — the agent-neutral shared runtime home (D-006), overridable
// via TREENAIL_HOME.
export function treenailHome(env = process.env) {
  return env.TREENAIL_HOME || path.join(HOME, '.treenail');
}

function onPath(bin, env = process.env) {
  const exts = process.platform === 'win32'
    ? (env.PATHEXT || '.EXE;.CMD;.BAT;.COM').split(';')
    : [''];
  for (const dir of (env.PATH || '').split(path.delimiter)) {
    if (!dir) continue;
    for (const ext of exts) {
      try {
        fs.accessSync(path.join(dir, bin + ext.toLowerCase()), fs.constants.X_OK);
        return true;
      } catch { /* keep looking */ }
    }
  }
  return false;
}

// An agent counts as present if its CLI is on PATH or its config dir exists.
export function detectProviders() {
  return PROVIDERS.map((p) => ({
    ...p,
    present: onPath(p.bin) || fs.existsSync(p.configDir),
    skillsDirExists: fs.existsSync(p.skillsDir),
  }));
}
