# Environment Variables

Complete reference for OASR environment variables.

**Introduced in:** v0.5.1

---

## Overview

OASR supports environment variables for all configuration options. This is perfect for:
- **CI/CD pipelines** - No config file needed
- **Temporary overrides** - Quick testing without changing config
- **Container deployments** - Configure at runtime
- **Multi-environment setups** - Different configs per environment

**Precedence:** CLI flags > Environment variables > Config file > Built-in defaults

---

## Environment Variable List

### Core Settings

**`OASR_AGENT`**
- **Type:** String
- **Values:** `codex`, `copilot`, `claude`, `opencode`
- **Default:** None (must be set)
- **Example:** `export OASR_AGENT=codex`
- **Config equivalent:** `[agent] default = "codex"`

**`OASR_PROFILE`**
- **Type:** String
- **Values:** Any profile name defined in config or profile files
- **Default:** `safe`
- **Example:** `export OASR_PROFILE=dev`
- **Config equivalent:** `[oasr] default_profile = "dev"`

### Validation Settings

**`OASR_VALIDATION_STRICT`**
- **Type:** Boolean
- **Values:** `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` (case-insensitive)
- **Default:** `false`
- **Example:** `export OASR_VALIDATION_STRICT=true`
- **Config equivalent:** `[validation] strict = true`

**`OASR_VALIDATION_MAX_LINES`**
- **Type:** Integer
- **Values:** Positive integer
- **Default:** `500`
- **Example:** `export OASR_VALIDATION_MAX_LINES=1000`
- **Config equivalent:** `[validation] reference_max_lines = 1000`

### Adapter Settings

**`OASR_ADAPTER_TARGETS`**
- **Type:** List (comma-separated)
- **Values:** IDE names (e.g., `cursor`, `windsurf`)
- **Default:** `cursor,windsurf`
- **Example:** `export OASR_ADAPTER_TARGETS=cursor,vscode`
- **Config equivalent:** `[adapter] default_targets = ["cursor", "vscode"]`

---

## Type Handling

### Strings

Used as-is:

```bash
export OASR_AGENT=codex
```

### Booleans

Accepts multiple formats (case-insensitive):

```bash
# True values
export OASR_VALIDATION_STRICT=true
export OASR_VALIDATION_STRICT=1
export OASR_VALIDATION_STRICT=yes
export OASR_VALIDATION_STRICT=on

# False values
export OASR_VALIDATION_STRICT=false
export OASR_VALIDATION_STRICT=0
export OASR_VALIDATION_STRICT=no
export OASR_VALIDATION_STRICT=off
```

### Integers

Parsed as integers:

```bash
export OASR_VALIDATION_MAX_LINES=1000
```

**Invalid values are skipped with a warning:**
```bash
export OASR_VALIDATION_MAX_LINES=not_a_number
# Warning: Invalid value for OASR_VALIDATION_MAX_LINES='not_a_number': ... Skipping.
```

### Lists

Comma-separated values:

```bash
export OASR_ADAPTER_TARGETS=cursor,windsurf,vscode
```

Whitespace is trimmed:

```bash
export OASR_ADAPTER_TARGETS="cursor, windsurf, vscode"
# Result: ["cursor", "windsurf", "vscode"]
```

---

## Precedence Examples

### Example 1: CLI Override

```bash
# Config file has agent = "codex"
export OASR_AGENT=copilot

# CLI flag overrides both
oasr exec skill -p "prompt" --agent claude
# Uses: claude (CLI wins)
```

### Example 2: Env Override

```bash
# Config file has agent = "codex"
export OASR_AGENT=copilot

# No CLI flag
oasr exec skill -p "prompt"
# Uses: copilot (env var wins over config)
```

### Example 3: Config Fallback

```bash
# No OASR_AGENT set
# Config file has agent = "codex"

oasr exec skill -p "prompt"
# Uses: codex (config file used)
```

### Example 4: Default Fallback

```bash
# No OASR_PROFILE set
# No config file

oasr exec skill -p "prompt"
# Uses: safe (built-in default)
```

