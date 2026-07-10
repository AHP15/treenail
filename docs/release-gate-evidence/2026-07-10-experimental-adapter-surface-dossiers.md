# Experimental Adapter Surface Dossiers - 2026-07-10

These dossiers are the pre-implementation source record for D-034. They are
not support claims. Each candidate remains an unvalidated experimental runtime
adapter until its packaged `--experimental <agent>` validation record passes the
D-031 support bar.

## Pi Coding Agent

- **Status**: candidate runtime adapter; unvalidated.
- **Official sources observed**:
  - https://pi.dev/
- **Install path**: The product page documents curl, PowerShell, npm, pnpm, and
  bun install commands for `@earendil-works/pi-coding-agent`.
- **Instruction/skill format**: Pi advertises support for skills and
  `AGENTS.md`. The page says project instructions are loaded from
  `~/.pi/agent/`, parent directories, and the current directory; it also
  describes skills as capability packages with instructions and tools.
- **Config directory**: Source-backed known path: `~/.pi/agent/` for startup
  `AGENTS.md`. Exact Treenail adapter write path remains to be validated in
  T-061.
- **CLI/TUI/headless mode**: Source-backed modes: interactive TUI, print/JSON
  mode via `pi -p`, RPC, and SDK.
- **Permission or sandbox behavior**: The product page says Pi has no built-in
  permission popups and points users to containerization or extensions for
  confirmation flows. Treat permission/sandbox behavior as adapter-sensitive
  until T-061 validates the concrete package.

## Cursor

- **Status**: candidate runtime adapter; unvalidated.
- **Official sources observed**:
  - https://cursor.com/docs
  - https://cursor.com/docs/skills
- **Install path**: Cursor docs are the current official docs landing surface.
  Exact CLI/package install path was not established by the source page and
  remains to be validated in T-063.
- **Instruction/skill format**: The docs landing title advertises Cursor docs
  for Agent, Rules, MCP, Skills, and CLI, and the current docs expose an Agent
  Skills page. Exact file layout and required frontmatter remain live-runtime
  validation items in T-063.
- **Config directory**: Unknown from the observed official source; validate
  before writing any adapter payload.
- **CLI/TUI/headless mode**: Unknown from the observed official source; validate
  before enabling packaged `--experimental cursor`.
- **Permission or sandbox behavior**: Unknown from the observed official
  source; validate before enabling packaged `--experimental cursor`.

## Kimi Code CLI

- **Status**: candidate runtime adapter; unvalidated.
- **Official sources observed**:
  - https://www.kimi.com/code
  - https://www.kimi.com/code/docs/en/
  - https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html
  - https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/config-files.html
  - https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/data-locations.html
- **Install path**: Kimi Code documents install via
  `curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash` on macOS/Linux
  and a PowerShell install command on Windows. After installation, the command
  is `kimi`.
- **Instruction/skill format**: Kimi Code CLI supports Agent Skills as Markdown
  documents with YAML frontmatter. Directory form uses `<name>/SKILL.md`;
  directory-form skills require explicit `name` and `description`, and support
  fields including `type`, `whenToUse`, `disableModelInvocation`, and
  `arguments`.
- **Config directory**: Kimi Code CLI reads `~/.kimi-code/config.toml` by
  default, overridable with `KIMI_CODE_HOME`.
- **Skill directories**: User-level skills scan `$KIMI_CODE_HOME/skills/`
  (default `~/.kimi-code/skills/`) and `~/.agents/skills/`. Project-level
  skills scan `.kimi-code/skills/` and `.agents/skills/`.
- **CLI/TUI/headless mode**: Kimi Code CLI runs in the terminal as `kimi`; the
  official overview says it can read code, edit files, execute commands, search
  the web, and autonomously complete development tasks.
- **Permission or sandbox behavior**: The config docs expose
  `default_permission_mode` and `permission.rules`. Exact Treenail mapping must
  be validated in T-062.

## Kiro

- **Status**: candidate runtime adapter; unvalidated.
- **Official sources observed**:
  - https://kiro.dev/docs/
  - https://kiro.dev/docs/cli/
  - https://kiro.dev/docs/skills/
  - https://kiro.dev/docs/steering/
  - https://kiro.dev/docs/cli/custom-agents/
  - https://kiro.dev/docs/specs/
  - https://kiro.dev/docs/hooks/
- **Install path**: Kiro CLI documents install via
  `curl -fsSL https://cli.kiro.dev/install | bash`, then `kiro-cli` from a
  project directory.
- **Instruction/skill format**: Kiro supports Agent Skills as folders
  containing a required `SKILL.md` file, with required `name` and `description`
  frontmatter. Kiro also supports steering Markdown files and `AGENTS.md`.
- **Config directory**: Source-backed global skills path: `~/.kiro/skills/`;
  source-backed workspace skills path: `.kiro/skills/`. Source-backed global
  steering path: `~/.kiro/steering/`; source-backed workspace steering path:
  `.kiro/steering/`.
- **CLI/TUI/headless mode**: Kiro CLI supports interactive terminal use and the
  official CLI page lists headless automation through API key authentication.
- **Permission or sandbox behavior**: Kiro CLI custom-agent docs say the
  default CLI requires user confirmation for most operations and custom agents
  can pre-approve or limit tools. Exact Treenail mapping must be validated in
  T-064.

## Graduation Freshness Rule

Before any candidate graduates, its packaged validation record must re-confirm
the source facts above on the validation date, cite the current official URLs,
and name the agent version, model/provider where applicable, channel, OS, and
interaction mode.
