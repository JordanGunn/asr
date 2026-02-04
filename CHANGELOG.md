# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2] - 2026-02-04

### Breaking
- **Removed deprecated commands** — `oasr use` and `oasr clean` have been removed. Use `oasr clone` and `oasr registry prune` instead.

### Changed
- **Update command** — `oasr update` now checks PyPI and upgrades via `uv`/`pip` instead of git pulls.

### Fixed
- **Zsh completions** — Removed erroneous execution in completion script that broke autoload.

### Added
- **Completion install shortcut** — `oasr completion <shell> --install` runs the install flow.

## [0.6.1] - 2026-02-04

### Fixed
- **Codex exec trust check** — Always pass `--skip-git-repo-check` for Codex to avoid trusted directory errors.

## [0.6.0] - 2026-02-03

### Added
- **🧭 Profile selection command** — New `oasr profile` command with interactive selector or explicit profile selection.
- **📄 Profile file support** — Auto-load `~/.oasr/profile/*.toml` profiles with inline config overrides.
- **🔧 Config subcommands** — `oasr config agent|validation|adapter|oasr|profiles` for focused views.
- **✅ Config validation and reference** — `oasr config validate` and `oasr config man` helpers.
- **Default profiles** — New built-ins: `strict`, `dev`, `unsafe`.

### Changed
- **Profiles subsystem** — New `profiles` subpackage with loaders, validation, and summary helpers.
- **Config listing** — Lists profiles with compact capability summaries and completions setting.

### Documentation
- **Config + profile docs** — Updated configuration guides and new `docs/commands/PROFILE.md`.

## [0.5.2] - 2026-02-02

### Added
- **⌨️ Shell Completion Support** — Intelligent tab completion for all major shells
  - Cross-platform support: Bash, Zsh, Fish, PowerShell
  - `oasr completion install` — Auto-detect shell and install completions
  - `oasr completion <shell>` — Output completion script for specific shell
  - Dynamic completions: skill names, agents, profiles fetched live from registry
  - Command, subcommand, and flag completion for all OASR commands
  - Smart shell detection (platform + $SHELL environment variable)
  - Installation paths: `~/.bash_completion.d/`, `~/.zsh/completion/`, `~/.config/fish/completions/`, `~/.config/powershell/`
  - Backup mechanism: existing completions backed up before overwrite
  - `--force` and `--dry-run` flags for installation control
  - `oasr completion uninstall` — Remove installed completions
  - Configuration support: `oasr.completions` config option
- **🧪 Comprehensive E2E Tests** — 16 new end-to-end tests covering all commands
  - Registry subcommands (list, sync, prune)
  - Diff, sync, info, validate, clean commands
  - Adapter, find, help commands
  - Total test count: 282 tests (all passing)
  - Ensures no regressions in existing functionality
- **⚠️ Exec Unsafe Pass-through** — Optional unsafe mode forwarding for agent CLIs
  - `oasr exec --unsafe` forwards `--skip-git-repo-check` to Codex
  - `oasr exec --unsafe` forwards `--dangerously-skip-permissions` to Claude
  - Unsupported agents (Copilot/OpenCode) emit a warning with guidance

### Documentation
- **[docs/commands/COMPLETION.md](docs/commands/COMPLETION.md)**: Complete completion command reference
  - Installation instructions for all shells
  - Shell-specific configuration notes
  - Troubleshooting guide
  - Examples and usage patterns
- **[README.md](README.md)**: Added Shell Completions section with quickstart
- **[docs/commands/.INDEX.md](docs/commands/.INDEX.md)**: Added completion to command index
- **[docs/commands/EXEC.md](docs/commands/EXEC.md)**: Documented `--unsafe` and trusted directory guidance

### Technical
- **New module**: `src/commands/completion.py` (259 lines) with shell detection and installation
- **Completion scripts**: 4 shell-specific scripts (~691 lines total)
  - `src/completions/bash.sh` (197 lines)
  - `src/completions/zsh.sh` (259 lines) with descriptions
  - `src/completions/fish.fish` (120 lines) with native Fish syntax
  - `src/completions/powershell.ps1` (115 lines) with ArgumentCompleter
- **45 new tests**: 29 completion tests + 16 E2E tests
- **Dynamic completion**: Scripts invoke `oasr` commands for live data (registry list, config keys)
- **Cross-platform**: Handles Windows, macOS, Linux path conventions

### Quality of Life
- Tab completion reduces typing and prevents typos
- Discovery: see available skills, agents, and profiles at your fingertips
- Professional UX: OASR now feels like a polished CLI tool
- Backward compatible: no changes to existing commands

## [0.5.1] - 2026-02-02