---

## Usage Patterns

### CI/CD Pipeline

```yaml
# GitHub Actions
env:
  OASR_AGENT: codex
  OASR_PROFILE: ci
  OASR_VALIDATION_STRICT: true

steps:
  - name: Run skill
    run: oasr exec test-skill -p "run tests"
```

```yaml
# GitLab CI
variables:
  OASR_AGENT: "codex"
  OASR_PROFILE: "ci"

script:
  - oasr exec build-skill -p "build project"
```

### Docker Container

```dockerfile
# Dockerfile
ENV OASR_AGENT=copilot
ENV OASR_PROFILE=production
ENV OASR_VALIDATION_STRICT=true

CMD ["oasr", "exec", "service-skill", "-p", "start service"]
```

```bash
# Or pass at runtime
docker run -e OASR_AGENT=codex myimage
```

### Multi-Environment Setup

```bash
# Development
export OASR_AGENT=codex
export OASR_PROFILE=dev

# Staging
export OASR_AGENT=copilot
export OASR_PROFILE=staging

# Production
export OASR_AGENT=codex
export OASR_PROFILE=production
export OASR_VALIDATION_STRICT=true
```

### Temporary Override

```bash
# Normal config uses codex
oasr exec skill -p "prompt"

# Try copilot once
OASR_AGENT=copilot oasr exec skill -p "prompt"

# Back to normal
oasr exec skill -p "prompt"
```

---

## Shell Integration

### Bash/Zsh

```bash
# ~/.bashrc or ~/.zshrc
export OASR_AGENT=codex
export OASR_PROFILE=dev
```

### Fish

```fish
# ~/.config/fish/config.fish
set -x OASR_AGENT codex
set -x OASR_PROFILE dev
```

### Project-Specific (direnv)

```bash
# .envrc
export OASR_AGENT=copilot
export OASR_PROFILE=project-specific
```

Then use `direnv allow` to auto-load when entering directory.

---

## Limitations

### Cannot Define Profiles

Environment variables cannot define full profile configurations. Profiles must be defined in `~/.oasr/config.toml`:

```bash
# ❌ This does NOT work
export OASR_PROFILE_DEV_NETWORK=true

# ✅ This works (selects existing profile)
export OASR_PROFILE=dev
```

To use a profile, it must first exist in the config file.

### Single Values Only

Each environment variable maps to a single config value:

```bash
# ❌ Cannot set nested objects
export OASR_AGENT_CODEX_MODEL=gpt-4

# ✅ Can set top-level values
export OASR_AGENT=codex
```

---

## Troubleshooting

### Env Var Not Working

**Check precedence:**
```bash
# See what's being used
oasr config list

# Test with just env var (no config file)
mv ~/.oasr/config.toml ~/.oasr/config.toml.bak
export OASR_AGENT=copilot
oasr exec skill -p "test"
```

### Invalid Value Warning

```bash
export OASR_VALIDATION_STRICT=invalid
oasr exec skill -p "test"
# ⚠ Warning: Invalid value for OASR_VALIDATION_STRICT='invalid': ... Skipping.
```

**Fix:** Use valid boolean value (`true`, `false`, `1`, `0`, etc.)

### Profile Not Found

```bash
export OASR_PROFILE=nonexistent
oasr exec skill -p "test"
# Uses safe profile + warning
```

**Fix:** Create the profile in `~/.oasr/config.toml` first

---

## Verification

### Check Current Values

```bash
# List all config (includes env var sources)
oasr config list

# Check specific value
oasr config get agent
```

### Test Precedence

```bash
# Set in all places
export OASR_AGENT=copilot
oasr config set agent codex
oasr exec skill -p "test" --agent claude
# Uses: claude (CLI flag wins)
```

---

## Related

- [Configuration Overview](README.md) - Full config guide
- [Configuration Precedence](precedence.md) - Detailed precedence rules
- [Agent Configuration](agent.md) - OASR_AGENT details
- [Policy Profiles](profiles.md) - OASR_PROFILE details
