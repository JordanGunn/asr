# `oasr registry`

Manage the skill registry - add, remove, list, and sync skills.

## Default Behavior (Validation)

By default, `oasr registry` validates all registered skills:

```bash
oasr registry              # Validate all registered skills
oasr registry -v           # Verbose output with per-skill details
oasr registry --json       # JSON output
```

**Example output:**
```
✓ Registry validation complete
  Valid: 12
  Modified: 2
  Missing: 0
```

## Subcommands

### `oasr registry list`

List all registered skills:

```bash
oasr registry list
oasr registry list --json
```

**Example output:**
```
Registered Skills:
  • my-skill (local: /path/to/skills/my-skill)
  • python-analyzer (remote: github.com/user/repo/skills/python-analyzer)
  • json-parser (local: /path/to/skills/json-parser)

Total: 3 skills
```

### `oasr registry add`

Register skills in the registry:

```bash
oasr registry add /path/to/skill
oasr registry add https://github.com/user/repo/tree/main/skills/my-skill  # Remote URL
oasr registry add /path/to/skills/*          # Glob paths
oasr registry add /path/to/skill --strict    # Fail on validation warnings
oasr registry add -r /path/to/root           # Recursive discovery
```

**Remote Skills:**

- Supports GitHub and GitLab URLs
- Formats: `https://github.com/{user}/{repo}/tree/{branch}/{path}`
- Set `GITHUB_TOKEN` or `GITLAB_TOKEN` for authentication
- Files validated during registration, fetched on-demand during use

**Example output:**
```bash
$ oasr registry add /home/user/skills/my-skill
✓ Registered 'my-skill' from /home/user/skills/my-skill
```

### `oasr registry rm`

Remove skills from the registry:

```bash
oasr registry rm skill-name
oasr registry rm /path/to/skill
oasr registry rm skill-one skill-two    # Multiple
oasr registry rm "prefix-*"             # Glob by name
oasr registry rm -r /path/to/root       # Recursive removal
```

**Example output:**
```bash
$ oasr registry rm my-skill
✓ Removed 'my-skill' from registry
```

### `oasr registry sync`

Sync registry with remote sources (update remote skills):

```bash
oasr registry sync              # Sync all remote skills
oasr registry sync --json       # JSON output
```

This fetches the latest versions of remote skills and updates their manifests.

**Example output:**
```bash
$ oasr registry sync
Syncing remote skills...
  ✓ python-analyzer (updated)
  ✓ json-parser (up-to-date)

Synced: 2 skills
```

### `oasr registry prune`

Clean up corrupted/missing skills and orphaned artifacts:

```bash
oasr registry prune              # Interactive cleanup
oasr registry prune -y           # Skip confirmation
oasr registry prune --dry-run    # Show what would be cleaned
oasr registry prune --json       # JSON output
```

This command:
- Removes skills whose source files/URLs are no longer accessible
- Removes orphaned manifest files not in the registry
- Requires confirmation unless `-y` flag is used

**Example output:**
```bash
$ oasr registry prune
Checking 3 remote skill(s)...
  ↓ python-analyzer (checking GitHub...)
  ✓ python-analyzer (checked)

The following will be cleaned:

Skills with missing sources:
  ✗ old-skill (/path/to/missing)

Proceed with cleanup? [y/N] y
Removed skill: old-skill

Cleaned 1 skill(s), 0 manifest(s)
```

## Migration from v0.2.0

The v0.3.0 CLI taxonomy reorganizes commands under the `registry` subcommand:

| v0.2.0 | v0.3.0 |
|--------|--------|
| `oasr add` | `oasr registry add` |
| `oasr rm` | `oasr registry rm` |
| `oasr list` | `oasr registry list` |
| `oasr status` | `oasr registry -v` |
| `oasr sync` (manifest validation) | `oasr registry` |
| `oasr sync --update` (remote sync) | `oasr registry sync` |

**v0.4.1 update:** `oasr clean` → `oasr registry prune`
