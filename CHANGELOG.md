# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/OWNER/REPO/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/REPO/releases/tag/v0.1.0
