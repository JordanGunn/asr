# ASR CLI

CLI for managing agent skills across IDE integrations (Cursor, Windsurf, Codex).

## Installation

```bash
cd asr
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Global Installation

If you want `asr` (and the compatibility alias `skills`) available globally on your machine:

- macOS/Linux: run `./install.sh`
- Windows (PowerShell): run `.\install.ps1`

These scripts install into an isolated virtual environment and place shims in a user-level bin directory
(by default `~/.local/bin` on macOS/Linux, and `%LOCALAPPDATA%\asr\bin` on Windows).

## Usage

```bash
# Show help
asr --help

# List registered skills
asr list

# Register a skill
asr add /path/to/skill-dir
asr add /path/to/skill-dir --strict  # Fail on warnings
asr add -r /path/to/root             # Recursively add all valid skills

# Remove a skill
asr rm skill-name
asr rm /path/to/skill-dir
asr rm -r /path/to/root      # Recursively remove all skills under path

# Copy skills to target directory (no registry modification)
asr use dewey grape                # Copy to current directory
asr use dewey grape -d /path/to/project

# Find skills recursively
asr find /path/to/search
asr find /path/to/search --add  # Also register found skills

# Validate skills
asr validate /path/to/skill-dir
asr validate --all
asr validate --all --strict  # Treat warnings as errors

# Generate IDE files
asr adapter                          # All default targets
asr adapter cursor                   # Cursor only
asr adapter windsurf                 # Windsurf only
asr adapter codex                    # Codex only
asr adapter --exclude skill1,skill2  # Exclude specific skills
asr adapter --output-dir /path/to/project
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--config <path>` | Override config file location |
| `--json` | Output in JSON format |
| `--quiet` | Suppress info/warnings |
| `--version` | Show version |

## Configuration

Configuration is stored in `~/.skills/config.toml`:

```toml
[validation]
reference_max_lines = 500  # W007 threshold
strict = false             # Treat warnings as errors by default

[adapter]
default_targets = ["cursor", "windsurf"]  # Default adapter targets
```

## Registry

Registered skills are stored in `~/.skills/registry.toml`.

## Changelog

See `CHANGELOG.md`.

## Validation Rules

### Errors

| Code | Description |
|------|-------------|
| E001 | Missing SKILL.md |
| E002 | Malformed YAML frontmatter |
| E003 | Missing `name` field |
| E004 | Missing `description` field |
| E005 | `name` violates kebab-case |

### Warnings

| Code | Description |
|------|-------------|
| W001 | Empty description |
| W002 | Directory name != frontmatter name |
| W003 | Path contains spaces/special chars |
| W004 | Only scripts/ directory present |
| W005 | Empty file in references/assets/scripts |
| W006 | .sh without .ps1 (or vice versa) |
| W007 | Reference file exceeds line threshold |

### Info

| Code | Description |
|------|-------------|
| I001 | Registered path no longer exists |
