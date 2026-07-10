# Cursor Experimental Adapter Validation - 2026-07-10

This is a packaged experimental-adapter validation record for D-034 and
T-063. It is not a D-031 supported-agent graduation record.

## Adapter Identity

- **Adapter id**: `cursor`
- **Runtime-qualified display name**: Cursor
- **Short CLI aliases**: `cursor-cli`
- **Experimental status visible in installer/detect output**: yes; installer
  output says `experimental runtime adapter (unvalidated)` and detector output
  groups it under `Experimental runtime adapters (unvalidated)`.
- **Validated package version**: `0.1.0`
- **Validation date**: 2026-07-10
- **OS and shell**: macOS development checkout, zsh.
- **Agent version and channel**: not executed against a live Cursor runtime;
  this record validates packaged adapter generation and install behavior only.
- **Model/provider, where applicable**: not applicable for packaged adapter
  validation.
- **Interaction mode**: packaged installer path via `treenail install
  --experimental cursor`; live Cursor parity remains unvalidated.

## Source Freshness

- **Official source URLs re-checked on validation date**:
  `https://cursor.com/docs` and `https://cursor.com/docs/skills`.
- **Install path confirmed**: not confirmed from the official source text
  available to this validation run.
- **Config directory confirmed**: not confirmed from the official source text
  available to this validation run; adapter currently targets
  `~/.cursor/skills/`.
- **Instruction/skill format confirmed**: the official docs expose an Agent
  Skills page, but exact path/frontmatter constraints remain live-runtime
  validation items.
- **CLI/TUI/headless mode confirmed**: not confirmed from the official source
  text available to this validation run.
- **Permission or sandbox behavior confirmed**: not confirmed from the official
  source text available to this validation run.
- **Dossier changes since initial observation**: added the current Cursor
  Agent Skills docs URL; unresolved facts remain explicitly called out.

## Runtime Mapping Checklist

- **Frontmatter/metadata mapping**: canonical `name` and `description` are kept;
  no Cursor-specific metadata is invented.
- **Skill placement**: packaged payload is
  `dist/experimental/cursor/user/<skill>/SKILL.md`; installer copies it to
  `~/.cursor/skills/<skill>/SKILL.md` only when explicitly selected.
- **User-level config/write path**: `~/.cursor/skills/`.
- **Project-level config/write path, if required**: none for this adapter.
- **Tool or permission instructions**: canonical instructions are retained; a
  Cursor provider note states live activation remains experimental until a
  runtime parity pass is recorded.
- **User-interview affordances**: provider note uses the standard prose
  interview protocol.
- **Dropped canonical content**: none.
- **Transformed canonical content**: shared-runtime references are rewritten to
  `~/.treenail`; provider note and version/runtime preflight notes are injected.
- **Adapter-specific provider note**: present in every generated Cursor skill.
- **Runtime-missing or unsupported-mode message**: unknown aliases report the
  known experimental adapter list before runtime provisioning.

## Packaged Install Validation

- **Command under test**: `node cli/test/experimental-install.mjs`.
- **Default install confirmed not to include this adapter**: yes; experimental
  adapters are never installed by default.
- **Explicit `--experimental <agent>` install result**: yes; explicit
  `--experimental cursor` install copies the selected Cursor payload to
  `~/.cursor/skills/`.
- **Manifest ownership entries observed**: yes; manifest schema 2 records
  `adapterId: cursor`, `experimental: true`, and package version metadata.
- **Update/prune behavior observed**: the shared experimental manifest/update
  path is exercised by the Pi prune test; Cursor install ownership is exercised
  directly.
- **Supported-agent surfaces remained unchanged**: yes; claim-surface tests
  assert experimental runtime adapters do not enter `SUPPORTED_AGENTS`.

## Parity Run

- **Skills exercised**: packaged install smoke around generated `task-brief`
  payload; no live Cursor skill invocation.
- **Scenario limits**: runtime execution, live prompt handling, exact Cursor
  skill discovery, and permission behavior were not exercised.
- **Audit result**: adapter validation is covered by the CLI smoke tests and
  build check; planning audit remains the release-gate check.
- **Interview-protocol judgment**: mapped through the standard prose interview
  provider note.
- **Known residual differences**: live Cursor skill discovery and behavior
  remain unknown until a Cursor runtime parity pass is run.
- **Graduation recommendation**: remain experimental.
