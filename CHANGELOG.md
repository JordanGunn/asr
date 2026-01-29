# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `oasr help` subcommand for viewing command help (e.g., `oasr help list`).
- Glob pattern support for `oasr use` (e.g., `oasr use "git-*"`).
- **Copilot adapter** — generates `.github/copilot-instructions.md` with managed skill sections.
- **Claude adapter** — generates `.claude/commands/*.md` files.
- Cross-platform installation scripts: `install.sh` and `install.ps1`.
- Test suite with pytest (18 tests covering new functionality).
- Documentation split into `docs/QUICKSTART.md` and `docs/COMMANDS.md`.

### Changed
- `oasr list` output redesigned with box-drawing characters, shortened paths, and `--verbose` flag.
- Renamed `src/oasr_cmd/` to `src/commands/` for clarity.
- Packaging migrated to a `src/` layout.
- Build backend migrated to Hatch (hatchling).
- CLI binary renamed to `oasr` (with `skills` kept as a compatibility alias).
- README simplified to focus on problem/solution; details moved to docs.

## [0.2.0] - 2026-01-29

### Changed
- `oasr sync` now applies updates by default. When a registered skill is detected as modified, `oasr sync` will validate and sync the registry manifest and propagate changes to recorded per-project clones automatically.
- The previous opt-in flag `--update` has been removed in favor of `--registry-only`. Use `--registry-only` to check registry manifests without applying updates to manifests or propagating changes to cloned copies.
- Sync now records per-project cloned copies under `.skills/manifests/<skill>.clones.manifest.json` and will attempt to update those copies when the source is synchronized.
- Documentation and CLI help updated to reflect the new default sync behavior and the `--registry-only` option.

## [0.1.0] - 2026-01-21

### Added
- Initial CLI with registry, discovery, validation, adapters, and manifests.

[Unreleased]: https://github.com/OWNER/REPO/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/OWNER/REPO/releases/tag/v0.2.0
[0.1.0]: https://github.com/OWNER/REPO/releases/tag/v0.1.0
