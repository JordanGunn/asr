# Validation Rules

ASR validates skill directories to catch structural issues, missing metadata, and potential problems before they cause silent failures.

Run validation with:

```bash
oasr validate /path/to/skill       # Single skill
oasr validate --all                # All registered skills
oasr validate --all --strict       # Treat warnings as errors
```

---

## Errors (E)

Errors indicate problems that will prevent a skill from working correctly. These must be fixed.

| Code | Description |
|------|-------------|
| E001 | Missing `SKILL.md` manifest file |
| E002 | Malformed YAML frontmatter (syntax error) |
| E003 | Missing required `name` field in frontmatter |
| E004 | Missing required `description` field in frontmatter |
| E005 | `name` field violates kebab-case naming convention |

---

## Warnings (W)

Warnings indicate potential issues that may cause problems but don't prevent basic functionality.

| Code | Description |
|------|-------------|
| W001 | Empty `description` field |
| W002 | Directory name does not match frontmatter `name` |
| W003 | Path contains spaces or special characters |
| W004 | Skill contains only a `scripts/` directory (no other content) |
| W005 | Empty file found in `references/`, `assets/`, or `scripts/` |
| W006 | Shell script (`.sh`) exists without PowerShell equivalent (`.ps1`), or vice versa |
| W007 | Reference file exceeds configured line threshold |

---

## Info (I)

Informational messages that highlight potential issues but are not validation failures.

| Code | Description |
|------|-------------|
| I001 | Registered skill path no longer exists on disk |

---

## Configuration

Validation behavior can be configured in `~/.skills/config.toml`:

```toml
[validation]
reference_max_lines = 500   # Threshold for W007
strict = false              # Treat warnings as errors by default
```
