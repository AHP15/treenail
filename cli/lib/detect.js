import { detectProviders } from './providers.js';

// `treenail detect` — report which agents are present and where each
// one's user-level skill directory is (T-012).
export function detect() {
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
  return 0;
}