### Added
- **🌍 Environment Variable Support** — Full OASR_* environment variable support for all configuration
  - Naming convention: `OASR_<SECTION>_<KEY>` (e.g., `OASR_AGENT`, `OASR_PROFILE`)
  - Type-aware parsing: bool, int, list (comma-separated), string
  - Clear precedence: CLI flags > env vars > config file > defaults
  - 17 documented environment variables
- **✅ Enhanced Config Validation** — Early validation with helpful error messages
  - `oasr config set` validates agent names against available drivers
  - Profile reference validation (checks if profile exists)
  - `--force` flag to bypass validation when needed
  - Dotted notation support: `validation.strict`, `adapter.default`
  - Suggestions in error messages: "Invalid agent 'foo'. Valid agents: codex, copilot..."
- **📚 Configuration Documentation Restructure** — Progressive disclosure documentation
  - New `docs/configuration/` directory with 12 files (~37KB)
  - Navigation manifest: `.INDEX` file for documentation structure
  - 7 detailed guides: Overview, Agent, Profiles, Validation, Adapter, Env Vars, Precedence
  - 4 example configs: Minimal, Development, CI/CD, Production
  - Easy-to-find specific information with cross-references

### Changed
- **Config loading**: Now accepts `cli_overrides` parameter for precedence merging
- **Config command**: Enhanced validation and better error messages
- **Documentation**: `docs/commands/CONFIG.md` updated with pointers to new structure

### Technical
- **New module**: `src/config/env.py` with parsing, type coercion, and merging logic
- **50 new tests**: 40 env var tests + 10 integration tests (287 total tests passing)
- **Backward compatible**: All existing functionality preserved
- **Type safety**: Enhanced type checking and validation throughout

### Documentation
- **[docs/configuration/](docs/configuration/README.md)**: New comprehensive configuration guide
- **[Environment Variables](docs/configuration/environment-variables.md)**: Complete OASR_* reference
- **[Precedence](docs/configuration/precedence.md)**: Detailed precedence rules and examples
- **[Examples](docs/configuration/examples/)**: 4 ready-to-use configuration examples

## [0.5.0] - 2026-02-02

### Added
- **🔒 Execution Policy System** — Host-level security boundaries for `oasr exec`
  - Policy profiles define what agents can and cannot do
  - Conservative safe defaults (fail closed)
  - User-defined custom profiles in `config.toml`
  - Pre-execution confirmation for risky operations
  - Risk triggers: stdin, file prompts, non-safe profiles, network/env/shell access
- **New CLI flags for `oasr exec`**:
  - `--profile <name>` — Choose execution policy profile
  - `-y/--yes` — Skip confirmation prompt
  - `--confirm` — Force confirmation even for safe operations
- **Configuration support for policies**:
  - `[oasr]` section with `default_profile` setting
  - `[profiles.<name>]` tables for custom profiles
  - Policy field validation in config schema
  - Built-in "safe" profile with conservative defaults

### Changed
- **Security model**: `oasr exec` now requires explicit confirmation for risky execution contexts
- **Config schema**: Extended to support execution policy profiles

### Security
- **Prompt injection mitigation**: Policy enforcement reduces impact of malicious skill instructions
- **Sensitive file protection**: Default deny list includes `~/.ssh`, `~/.aws`, `~/.gnupg`, `.env`, etc.
- **Execution boundaries**: Clear limits on filesystem access, network, environment variables, and shell commands
- **User awareness**: Policy summary shown before risky executions
- **Fail-closed design**: Missing/malformed config falls back to safe defaults

### Documentation
- **[EXEC.md](docs/commands/EXEC.md)**: Added comprehensive Security Model section
- **[CONFIG.md](docs/commands/CONFIG.md)**: Added Execution Policy Profiles documentation
- **Policy examples**: Multiple profile configurations for different use cases

### Technical
- **New module**: `src/policy/` subpackage with clean API (Profile, load, assess_risk, prompt_confirmation)
- **41 new tests**: 30 policy tests + 11 config profile tests
- **Test coverage**: 187 total tests passing (all existing tests still pass)
- **Backward compatible**: No breaking changes to existing commands

## [0.4.2] - 2026-02-01

### Added
- **registry prune subcommand**: Added `oasr registry prune` to align with registry command taxonomy

### Changed
- **clean command**: Deprecated `oasr clean` in favor of `oasr registry prune` (will be removed in v0.6.0)
- **documentation**: Updated REGISTRY.md with prune subcommand documentation and usage examples

## [0.4.1] - 2026-02-01

### Fixed
- **exec command**: Fixed `CompletedProcess` attribute error where code incorrectly referenced `.success`, `.output`, and `.error` attributes that don't exist. Now correctly uses `.returncode`
- **clone documentation**: Removed non-existent `-r, --recursive` flag from CLONE.md documentation

