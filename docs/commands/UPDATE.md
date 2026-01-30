# `oasr update`

Update `oasr` tool itself from GitHub.

```bash
oasr update                      # Pull updates and reinstall
oasr update --no-reinstall       # Pull only, skip reinstallation
oasr update --changelog 5        # Show 5 changelog entries (default: 10)
oasr update --json               # Output in JSON format
oasr update --quiet              # Suppress info messages
```

**Requirements:**\

- `oasr` must be retain it's cloned repository structure and git history
- Working tree must be clean (no uncommitted changes)
- Remote must be configured (typically GitHub)

> **NOTE**
> PyPI installations are not available yet, but will be coming soon.
> Current `oasr update` command only works with git installations.

**Behavior:**

- Finds `oasr` installation directory
- Runs `git pull --ff-only` from remote
- Displays truncated changelog with commit count
- Reinstalls package with `uv pip install -e .` or falls back to `pip`
- Suppresses verbose git output

**JSON Output:**

```json
{
  "success": true,
  "updated": true,
  "repo_path": "/path/to/asr",
  "remote_url": "https://github.com/user/asr.git",
  "old_commit": "abc1234",
  "new_commit": "def5678",
  "commits": 3,
  "files_changed": 5,
  "insertions": 150,
  "deletions": 42,
  "changelog": [
    "def5678 feat: add new feature",
    "cba4321 fix: resolve bug"
  ]
}
```

---

## Data Locations

| Path                      | Purpose                        |
|---------------------------|--------------------------------|
| `~/.oasr/registry.toml`   | Registered skills              |
| `~/.oasr/manifests/`      | Per-skill manifest snapshots   |
| `~/.oasr/config.toml`     | Configuration                  |
