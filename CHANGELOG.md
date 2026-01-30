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
- **`oasr update` command** — self-update ASR tool from GitHub
  - Pulls latest changes with `git pull --ff-only`
  - Displays truncated changelog with commit count and file statistics
  - Reinstalls package automatically (unless `--no-reinstall` specified)
  - Suppresses verbose git output with custom messages
  - JSON output support for automation
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
- Comprehensive test suite (41 tests covering new functionality)
- Documentation split into `docs/QUICKSTART.md` and `docs/COMMANDS.md`
- Screenshots gallery in `docs/images/` for visual documentation

### Changed
- **BREAKING**: `oasr adapter` now always copies skills locally (old `--copy` flag is deprecated)
- `--copy` flag kept for backward compatibility but has no effect
- Skills are always copied to `.{ide}/skills/` directories for consistency
- Adapter files now use relative paths to local skill copies
- Remote skills fetch on-demand (not stored permanently after `oasr add`)
- `oasr list` output redesigned with box-drawing characters, shortened paths, and `--verbose` flag
- Renamed `src/oasr_cmd/` to `src/commands/` for clarity
- Packaging migrated to a `src/` layout
- Build backend migrated to Hatch (hatchling)
- CLI binary renamed to `oasr` (with `skills` kept as a compatibility alias)
- README simplified to focus on problem/solution; details moved to docs

### Fixed
- W002 validation warning no longer fires for remote skills during registration
- Remote reachability check now validates specific path, not just repository
- URL preservation in manifests (no longer mangled by Path conversion)
- Graceful handling of GitHub API rate limits (operations continue for other skills)
- Smart caching prevents redundant fetches during adapter operations

## [0.1.0] - 2026-01-21

### Added
- Initial CLI with registry, discovery, validation, adapters, and manifests.

[Unreleased]: https://github.com/OWNER/REPO/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/REPO/releases/tag/v0.1.0
