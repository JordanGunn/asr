# Command Reference

## Global Flags

| Flag | Description |
|------|-------------|
| `--config <path>` | Override config file location |
| `--json` | Output in JSON format |
| `--quiet` | Suppress info/warnings |
| `--version` | Show version |

---

## `asr list`

List all registered skills.

```bash
asr list              # Human-readable output
asr list --json       # JSON output
asr list --verbose    # Show full paths
```

---

## `asr add`

Register skills in the registry.

```bash
asr add /path/to/skill
asr add /path/to/skills/*          # Glob paths
asr add /path/to/skill --strict    # Fail on validation warnings
asr add -r /path/to/root           # Recursive discovery
```

---

## `asr rm`

Remove skills from the registry.

```bash
asr rm skill-name
asr rm /path/to/skill
asr rm skill-one skill-two         # Multiple
asr rm "prefix-*"                  # Glob by name
asr rm -r /path/to/root            # Recursive removal
```

---

## `asr use`

Copy skills to a target directory. Supports glob patterns.

```bash
asr use skill-name
asr use skill-name -d /path/to/project
asr use "git-*"                    # Glob pattern
asr use skill-one skill-two        # Multiple skills
```

---

## `asr find`

Discover skills by searching for `SKILL.md` manifests.

```bash
asr find /path/to/search
asr find /path/to/search --add     # Register found skills
asr find /path/to/search --json
```

---

## `asr validate`

Validate skill structure and `SKILL.md` frontmatter.

```bash
asr validate /path/to/skill
asr validate --all                 # All registered skills
asr validate --all --strict        # Treat warnings as errors
```

See [VALIDATION.md](VALIDATION.md) for validation error and warning codes.

---

## `asr sync`

Synchronize manifests with registered skills.

```bash
asr sync              # Create manifests where missing
asr sync --update     # Update manifests for modified skills
asr sync --prune      # Remove entries for missing source paths
```

---

## `asr status`

Show the current state of registered skills.

```bash
asr status
asr status --json
```

States: `valid`, `modified`, `missing`, `untracked`

---

## `asr clean`

Remove orphaned manifests and entries for missing skills.

```bash
asr clean
asr clean --dry-run
```

---

## `asr adapter`

Generate IDE-specific adapter files that delegate to your canonical skills.

```bash
asr adapter                              # All default targets
asr adapter cursor                       # Cursor only
asr adapter windsurf                     # Windsurf only
asr adapter codex                        # Codex only
asr adapter copilot                      # GitHub Copilot
asr adapter claude                       # Claude Code
asr adapter --exclude skill1,skill2
asr adapter --output-dir /path/to/project
asr adapter --copy                       # Copy skills locally, use relative paths
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

## `asr help`

Show help for any command.

```bash
asr help
asr help list
asr help adapter
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