## [0.4.0] - 2026-01-31

### Added
- **🚀 `oasr exec` command** — Execute skills as CLI tools from anywhere
  - Run skills with agent-driven execution: `oasr exec <skill> -p "prompt"`
  - Multiple prompt input methods: inline (`-p`), file (`-i`), or stdin (pipe)
  - Agent selection via flag (`--agent`) or config default
  - Graceful error handling with helpful guidance
- **`oasr config` command** — Manage OASR configuration
  - `config set <key> <value>` — Set config values (e.g., default agent)
  - `config get <key>` — Retrieve config values
  - `config list` — Display all configuration with agent availability
  - `config path` — Show config file location
- **`oasr clone` command** — Renamed from `oasr use` for clarity
  - Clones skills from registry to current directory
  - Same functionality as deprecated `oasr use`
- **Agent driver system** — Support for multiple AI agent CLIs
  - Codex: `codex exec "<prompt>"`
  - GitHub Copilot: `copilot -p "<prompt>"`
  - Claude CLI: `claude <prompt> -p`
  - OpenCode: `opencode run "<prompt>"`
  - Auto-detection of available agent binaries
  - Extensible driver architecture for adding new agents
- **Multi-skill repository support** — Detect and add multiple skills from one repo
  - `oasr registry add <repo-url>` automatically finds all SKILL.md files
  - Interactive prompt for bulk addition: "Found 3 skills. Add all? [Y/n]"
  - Each skill registered with proper subdirectory URL

### Changed
- **Config system refactored** — Moved to subpackage architecture
  - `src/config/` subpackage with schema validation
  - New `agent.default` field in config for default agent selection
  - TOML serialization improved (strips None values)
  - Backward compatible with existing configs

### Deprecated
- **`oasr use` command** — Use `oasr clone` instead
  - Shows deprecation warning (suppressible with `--quiet` or `--json`)
  - Warning: "This command will be removed in v0.5.0"
  - Fully functional shim delegates to `oasr clone`

### Fixed
- Config validation now properly handles None values in TOML serialization

## [0.3.4] - 2026-02-01

### Fixed
- Enable PyPI trusted publishing workflow and update package metadata for `oasr`

## [0.3.3] - 2026-01-30

### Fixed
- **Critical**: Adapters now inject tracking metadata when copying skills
  - Skills copied by `oasr adapter cursor`, `claude`, etc. now include `metadata.oasr`
  - Enables `oasr diff` and `oasr sync` to work with adapter-copied skills
  - Graceful degradation if manifest cannot be loaded

## [0.3.2] - 2026-01-30

### Fixed
- **Critical**: Adapters now inject tracking metadata when copying skills
  - Skills copied by `oasr adapter cursor`, `claude`, etc. now include `metadata.oasr`
  - Enables `oasr diff` and `oasr sync` to work with adapter-copied skills
  - Graceful degradation if manifest cannot be loaded

## [0.3.1] - 2026-01-30

### Fixed
- **Critical**: Fix `oasr registry add` and `oasr registry rm` missing arguments
  - Error: "'Namespace' object has no attribute 'recursive'"
  - Error: "'Namespace' object has no attribute 'targets'"
  - Added missing `-r/--recursive` flag to `registry add` and `registry rm`
  - Added missing `--strict` flag to `registry add`
  - Fixed `registry rm` argument name from `names` to `targets` (for glob pattern support)
  - Added missing `--quiet` flag to `registry rm`

## [0.3.0] - 2026-01-30

### Added
- **Metadata tracking via frontmatter** — Skills now track their source via `metadata.oasr` field in SKILL.md
  - Eliminates need for external tracking files (.oasr directories)
  - Spec-compliant (Open Agent Skill metadata field)
  - Tracks: content hash, source path/URL, sync timestamp
- **`oasr diff` command** — Show status of tracked skills (up-to-date, outdated, modified, untracked)
- **`oasr sync` command** — Refresh outdated tracked skills from registry
- **`oasr registry` command** — New unified registry management
  - `oasr registry` (default) - Validate registry manifests
  - `oasr registry list` - List registered skills
  - `oasr registry add` - Add skills to registry
  - `oasr registry rm` - Remove skills from registry
  - `oasr registry sync` - Sync with remote repositories

### Changed
- **BREAKING**: Complete CLI taxonomy redesign for clarity and flexibility
  - `oasr add` → `oasr registry add`
  - `oasr rm` → `oasr registry rm`
  - `oasr list` → `oasr registry list`
  - `oasr sync` → `oasr registry` (validation)
  - `oasr sync --update` → `oasr registry sync`
  - `oasr status` → `oasr registry -v`
