# `oasr update`

Update the `oasr` tool from PyPI.

```bash
oasr update                      # Check and update from PyPI
oasr update --check              # Check for updates only
oasr update --yes                # Skip confirmation prompt
oasr update --json               # Output in JSON format
oasr update --quiet              # Suppress info messages
```

**Requirements:**\
- `oasr` must be installed from PyPI
- Network access to PyPI is required

**Behavior:**

- Checks PyPI for latest version
- Prompts before upgrading unless `--yes` is provided
- Attempts update via `uv pip install --upgrade oasr`, falls back to `pip`
- Returns JSON output suitable for scripting (use `--check` for non-destructive checks)

**JSON Output:**

```json
{
  "success": true,
  "updated": true,
  "installed_version": "0.6.1",
  "latest_version": "0.6.2",
  "update_available": true,
  "runner": "pip",
  "error": null
}
```

---

## Data Locations

| Path                      | Purpose                        |
|---------------------------|--------------------------------|
| `~/.oasr/registry.toml`   | Registered skills              |
| `~/.oasr/manifests/`      | Per-skill manifest snapshots   |
| `~/.oasr/config.toml`     | Configuration                  |
