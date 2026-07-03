#!/usr/bin/env node
import { detect } from '../lib/detect.js';
import { install } from '../lib/install.js';

const USAGE = `keel-skills — installer for the Keel planning-skills pack

Usage:
  npx keel-skills detect     report which supported agents are present
  npx keel-skills install    install skills for detected agents + provision ~/.keel
  npx keel-skills update     overwrite Keel-managed dirs with this version
  npx keel-skills help       show this message

Supported agents: Claude Code, opencode, Codex CLI (user-level installs).
Shared runtime home: ~/.keel (override with KEEL_HOME).
`;

async function main() {
  // D-020: hard gate, not just advisory engines — on distro/corporate
  // Node 18/20 the CLI half-works and then crashes cryptically inside
  // install (import.meta.dirname is undefined below 20.11).
  const nodeMajor = Number(process.versions.node.split('.')[0]);
  if (nodeMajor < 22) {
    console.error(
      `keel-skills requires Node 22 or newer (you are running ${process.versions.node}).`
    );
    return 1;
  }

  const [cmd, ...args] = process.argv.slice(2);
  switch (cmd) {
    case 'detect':
      return detect(args);
    case 'install':
      return install(args);
    case 'update':
      console.error('keel-skills update: not implemented yet.');
      return 1;
    case 'help':
    case '--help':
    case '-h':
    case undefined:
      console.log(USAGE);
      return cmd === undefined ? 1 : 0;
    default:
      console.error(`keel-skills: unknown command '${cmd}'\n`);
      console.log(USAGE);
      return 1;
  }
}

main().then(
  (code) => process.exit(code),
  (err) => {
    console.error(`keel-skills: ${err.message}`);
    process.exit(1);
  }
);