- **BREAKING**: `oasr use` now injects tracking metadata automatically
- Skills copied locally now contain self-describing metadata for drift detection

### Removed
- **BREAKING**: Removed standalone `add`, `rm`, `list`, `status` commands (moved to `registry` subcommand)

## [0.2.0] - 2026-01-30

### Added
- **Remote skills support** — register skills from GitHub and GitLab URLs
  - `oasr add` now accepts GitHub/GitLab repository URLs
  - `GITHUB_TOKEN` and `GITLAB_TOKEN` environment variable support for authentication
  - Remote reachability checks in `oasr sync`
  - Automatic fetching and copying of remote skills during `adapter` and `use` operations
  - Smart caching to avoid redundant API calls
  - Graceful failure handling for rate limits and network errors
  - **Parallel fetching** — up to 4 concurrent remote skill downloads
  - **Progress indicators** — real-time feedback during remote operations
- **`oasr update` command** — self-update ASR tool from GitHub
  - Pulls latest changes with `git pull --ff-only`
  - Displays truncated changelog with commit count and file statistics
  - Reinstalls package automatically (unless `--no-reinstall` specified)
  - Suppresses verbose git output with custom messages
  - JSON output support for automation
- **`oasr info` command** — detailed skill information display
  - Shows skill metadata: description, source, type, status, files, hash
  - Support for `--files` flag to list all skill files
  - JSON output support with `--json`
  - Clean formatted output with visual separators
- User feedback during remote operations ("Registering from GitHub...")
- `skillcopy` module for unified skill copying (local and remote)
- `remote` module for GitHub/GitLab API integration with full error handling
- URL parsing and validation for GitHub and GitLab
- Skill name derivation from remote URLs (kebab-case format)
- `oasr help` subcommand for viewing command help (e.g., `oasr help list`)
- Glob pattern support for `oasr use` (e.g., `oasr use "git-*"`)
- **Copilot adapter** — generates `.github/copilot-instructions.md` with managed skill sections
- **Claude adapter** — generates `.claude/commands/*.md` files
- Cross-platform installation scripts: `install.sh` and `install.ps1`
  - Automatic migration from `~/.skills/` to `~/.oasr/`
  - Safe, idempotent migration (only moves oasr-managed files)
- Comprehensive test suite (41 tests covering new functionality)
- Documentation reorganization:
  - Split into `docs/QUICKSTART.md` and `docs/commands/`
  - Validation documentation moved to `docs/validation/`
  - Screenshots gallery in `docs/.images/`
  - Individual command pages with examples

### Changed
- **BREAKING**: `oasr adapter` now always copies skills locally (old `--copy` flag is deprecated)
- **BREAKING**: Data directory changed from `~/.skills/` to `~/.oasr/`
  - Automatic migration during installation
  - Preserves `~/.skills/` if other files exist
- `--copy` flag kept for backward compatibility but has no effect
- Skills are always copied to `.{ide}/skills/` directories for consistency
- Adapter files now use relative paths to local skill copies
- Remote skills fetch on-demand (not stored permanently after `oasr add`)
- Remote operations now show progress and fetch in parallel (3-4x faster)
- `oasr info` simplified to use positional argument (`oasr info <skill-name>`)
- `oasr list` output redesigned with box-drawing characters, shortened paths, and `--verbose` flag
- Renamed `src/oasr_cmd/` to `src/commands/` for clarity
- Packaging migrated to a `src/` layout
- Build backend migrated to Hatch (hatchling)
- CLI binary renamed to `oasr` (with `skills` kept as a compatibility alias)
- README rebranded to "OASR" (Open Agent Skill Registry)
- README simplified to focus on problem/solution; details moved to docs

### Fixed
- W002 validation warning no longer fires for remote skills during registration
- Remote reachability check now validates specific path, not just repository
- URL preservation in manifests (no longer mangled by Path conversion)
- Graceful handling of GitHub API rate limits (operations continue for other skills)
- Smart caching prevents redundant fetches during adapter operations
- Error messages now include helpful suggestions (e.g., "Try: oasr list")

### Performance
- **Parallel remote skill fetching** — 3-4x faster with multiple remote skills
- **Smart caching** — skip unchanged remote skills during adapter operations
- **Thread-safe operations** — concurrent downloads with proper synchronization

## [0.1.0] - 2026-01-21

### Added
- Initial CLI with registry, discovery, validation, adapters, and manifests.

[Unreleased]: https://github.com/JordanGunn/asr/compare/v0.3.2...HEAD
[0.3.2]: https://github.com/JordanGunn/asr/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/JordanGunn/asr/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/JordanGunn/asr/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/JordanGunn/asr/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/JordanGunn/asr/releases/tag/v0.1.0
