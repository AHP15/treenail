# Kiro Experimental Adapter Validation - 2026-07-10

This is a packaged experimental-adapter validation record for D-034 and
T-064. It is not a D-031 supported-agent graduation record.

## Adapter Identity

- **Adapter id**: `kiro`
- **Runtime-qualified display name**: Kiro
- **Short CLI aliases**: `kiro-cli`
- **Experimental status visible in installer/detect output**: yes; installer
  output says `experimental runtime adapter (unvalidated)` and detector output
  groups it under `Experimental runtime adapters (unvalidated)`.
- **Validated package version**: `0.1.0`
- **Validation date**: 2026-07-10
- **OS and shell**: macOS development checkout, zsh.
- **Agent version and channel**: not executed against a live Kiro runtime; this
  record validates packaged adapter generation and install behavior only.
- **Model/provider, where applicable**: not applicable for packaged adapter
  validation.
- **Interaction mode**: packaged installer path via `treenail install
  --experimental kiro`; live Kiro parity remains unvalidated.

## Source Freshness

- **Official source URLs re-checked on validation date**:
  `https://kiro.dev/docs/`, `https://kiro.dev/docs/cli/`,
  `https://kiro.dev/docs/skills/`, `https://kiro.dev/docs/steering/`, and
  `https://kiro.dev/docs/cli/custom-agents/`.
- **Install path confirmed**: source dossier records
  `curl -fsSL https://cli.kiro.dev/install | bash`, then `kiro-cli` from a
  project directory; live installation was not performed.
- **Config directory confirmed**: Kiro docs record global skills under
  `~/.kiro/skills/` and workspace skills under `.kiro/skills/`.
- **Instruction/skill format confirmed**: Kiro docs record directory-form
  skills containing required `SKILL.md` files with required `name` and
  `description` frontmatter.
- **CLI/TUI/headless mode confirmed**: Kiro CLI docs record terminal use via
  `kiro-cli` and headless automation with API key authentication.
- **Permission or sandbox behavior confirmed**: Kiro CLI custom-agent docs say
  the default CLI requires user confirmation for most operations and custom
  agents can pre-approve or limit tools.
- **Dossier changes since initial observation**: Kiro adapter path corrected
  from steering to the documented `~/.kiro/skills/` Agent Skills directory.

## Runtime Mapping Checklist

- **Frontmatter/metadata mapping**: canonical `name` and `description` are kept,
  matching Kiro's documented required fields.
- **Skill placement**: packaged payload is
  `dist/experimental/kiro/user/<skill>/SKILL.md`; installer copies it to
  `~/.kiro/skills/<skill>/SKILL.md` only when explicitly selected.
- **User-level config/write path**: `~/.kiro/skills/`.
- **Project-level config/write path, if required**: none for this adapter.
- **Tool or permission instructions**: canonical instructions are retained; a
  Kiro provider note warns that scripted write steps depend on active Kiro
  permission settings.
- **User-interview affordances**: provider note uses the standard prose
  interview protocol.
- **Dropped canonical content**: none.
- **Transformed canonical content**: shared-runtime references are rewritten to
  `~/.treenail`; provider note and version/runtime preflight notes are injected.
- **Adapter-specific provider note**: present in every generated Kiro skill.
- **Runtime-missing or unsupported-mode message**: unknown aliases report the
  known experimental adapter list before runtime provisioning.

## Packaged Install Validation

- **Command under test**: `node cli/test/experimental-install.mjs`.
- **Default install confirmed not to include this adapter**: yes; experimental
  adapters are never installed by default.
- **Explicit `--experimental <agent>` install result**: yes; explicit
  `--experimental kiro` install copies the selected Kiro payload to
  `~/.kiro/skills/`.
- **Manifest ownership entries observed**: yes; manifest schema 2 records
  `adapterId: kiro`, `experimental: true`, and package version metadata.
- **Update/prune behavior observed**: the shared experimental manifest/update
  path is exercised by the Pi prune test; Kiro install ownership is exercised
  directly.
- **Supported-agent surfaces remained unchanged**: yes; claim-surface tests
  assert experimental runtime adapters do not enter `SUPPORTED_AGENTS`.

## Parity Run

- **Skills exercised**: packaged install smoke around generated `task-brief`
  payload; no live Kiro skill invocation.
- **Scenario limits**: runtime execution, live prompt handling, and real Kiro
  permission behavior were not exercised.
- **Audit result**: adapter validation is covered by the CLI smoke tests and
  build check; planning audit remains the release-gate check.
- **Interview-protocol judgment**: mapped through the standard prose interview
  provider note.
- **Known residual differences**: live Kiro skill discovery and behavior remain
  unknown until a Kiro runtime parity pass is run.
- **Graduation recommendation**: remain experimental.
