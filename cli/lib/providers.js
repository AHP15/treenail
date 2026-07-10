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

export const EXPERIMENTAL_ADAPTERS = [
  {
    id: 'pi',
    aliases: ['pi-coding-agent'],
    name: 'Pi Coding Agent',
    bin: 'pi',
    configDir: path.join(HOME, '.pi', 'agent'),
    skillsDir: path.join(HOME, '.pi', 'agent', 'skills'),
  },
  {
    id: 'cursor',
    aliases: ['cursor-cli'],
    name: 'Cursor',
    bin: 'cursor-agent',
    configDir: path.join(HOME, '.cursor'),
    skillsDir: path.join(HOME, '.cursor', 'skills'),
  },
  {
    id: 'kimi-code-cli',
    aliases: ['kimi', 'kimi-code'],
    name: 'Kimi Code CLI',
    bin: 'kimi',
    configDir: path.join(HOME, '.kimi-code'),
    skillsDir: path.join(HOME, '.kimi-code', 'skills'),
  },
  {
    id: 'kiro',
    aliases: ['kiro-cli'],
    name: 'Kiro',
    bin: 'kiro-cli',
    configDir: path.join(HOME, '.kiro'),
    skillsDir: path.join(HOME, '.kiro', 'skills'),
  },
].map((adapter) => ({
  ...adapter,
  experimental: true,
  unvalidated: true,
}));

const EXPERIMENTAL_BY_TOKEN = new Map(
  EXPERIMENTAL_ADAPTERS.flatMap((adapter) => [
    [adapter.id, adapter],
    ...adapter.aliases.map((alias) => [alias, adapter]),
  ])
);

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

export function detectExperimentalAdapters() {
  return EXPERIMENTAL_ADAPTERS.map((p) => ({
    ...p,
    present: onPath(p.bin) || fs.existsSync(p.configDir),
    skillsDirExists: fs.existsSync(p.skillsDir),
  }));
}

export function experimentalAdapterTokens() {
  return [...EXPERIMENTAL_BY_TOKEN.keys()].sort();
}

export function normalizeExperimentalAdapter(token) {
  return EXPERIMENTAL_BY_TOKEN.get(String(token || '').toLowerCase()) || null;
}

export function parseExperimentalSelections(args = []) {
  const selections = [];
  const errors = [];
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--experimental') {
      const value = args[i + 1];
      if (!value || value.startsWith('-')) {
        errors.push('--experimental requires an adapter id');
      } else {
        selections.push(...value.split(','));
        i += 1;
      }
    } else if (arg.startsWith('--experimental=')) {
      selections.push(...arg.slice('--experimental='.length).split(','));
    }
  }

  const adapters = [];
  const seen = new Set();
  for (const raw of selections.map((s) => s.trim()).filter(Boolean)) {
    const adapter = normalizeExperimentalAdapter(raw);
    if (!adapter) {
      errors.push(
        `unknown experimental adapter '${raw}' (known: ${experimentalAdapterTokens().join(', ')})`
      );
      continue;
    }
    if (!seen.has(adapter.id)) {
      adapters.push(adapter);
      seen.add(adapter.id);
    }
  }
  return { adapters, errors };
}
