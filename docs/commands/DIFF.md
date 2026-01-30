# `oasr diff`

Show the status of tracked skills (skills copied with `oasr use`).

## Overview

When you copy a skill with `oasr use`, metadata tracking is automatically injected into the `SKILL.md` frontmatter under `metadata.oasr`. This allows ASR to detect drift between your local copy and the registry source.

The `oasr diff` command scans for tracked skills and reports their status.

## Usage

```bash
oasr diff                    # Scan current directory
oasr diff /path/to/project   # Scan specific path
oasr diff --json             # JSON output
```

## Skill Status

- **✓ up-to-date** - Local copy matches registry source (hash match)
- **⚠ outdated** - Registry source has been updated (hash mismatch)
- **⚠ modified** - Local file has been edited (content differs from tracked hash)
- **⚠ untracked** - Skill not in registry (source removed or renamed)

## Example Output

```bash
$ oasr diff

Scanning /home/user/project for tracked skills...

✓ my-skill (up-to-date)
  Source: /home/user/registry/my-skill
  Synced: 2026-01-30T19:30:15Z

⚠ python-analyzer (outdated)
  Source: github.com/user/repo/skills/python-analyzer
  Registry has newer version
  Run 'oasr sync' to update

⚠ json-parser (modified)
  Source: /home/user/registry/json-parser
  Local changes detected
  Use --force with 'oasr sync' to overwrite

Summary:
  Up-to-date: 1
  Outdated: 1
  Modified: 1
  Untracked: 0
```

## JSON Output

```bash
$ oasr diff --json
{
  "tracked_skills": [
    {
      "name": "my-skill",
      "path": "/home/user/project/my-skill",
      "status": "up-to-date",
      "source": "/home/user/registry/my-skill",
      "tracked_hash": "abc123...",
      "registry_hash": "abc123...",
      "synced_at": "2026-01-30T19:30:15Z"
    },
    {
      "name": "python-analyzer",
      "path": "/home/user/project/python-analyzer",
      "status": "outdated",
      "source": "github.com/user/repo/skills/python-analyzer",
      "tracked_hash": "def456...",
      "registry_hash": "xyz789...",
      "synced_at": "2026-01-29T10:15:00Z"
    }
  ],
  "summary": {
    "up_to_date": 1,
    "outdated": 1,
    "modified": 0,
    "untracked": 0
  }
}
```

## See Also

- [`oasr sync`](SYNC.md) - Refresh outdated tracked skills
- [`oasr use`](USE.md) - Copy skills with tracking metadata
