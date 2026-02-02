# Validation Settings

Configure skill validation and reference display settings.

---

## Overview

OASR validates skills before execution and when displaying references. These settings control validation behavior.

---

## Settings

### reference_max_lines

**Maximum lines to display in skill reference output.**

- **Type:** Integer
- **Default:** `500`
- **Valid range:** 1 or greater

**Via CLI:**
```bash
oasr config set validation.reference_max_lines 1000
```

**Via Environment Variable:**
```bash
export OASR_VALIDATION_MAX_LINES=1000
```

**Via Config File:**
```toml
[validation]
reference_max_lines = 1000
```

**Usage:**
Controls how much of a skill's SKILL.md is displayed when using `oasr info` or similar commands.

### strict

**Enable strict validation mode.**

- **Type:** Boolean
- **Default:** `false`
- **Values:** `true` or `false`

**Via CLI:**
```bash
oasr config set validation.strict true
```

**Via Environment Variable:**
```bash
export OASR_VALIDATION_STRICT=true
```

**Via Config File:**
```toml
[validation]
strict = true
```

**Behavior:**
- `false` (default): Warnings are logged but don't prevent execution
- `true`: Warnings are treated as errors and prevent execution

---

## Examples

### Increase Reference Display

For skills with long documentation:

```toml
[validation]
reference_max_lines = 2000
```

### Strict Mode for CI/CD

Fail fast on any validation issues:

```bash
export OASR_VALIDATION_STRICT=true
oasr exec skill -p "test"
```

---

## Related

- [Configuration Overview](README.md)
- [Environment Variables](environment-variables.md)
