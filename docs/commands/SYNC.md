# `oasr sync`

Refresh outdated tracked skills from the registry.

## Overview

The `oasr sync` command updates local copies of skills that have been modified in the registry. It only updates skills with tracking metadata (copied via `oasr use`).

## Usage

```bash
oasr sync                    # Scan current directory, update outdated skills
oasr sync /path/to/project   # Scan specific path
oasr sync --force            # Overwrite modified skills (default: skip)
oasr sync --json             # JSON output
```

## Behavior

- **Scans for tracked skills** - Finds all `SKILL.md` files with `metadata.oasr`
- **Checks registry** - Compares tracked hash with current registry hash
- **Updates outdated** - Re-copies skills where registry is newer
- **Skips modified** - By default, leaves locally-modified skills alone
- **Force overwrite** - Use `--force` to overwrite modified skills

## Example Output

```bash
$ oasr sync

Scanning /home/user/project for tracked skills...

Found 3 tracked skills:
  • my-skill (up-to-date, skipping)
  • python-analyzer (outdated, updating...)
    ✓ Refreshed from github.com/user/repo/skills/python-analyzer
  • json-parser (modified, skipping - use --force to overwrite)

Updated: 1
Skipped: 2
```

## Force Overwrite

To overwrite locally-modified skills:

```bash
$ oasr sync --force

Scanning /home/user/project for tracked skills...

Found 3 tracked skills:
  • my-skill (up-to-date, skipping)
  • python-analyzer (outdated, updating...)
    ✓ Refreshed from github.com/user/repo/skills/python-analyzer
  • json-parser (modified, forcing overwrite...)
    ✓ Refreshed from /home/user/registry/json-parser
    ⚠ Local changes discarded

Updated: 2
Skipped: 1
```

## JSON Output

```bash
$ oasr sync --json
{
  "updated": [
    {
      "name": "python-analyzer",
      "path": "/home/user/project/python-analyzer",
      "source": "github.com/user/repo/skills/python-analyzer"
    }
  ],
  "skipped": [
    {
      "name": "my-skill",
      "reason": "up-to-date"
    },
    {
      "name": "json-parser",
      "reason": "modified"
    }
  ],
  "summary": {
    "updated": 1,
    "skipped": 2
  }
}
```

## See Also

- [`oasr diff`](DIFF.md) - Show status of tracked skills without updating
- [`oasr use`](USE.md) - Copy skills with tracking metadata
- [`oasr registry sync`](REGISTRY.md#oasr-registry-sync) - Sync registry with remote sources

## Migration from v0.2.0

The `oasr sync` command has completely changed in v0.3.0:

| v0.2.0 | v0.3.0 |
|--------|--------|
| `oasr sync` (validate manifests) | `oasr registry` |
| `oasr sync --update` (sync remotes) | `oasr registry sync` |
| N/A | `oasr sync` (refresh tracked skills) |
