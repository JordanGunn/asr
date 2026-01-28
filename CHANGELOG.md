# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `asr help` subcommand for viewing command help (e.g., `asr help list`).
- Glob pattern support for `asr use` (e.g., `asr use "git-*"`).
- **Copilot adapter** — generates `.github/copilot-instructions.md` with managed skill sections.
- **Claude adapter** — generates `.claude/commands/*.md` files.
- Cross-platform installation scripts: `install.sh` and `install.ps1`.
- Test suite with pytest (18 tests covering new functionality).
- Documentation split into `docs/QUICKSTART.md` and `docs/COMMANDS.md`.

### Changed
- `asr list` output redesigned with box-drawing characters, shortened paths, and `--verbose` flag.
- Renamed `src/asr_cmd/` to `src/commands/` for clarity.
- Packaging migrated to a `src/` layout.
- Build backend migrated to Hatch (hatchling).
- CLI binary renamed to `asr` (with `skills` kept as a compatibility alias).
- README simplified to focus on problem/solution; details moved to docs.

## [0.1.0] - 2026-01-21

### Added
- Initial CLI with registry, discovery, validation, adapters, and manifests.

[Unreleased]: https://github.com/OWNER/REPO/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/REPO/releases/tag/v0.1.0
