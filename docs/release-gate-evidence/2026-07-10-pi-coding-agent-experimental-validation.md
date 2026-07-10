# Pi Coding Agent Experimental Adapter Validation - 2026-07-10

This is a packaged experimental-adapter validation record for D-034 and
T-061. It is not a D-031 supported-agent graduation record.

## Adapter Identity

- **Adapter id**: `pi`
- **Runtime-qualified display name**: Pi Coding Agent
- **Short CLI aliases**: `pi-coding-agent`
- **Experimental status visible in installer/detect output**: yes;
  installer output says `experimental runtime adapter (unvalidated)` and
  detector output groups it under `Experimental runtime adapters
  (unvalidated)`.
- **Validated package version**: `0.1.0`
- **Validation date**: 2026-07-10
- **OS and shell**: macOS development checkout, zsh.
- **Agent version and channel**: not executed against a live Pi runtime; this
  record validates packaged adapter generation and install behavior only.
- **Model/provider, where applicable**: not applicable for packaged adapter
  validation.
- **Interaction mode**: packaged installer path via `treenail install
  --experimental pi`; live TUI/headless parity remains unvalidated.

## Source Freshness

- **Official source URLs re-checked on validation date**: dossier source
  `https://pi.dev/`, observed in
  `2026-07-10-experimental-adapter-surface-dossiers.md`.
- **Install path confirmed**: source dossier records install commands for
  `@earendil-works/pi-coding-agent`; live installation was not performed.
- **Config directory confirmed**: source dossier records `~/.pi/agent/` for
  startup `AGENTS.md`; adapter writes user skills to `~/.pi/agent/skills/`.
- **Instruction/skill format confirmed**: source dossier records Pi support for
  skills and `AGENTS.md`; adapter emits directory-form `SKILL.md` packages.
- **CLI/TUI/headless mode confirmed**: source dossier records interactive TUI,
  `pi -p` print/JSON mode, RPC, and SDK; live runtime execution remains for
  graduation validation.
- **Permission or sandbox behavior confirmed**: source dossier records no
  built-in permission popups; adapter provider note calls this out.
- **Dossier changes since initial observation**: none.

## Runtime Mapping Checklist

- **Frontmatter/metadata mapping**: canonical `name` and `description` are kept;
  no Pi-specific metadata is invented.
- **Skill placement**: packaged payload is
  `dist/experimental/pi/user/<skill>/SKILL.md`; installer copies it to
  `~/.pi/agent/skills/<skill>/SKILL.md` only when explicitly selected.
- **User-level config/write path**: `~/.pi/agent/skills/`.
- **Project-level config/write path, if required**: none for this adapter.
- **Tool or permission instructions**: canonical instructions are retained; a
  Pi provider note warns that scripted write steps depend on shell/sandbox
  controls because Pi has no built-in permission popups.
- **User-interview affordances**: provider note uses the standard prose
  interview protocol.
- **Dropped canonical content**: none.
- **Transformed canonical content**: shared-runtime references are rewritten to
  `~/.treenail`; provider note and version/runtime preflight notes are injected.
- **Adapter-specific provider note**: present in every generated Pi skill.
- **Runtime-missing or unsupported-mode message**: missing packaged payload
  fails before runtime provisioning; unknown aliases report the known
  experimental adapter list.

## Packaged Install Validation

- **Command under test**: `node cli/test/experimental-install.mjs`.
- **Default install confirmed not to include this adapter**: yes; default
  install skips `~/.pi/agent/skills/`.
- **Explicit `--experimental <agent>` install result**: yes; explicit install
  copies the selected Pi payload.
- **Manifest ownership entries observed**: yes; manifest schema 2 records
  `adapterId: pi`, `experimental: true`, and package version metadata.
- **Update/prune behavior observed**: yes; selected experimental update prunes
  removed Pi managed files and installs replacements.
- **Supported-agent surfaces remained unchanged**: yes; claim-surface tests
  assert experimental runtime adapters do not enter `SUPPORTED_AGENTS`.

## Parity Run

- **Skills exercised**: packaged install/update smoke around generated
  `task-brief` payload; no live Pi agent skill invocation.
- **Scenario limits**: runtime execution, live prompt handling, and real Pi
  permission behavior were not exercised.
- **Audit result**: adapter validation is covered by the CLI smoke tests and
  build check; planning audit remains the release-gate check.
- **Interview-protocol judgment**: mapped through the standard prose interview
  provider note.
- **Known residual differences**: live Pi skill discovery and behavior remain
  unknown until a Pi runtime parity pass is run.
- **Graduation recommendation**: remain experimental.
