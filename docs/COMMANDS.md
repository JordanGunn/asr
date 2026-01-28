# Command Reference

## Global Flags

| Flag | Description |
|------|-------------|
| `--config <path>` | Override config file location |
| `--json` | Output in JSON format |
| `--quiet` | Suppress info/warnings |
| `--version` | Show version |

---

## `oasr list`

List all registered skills.

```bash
oasr list              # Human-readable output
oasr list --json       # JSON output
oasr list --verbose    # Show full paths
```

---

## `oasr add`

Register skills in the registry.

```bash
oasr add /path/to/skill
oasr add /path/to/skills/*          # Glob paths
oasr add /path/to/skill --strict    # Fail on validation warnings
oasr add -r /path/to/root           # Recursive discovery
```

---

## `oasr rm`

Remove skills from the registry.

```bash
oasr rm skill-name
oasr rm /path/to/skill
oasr rm skill-one skill-two         # Multiple
oasr rm "prefix-*"                  # Glob by name
oasr rm -r /path/to/root            # Recursive removal
```

---

## `oasr use`

Copy skills to a target directory. Supports glob patterns.

```bash
oasr use skill-name
oasr use skill-name -d /path/to/project
oasr use "git-*"                    # Glob pattern
oasr use skill-one skill-two        # Multiple skills
```

---

## `oasr find`

Discover skills by searching for `SKILL.md` manifests.

```bash
oasr find /path/to/search
oasr find /path/to/search --add     # Register found skills
oasr find /path/to/search --json
```

---

## `oasr validate`

Validate skill structure and `SKILL.md` frontmatter.

```bash
oasr validate /path/to/skill
oasr validate --all                 # All registered skills
oasr validate --all --strict        # Treat warnings as errors
```

See [VALIDATION.md](VALIDATION.md) for validation error and warning codes.

---

## `oasr sync`

Synchronize manifests with registered skills.

```bash
oasr sync              # Create manifests where missing
oasr sync --update     # Update manifests for modified skills
oasr sync --prune      # Remove entries for missing source paths
```

---

## `oasr status`

Show the current state of registered skills.

```bash
oasr status
oasr status --json
```

States: `valid`, `modified`, `missing`, `untracked`

---

## `oasr clean`

Remove orphaned manifests and entries for missing skills.

```bash
oasr clean
oasr clean --dry-run
```

---

## `oasr adapter`

Generate IDE-specific adapter files that delegate to your canonical skills.

```bash
oasr adapter                              # All default targets
oasr adapter cursor                       # Cursor only
oasr adapter windsurf                     # Windsurf only
oasr adapter codex                        # Codex only
oasr adapter copilot                      # GitHub Copilot
oasr adapter claude                       # Claude Code
oasr adapter --exclude skill1,skill2
oasr adapter --output-dir /path/to/project
oasr adapter --copy                       # Copy skills locally, use relative paths
```

### `--copy` Flag

When `--copy` is specified, skills are copied into a local `skills/` directory sibling to the adapter output, and generated files use relative paths instead of absolute paths.

**Without `--copy` (default):**
```
.windsurf/workflows/my-skill.md  → points to ~/skills/my-skill/
```

**With `--copy`:**
```
.windsurf/
├── skills/my-skill/             ← copied from source
└── workflows/my-skill.md        → points to ../skills/my-skill/
```

Use cases:
- Self-contained projects without external path dependencies
- Distributable repositories
- Snapshotting skills at a specific version

### Adapter Outputs

| Target | Output Path |
|--------|-------------|
| cursor | `.cursor/commands/{skill}.md` |
| windsurf | `.windsurf/workflows/{skill}.md` |
| codex | `.codex/skills/{skill}.md` |
| copilot | `.github/prompts/*.prompt.md` |
| claude | `.claude/commands/{skill}.md` |

---

## `oasr help`

Show help for any command.

```bash
oasr help
oasr help list
oasr help adapter
```

---

## Configuration

Stored in `~/.skills/config.toml`:

```toml
[validation]
reference_max_lines = 500
strict = false

[adapter]
default_targets = ["cursor", "windsurf"]
```

## Data Locations

| Path | Purpose |
|------|---------|
| `~/.skills/registry.toml` | Registered skills |
| `~/.skills/manifests/` | Per-skill manifest snapshots |
| `~/.skills/config.toml` | Configuration |
