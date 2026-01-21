# ASR CLI

Manage agent “skills” across tools without drift: registry + validation + manifests + IDE adapters.

## TL;DR

- **One source of truth:** skills live in their original directories; ASR tracks them in a registry (no duplication).
- **Catch drift early:** validate `SKILL.md` + structure, and track changes over time with manifests.
- **Bridge tool differences:** generate thin adapters for Cursor / Windsurf / Codex-style setups even when their root dirs and invocation syntax differ.

Agent skills are an open spec, but different agentic providers and IDEs tend to:
- store skills in different **root directories**, and
- use different **invocation surfaces/syntax** (commands vs workflows, reserved names, etc.).

ASR’s job is to keep your skills “canonical” and make integrations *point at them* instead of copying them everywhere.

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

## Why this exists

If you keep a growing library of skills, the painful parts aren’t the first few skills — it’s the long-term maintenance:

- **Drift:** you edit a skill, but the “wrapper” copied into an IDE directory is stale.
- **Mismatch:** one environment expects commands, another expects workflows, another expects a different root directory.
- **Silent breakage:** renamed directories, missing `SKILL.md`, bad frontmatter, missing Windows equivalents for scripts, etc.

ASR tackles this with a registry + validation + manifests, and (optionally) generated adapters.

## Core concepts

### Registry (source of truth)

ASR keeps a registry at `~/.skills/registry.toml` that records *where the canonical skill directories live*.

- No copying required to “register” a skill
- Enables `validate --all`, `status`, `sync`, and adapter generation against a consistent list of skills

### Validation (make problems explicit)

Run validation against a single directory or everything registered:

```bash
asr validate /path/to/skill-dir
asr validate --all
asr validate --all --strict
```

Validation checks `SKILL.md` + frontmatter and a handful of structural rules (errors vs warnings with codes).

### Manifests (track change over time)

ASR stores per-skill manifests (JSON) under `~/.skills/manifests/` so you can tell whether a skill is:
- `valid` (matches manifest),
- `modified` (content changed),
- `missing` (source path gone),
- `untracked` (registered but no manifest yet).

Useful commands:

```bash
asr sync          # create manifests where missing
asr status        # show current state (valid/modified/missing/untracked)
asr sync --update # update manifests for modified skills
asr sync --prune  # remove registry entries whose source path is missing
asr clean         # clean orphaned manifests, missing-source skills, etc.
```

### Adapters (bridge tool-specific formats without copying)

Different tools often have different “skill roots” and invocation formats, so a single universal “/skill” command syntax rarely works everywhere.

ASR can generate **thin adapters** (small files) for environments like Cursor / Windsurf / Codex-style setups that *delegate to your canonical skill directories* (from the registry). This prevents the common “copied wrapper drift” problem.

```bash
asr adapter --output-dir /path/to/project
asr adapter cursor --output-dir /path/to/project
asr adapter windsurf --output-dir /path/to/project
asr adapter codex --output-dir /path/to/project
```

## Usage

```bash
# Show help
asr --help

# List registered skills
asr list

# Register a skill
asr add /path/to/skill-dir
asr add aux/*                                 # glob paths
asr add /path/to/skill-dir --strict  # Fail on warnings
asr add -r /path/to/root             # Recursively add all valid skills

# Remove a skill
asr rm skill-name
asr rm /path/to/skill-dir
asr rm sniff-bloaters sniff-abusers            # multiple
asr rm "sniff-*"                               # glob by name
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
