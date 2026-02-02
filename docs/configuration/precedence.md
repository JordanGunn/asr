# Configuration Precedence

Understanding how CLI flags, environment variables, config file, and defaults interact.

---

## Precedence Order

OASR merges configuration from multiple sources with a clear precedence order:

```
1. CLI flags         (highest priority)
   ↓
2. Environment variables
   ↓
3. Config file
   ↓
4. Built-in defaults (lowest priority)
```

**Rule:** Higher priority sources override lower priority sources.

---

## How It Works

### Merging Strategy

- **Per-setting basis:** Each configuration setting is resolved independently
- **No cascading:** Setting one value doesn't affect others in the same section
- **Additive for profiles:** Profile definitions are merged (user profiles override defaults)

### Resolution Process

For each setting (e.g., `agent.default`):

1. Check if CLI flag provided (`--agent codex`)
   - If yes: Use CLI value ✅
   - If no: Continue...

2. Check if environment variable set (`OASR_AGENT=copilot`)
   - If yes: Use env var value ✅
   - If no: Continue...

3. Check if value in config file (`[agent] default = "claude"`)
   - If yes: Use config file value ✅
   - If no: Continue...

4. Use built-in default (varies by setting)
   - Always available as fallback ✅

---

## Examples

### Example 1: Full Override Chain

**Setup:**
```toml
# ~/.oasr/config.toml
[agent]
default = "codex"
```

```bash
export OASR_AGENT=copilot
```

**Test:**
```bash
# No CLI flag
oasr exec skill -p "test"
# Uses: copilot (env var overrides config)

# With CLI flag
oasr exec skill -p "test" --agent claude
# Uses: claude (CLI overrides env var)
```

### Example 2: Partial Configuration

**Setup:**
```toml
# ~/.oasr/config.toml
[validation]
strict = false
reference_max_lines = 500
```

```bash
export OASR_VALIDATION_STRICT=true
# Only strict is overridden
```

**Result:**
- `strict`: `true` (from env var)
- `reference_max_lines`: `500` (from config file)

Each setting resolves independently!

### Example 3: Profile Selection

**Setup:**
```toml
# ~/.oasr/config.toml
[oasr]
default_profile = "safe"

[profiles.dev]
network = true
```

```bash
export OASR_PROFILE=dev
```

**Test:**
```bash
# No CLI flag
oasr exec skill -p "test"
# Uses: dev (env var overrides config)

# With CLI flag
oasr exec skill -p "test" --profile test
# Uses: test (CLI overrides env var)
```

### Example 4: Missing Values

**Setup:**
```toml
# ~/.oasr/config.toml (empty or missing)
```

```bash
# No env vars set
# No CLI flags
```

**Result:**
```bash
oasr exec skill -p "test"
# Uses built-in defaults:
#   - profile: safe (built-in)
#   - agent: (error - must be set somewhere)
```

---

## Per-Setting Precedence

### Agent

```
--agent flag > OASR_AGENT > config [agent].default > (no default, error)
```

### Profile

```
--profile flag > OASR_PROFILE > config [oasr].default_profile > "safe"
```

### Validation Strict

```
(no CLI flag) > OASR_VALIDATION_STRICT > config [validation].strict > false
```

### Validation Max Lines

```
(no CLI flag) > OASR_VALIDATION_MAX_LINES > config [validation].reference_max_lines > 500
```

### Adapter Targets

```
--targets flag > OASR_ADAPTER_TARGETS > config [adapter].default_targets > ["cursor", "windsurf"]
```

---

## Common Patterns

### Pattern 1: Global Defaults, Local Overrides

```bash
# Set global defaults in config
# ~/.oasr/config.toml
[agent]
default = "codex"

[oasr]
default_profile = "safe"

# Override per-project with environment
cd ~/project-a
export OASR_AGENT=copilot
export OASR_PROFILE=dev

# Override per-command with flags
oasr exec skill -p "test" --agent claude
```

### Pattern 2: CI/CD with Env Vars

```yaml
# No config file in CI
# Use only environment variables
env:
  OASR_AGENT: codex
  OASR_PROFILE: ci
  OASR_VALIDATION_STRICT: true
```

### Pattern 3: Development Flexibility

```bash
# Config has safe defaults
# ~/.oasr/config.toml
[agent]
default = "codex"

# Quick experiments with env vars
OASR_AGENT=copilot oasr exec skill -p "test copilot"
OASR_AGENT=claude oasr exec skill -p "test claude"

# Back to defaults
oasr exec skill -p "test codex"
```

---

## Debugging Precedence

### View Final Configuration

```bash
oasr config list
```

Shows merged configuration with sources indicated.

### Test Precedence

```bash
# Set all layers
oasr config set agent codex
export OASR_AGENT=copilot
oasr exec skill -p "test" --agent claude

# Result: Uses claude (CLI wins)
```

### Verify Env Var Overrides

```bash
# Check what config file has
oasr config get agent
# Output: codex

# Set env var
export OASR_AGENT=copilot

# Verify it takes effect
oasr config list | grep agent
# Should show copilot with (from: env var)
```

---

## Edge Cases

### Case 1: Invalid Env Var

```bash
export OASR_VALIDATION_STRICT=invalid
oasr exec skill -p "test"
# Warning logged, env var skipped
# Falls back to config or default
```

### Case 2: Profile Not Found

```bash
export OASR_PROFILE=nonexistent
oasr exec skill -p "test"
# Warning logged, uses safe profile
```

### Case 3: Empty String

```bash
export OASR_AGENT=""
oasr exec skill -p "test"
# Treated as not set, falls back to config/default
```

---

## Related

- [Configuration Overview](README.md)
- [Environment Variables](environment-variables.md)
- [Agent Configuration](agent.md)
- [Policy Profiles](profiles.md)
