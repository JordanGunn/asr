# `oasr clone`

Clone skills from the registry to a target directory. Supports glob patterns and works with both local and remote skills.

> **note**  
> `oasr clone` provides an open-closed extension mechanism for using skills with any agentic provider.

## Usage

```bash
oasr clone skill-name
oasr clone skill-name -d /path/to/project
oasr clone "git-*"                    # Glob pattern
oasr clone skill-one skill-two        # Multiple skills
```

## Options

- `-d, --dest DIR` — Destination directory (default: current directory)
- `--quiet` — Suppress informational output
- `--json` — Output results in JSON format

## Features

### Glob Pattern Support

Clone multiple skills matching a pattern:
```bash
oasr clone "python-*"     # All Python-related skills
oasr clone "*-api"        # All API-related skills
```

### Remote Skill Fetching

Remote skills are automatically fetched during clone:
```bash
oasr registry add https://github.com/user/skill-repo
oasr clone my-remote-skill
```

### Tracking Metadata

Cloned skills include tracking metadata in their frontmatter:
```yaml
---
metadata:
  oasr:
    hash: "abc123..."
    source: "~/.oasr/registry/my-skill"
    synced_at: "2026-02-01T12:00:00Z"
---
```

This enables:
- `oasr diff` — Check if cloned skills are up-to-date
- `oasr sync` — Update outdated skills from registry

## Examples

### Basic Clone
```bash
# Clone to current directory
oasr clone csv-analyzer

# Clone to specific project
oasr clone csv-analyzer -d ~/projects/data-pipeline
```

### Bulk Clone
```bash
# Clone multiple skills
oasr clone python-test-generator python-docstring-writer

# Clone with glob patterns
oasr clone "test-*" -d ~/projects/testing-tools
```

### Integration with Adapters

After cloning, use with IDE adapters:
```bash
# Clone skills first
oasr clone my-skill

# Then adapt for your IDE
oasr adapter cursor
```

## Related Commands

- [`oasr exec`](EXEC.md) — Execute skills as CLI tools (no cloning needed)
- [`oasr registry add`](REGISTRY.md) — Add skills to registry before cloning
- [`oasr diff`](DIFF.md) — Check status of cloned skills
- [`oasr sync`](SYNC.md) — Update cloned skills from registry

## Migration from `oasr use`

`oasr clone` replaces the deprecated `oasr use` command. The functionality is identical—only the name has changed for clarity:

```bash
# Old (deprecated)
oasr use my-skill

# New
oasr clone my-skill
```

> **warning**  
> `oasr use` will be removed in v0.5.0. Update your scripts and workflows to use `oasr clone`.
