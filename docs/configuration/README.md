# OASR Configuration

Complete guide to configuring OASR for your workflow.

## Quick Start

OASR uses a configuration file at `~/.oasr/config.toml` and supports environment variables for all settings.

**First time setup:**

```bash
# Set your default agent
oasr config set agent codex

# Or use an environment variable
export OASR_AGENT=codex

# Verify configuration
oasr config list
```

**Configuration precedence:**
```
CLI flags > Environment variables > Config file > Built-in defaults
```

---

## Common Scenarios

### Scenario 1: Local Development

You want permissive settings for local work:

```bash
# Set a dev profile with broader permissions
# Add this to ~/.oasr/config.toml:
```

```toml
[oasr]
default_profile = "dev"

[profiles.dev]
fs_read_roots = ["./", "~/projects"]
fs_write_roots = ["./", "~/projects/output"]
deny_paths = ["~/.ssh", "~/.aws"]
allowed_commands = ["bash", "python", "node", "git", "curl"]
deny_shell = false
network = true
allow_env = true
```

### Scenario 2: CI/CD Pipeline

You want ephemeral configuration without creating files:

```bash
# GitHub Actions / GitLab CI
export OASR_AGENT=codex
export OASR_PROFILE=ci
export OASR_VALIDATION_STRICT=true

# Run skill
oasr exec my-skill -p "build and test"
```

### Scenario 3: Quick Agent Switch

You want to try a different agent temporarily:

```bash
# Use flag to override config
oasr exec my-skill -p "prompt" --agent copilot

# Or set environment variable for the session
export OASR_AGENT=copilot
oasr exec my-skill -p "prompt"
```

### Scenario 4: Multiple Profiles

You want different security profiles for different use cases:

```toml
[oasr]
default_profile = "safe"

[profiles.safe]
# Conservative defaults (built-in)

[profiles.dev]
# Development profile
deny_shell = false
network = true

[profiles.test]
# Testing profile
fs_read_roots = ["./tests"]
fs_write_roots = ["./test-output"]

[profiles.production]
# Production hardened
fs_write_roots = ["./logs"]
allowed_commands = ["cat", "rg"]
```

Then select per execution:

```bash
oasr exec skill -p "prompt" --profile dev
oasr exec skill -p "prompt" --profile production
```

---

## Configuration Sections

### 📋 Core Configuration

- **[agent]** - Default agent selection → [Details](agent.md)
- **[oasr]** - OASR-specific settings (default profile) → [Details](profiles.md)

### 🔒 Security

- **[profiles.*]** - Execution policy profiles → [Details](profiles.md)

### ⚙️ Advanced

- **[validation]** - Skill validation settings → [Details](validation.md)
- **[adapter]** - IDE adapter targets → [Details](adapter.md)

### 🌍 Environment Variables

Complete reference for `OASR_*` environment variables → [Details](environment-variables.md)

---

## Configuration Files

| File | Purpose |
|------|---------|
| `~/.oasr/config.toml` | User configuration file |
| `~/.oasr/registry.json` | Skill registry (auto-managed) |

**View config location:**
```bash
oasr config path
```

**Edit config:**
```bash
$EDITOR ~/.oasr/config.toml
# or
code ~/.oasr/config.toml
```

---

## Configuration Methods

### Method 1: CLI Commands

Recommended for simple settings:

```bash
oasr config set agent codex
oasr config set validation.strict true
oasr config set oasr.default_profile dev
```

### Method 2: Environment Variables

Perfect for CI/CD and temporary overrides:

```bash
export OASR_AGENT=copilot
export OASR_PROFILE=ci
export OASR_VALIDATION_STRICT=true
```

### Method 3: Direct File Editing

Best for complex configurations (profiles):

```bash
$EDITOR ~/.oasr/config.toml
```

---

## Examples

Ready-to-use configuration examples:

- [Development Config](examples/development.toml) - Permissive for local dev
- [CI/CD Config](examples/ci-cd.toml) - Pipeline friendly
- [Production Config](examples/production.toml) - Hardened for production
- [Minimal Config](examples/minimal.toml) - Bare minimum setup

---

## Topics

### Essential

- [Agent Configuration](agent.md) - Choose your AI agent
- [Policy Profiles](profiles.md) - Security and isolation
- [Environment Variables](environment-variables.md) - OASR_* reference

### Advanced

- [Configuration Precedence](precedence.md) - How settings merge
- [Validation Settings](validation.md) - Skill validation options
- [Adapter Configuration](adapter.md) - IDE integration

---

## Need Help?

- **List current config:** `oasr config list`
- **Get specific value:** `oasr config get agent`
- **Set a value:** `oasr config set agent codex`
- **Config file location:** `oasr config path`

For more details, see individual documentation pages linked above.
