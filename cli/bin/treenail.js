#!/usr/bin/env node
import { detect } from '../lib/detect.js';
import { install, update } from '../lib/install.js';

const USAGE = `treenail — installer for the Treenail planning-skills pack

Usage:
  npx treenail detect     report which supported agents are present
  npx treenail install    install skills for detected agents + provision ~/.treenail
  npx treenail update     overwrite Treenail-managed dirs with this version
  npx treenail help       show this message

Supported agents: Claude Code, opencode, Codex CLI (user-level installs).
Shared runtime home: ~/.treenail (override with TREENAIL_HOME).
`;

async function main() {
  // D-020: hard gate, not just advisory engines — on distro/corporate
  // Node 18/20 the CLI half-works and then crashes cryptically inside
  // install (import.meta.dirname is undefined below 20.11).
  const nodeMajor = Number(process.versions.node.split('.')[0]);
  if (nodeMajor < 22) {
    console.error(
      `treenail requires Node 22 or newer (you are running ${process.versions.node}).`
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
      return update(args);
    case 'help':
    case '--help':
    case '-h':
    case undefined:
      console.log(USAGE);
      return cmd === undefined ? 1 : 0;
    default:
      console.error(`treenail: unknown command '${cmd}'\n`);
      console.log(USAGE);
      return 1;
  }
}

main().then(
  (code) => process.exit(code),
  (err) => {
    console.error(`treenail: ${err.message}`);
    process.exit(1);
  }
);
