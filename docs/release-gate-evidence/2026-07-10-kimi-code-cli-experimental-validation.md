# Kimi Code CLI Experimental Adapter Validation - 2026-07-10

This is a packaged experimental-adapter validation record for D-034 and
T-062. It is not a D-031 supported-agent graduation record.

## Adapter Identity

- **Adapter id**: `kimi-code-cli`
- **Runtime-qualified display name**: Kimi Code CLI
- **Short CLI aliases**: `kimi`, `kimi-code`
- **Experimental status visible in installer/detect output**: yes;
  installer output says `experimental runtime adapter (unvalidated)` and
  detector output groups it under `Experimental runtime adapters
  (unvalidated)`.
- **Validated package version**: `0.1.0`
- **Validation date**: 2026-07-10
- **OS and shell**: macOS development checkout, zsh.
- **Agent version and channel**: not executed against a live Kimi Code CLI
  runtime; this record validates packaged adapter generation and install
  behavior only.
- **Model/provider, where applicable**: not applicable for packaged adapter
  validation.
- **Interaction mode**: packaged installer path via `treenail install
  --experimental kimi`; live terminal parity remains unvalidated.

## Source Freshness

- **Official source URLs re-checked on validation date**: dossier sources
  `https://www.kimi.com/code`,
  `https://www.kimi.com/code/docs/en/`,
  `https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html`,
  `https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files.html`,
  and
  `https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/data-locations.html`.
- **Install path confirmed**: source dossier records the official install
  script and `kimi` command; live installation was not performed.
- **Config directory confirmed**: source dossier records `~/.kimi-code/` by
  default, overridable with `KIMI_CODE_HOME`.
- **Instruction/skill format confirmed**: source dossier records directory-form
  `<name>/SKILL.md` skills with required `name` and `description` frontmatter.
- **CLI/TUI/headless mode confirmed**: source dossier records terminal use via
  `kimi`; live runtime execution remains for graduation validation.
- **Permission or sandbox behavior confirmed**: source dossier records
  `default_permission_mode` and `permission.rules`; adapter provider note calls
  this out.
- **Dossier changes since initial observation**: registry write path corrected
  to the documented `~/.kimi-code/skills/` user-level directory.

## Runtime Mapping Checklist

- **Frontmatter/metadata mapping**: canonical `name` and `description` are kept,
  matching Kimi Code CLI directory-form requirements.
- **Skill placement**: packaged payload is
  `dist/experimental/kimi-code-cli/user/<skill>/SKILL.md`; installer copies it
  to `~/.kimi-code/skills/<skill>/SKILL.md` only when explicitly selected.
- **User-level config/write path**: `~/.kimi-code/skills/`.
- **Project-level config/write path, if required**: none for this adapter.
- **Tool or permission instructions**: canonical instructions are retained; a
  Kimi provider note warns that scripted write steps depend on the active Kimi
  permission settings.
- **User-interview affordances**: provider note uses the standard prose
  interview protocol.
- **Dropped canonical content**: none.
- **Transformed canonical content**: shared-runtime references are rewritten to
  `~/.treenail`; provider note and version/runtime preflight notes are injected.
- **Adapter-specific provider note**: present in every generated Kimi skill.
- **Runtime-missing or unsupported-mode message**: missing packaged payload
  fails before runtime provisioning; unknown aliases report the known
  experimental adapter list.

## Packaged Install Validation

- **Command under test**: `node cli/test/experimental-install.mjs`.
- **Default install confirmed not to include this adapter**: yes; experimental
  adapters are never installed by default.
- **Explicit `--experimental <agent>` install result**: yes; explicit
  `--experimental kimi` install copies the selected Kimi payload to
  `~/.kimi-code/skills/`.
- **Manifest ownership entries observed**: yes; manifest schema 2 records
  `adapterId: kimi-code-cli`, `experimental: true`, and package version
  metadata.
- **Update/prune behavior observed**: the shared experimental manifest/update
  path is exercised by the Pi prune test; Kimi install ownership is exercised
  directly.
- **Supported-agent surfaces remained unchanged**: yes; claim-surface tests
  assert experimental runtime adapters do not enter `SUPPORTED_AGENTS`.

## Parity Run

- **Skills exercised**: packaged install smoke around generated `task-brief`
  payload; no live Kimi Code CLI skill invocation.
- **Scenario limits**: runtime execution, live prompt handling, and real Kimi
  permission behavior were not exercised.
- **Audit result**: adapter validation is covered by the CLI smoke tests and
  build check; planning audit remains the release-gate check.
- **Interview-protocol judgment**: mapped through the standard prose interview
  provider note.
- **Known residual differences**: live Kimi Code CLI skill discovery and
  behavior remain unknown until a Kimi runtime parity pass is run.
- **Graduation recommendation**: remain experimental.
