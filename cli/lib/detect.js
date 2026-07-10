import {
  detectExperimentalAdapters,
  detectProviders,
  parseExperimentalSelections,
} from './providers.js';

// `treenail detect` — report which agents are present and where each
// one's user-level skill directory is (T-012).
export function detect(args = []) {
  const results = detectProviders();
  for (const p of results) {
    const mark = p.present ? 'found' : 'not found';
    console.log(`${p.name.padEnd(12)} ${mark.padEnd(10)} ${p.skillsDir}`);
  }
  const found = results.filter((p) => p.present);
  console.log(
    found.length
      ? `\n${found.length} agent(s) detected.`
      : '\nNo supported agents detected (looked for Claude Code, opencode, Codex CLI).'
  );

  const wantsExperimental = args.some((arg) => arg === '--experimental' || arg.startsWith('--experimental='));
  if (wantsExperimental) {
    const bareListAll = args.length === 1 && args[0] === '--experimental';
    const { adapters, errors } = bareListAll
      ? { adapters: [], errors: [] }
      : parseExperimentalSelections(args);
    if (errors.length) {
      for (const err of errors) console.error(err);
      return 1;
    }
    const selected = adapters.length
      ? detectExperimentalAdapters().filter((p) => adapters.some((a) => a.id === p.id))
      : detectExperimentalAdapters();
    console.log('\nExperimental runtime adapters (unvalidated):');
    for (const p of selected) {
      const mark = p.present ? 'found' : 'not found';
      console.log(`${p.name.padEnd(20)} ${mark.padEnd(10)} ${p.skillsDir}`);
    }
  }
  return 0;
}
