# Policy Profiles

Execution policy profiles define security boundaries for `oasr exec`. They control what agents can and cannot do during skill execution.

**Introduced in:** v0.5.0

---

## Overview

Policy profiles provide host-level security enforcement to mitigate risks from:
- Prompt injection attacks in skill instructions
- Unsafe agent behavior (network access, shell execution)
- Access to sensitive files and directories

**Key principle:** Even if an agent is tricked by malicious instructions, the host policy enforces boundaries.

---

## Default Profiles

OASR includes built-in profiles with conservative defaults:

- `safe` (default)
- `strict`
- `dev`
- `unsafe`

The `safe` profile uses conservative defaults:

```toml
[profiles.safe]
fs_read_roots = ["./"]
fs_write_roots = ["./out", "./.oasr"]
deny_paths = ["~/.ssh", "~/.aws", "~/.gnupg", "~/.config", ".env", "~/.bashrc"]
allowed_commands = ["rg", "fd", "jq", "cat"]
deny_shell = true
network = false
allow_env = false
```

**This profile:**
- ✅ Allows reading current directory
- ✅ Allows writing to `./out` and `./.oasr`
- ✅ Allows read-only search tools (rg, fd, jq, cat)
- ❌ Denies shell execution
- ❌ Denies network access
- ❌ Denies environment variable access
- ❌ Denies sensitive paths (~/.ssh, ~/.aws, etc.)

---

## Setting Default Profile

### Via CLI

```bash
oasr config set oasr.default_profile safe
oasr profile dev
```

### Via Environment Variable

```bash
export OASR_PROFILE=dev
```

### Via Config File

```toml
[oasr]
default_profile = "safe"
```

---

## Profile Settings Reference

### Filesystem Access

**`fs_read_roots`** (list of strings)
- Directories where agents can READ files
- Paths can be relative (`./`) or absolute (`~/projects`)
- Relative paths are workspace-relative (relative to cwd)

**`fs_write_roots`** (list of strings)
- Directories where agents can WRITE files
- Same path rules as `fs_read_roots`

**`deny_paths`** (list of strings)
- Paths that are ALWAYS denied (takes precedence over read/write roots)
- Use to protect sensitive files even if they're in allowed roots
- Examples: `~/.ssh`, `~/.aws`, `.env`

### Command Execution

**`allowed_commands`** (list of strings)
- Whitelist of commands agents can execute
- Only these commands are permitted
- Empty list with `deny_shell=false` allows all commands

**`deny_shell`** (boolean)
- If `true`: NO shell execution allowed (overrides `allowed_commands`)
- If `false`: Shell commands permitted (filtered by `allowed_commands`)
- Conservative default: `true`

### External Access

**`network`** (boolean)
- Allow agents to make network requests
- Conservative default: `false`

**`allow_env`** (boolean)
- Allow agents to read environment variables
- Protects API keys, tokens, and secrets in environment
- Conservative default: `false`

---

## Creating Custom Profiles

### Option 1: Config file

Edit `~/.oasr/config.toml` to add custom profiles:

```toml
[oasr]
default_profile = "safe"

# Development profile (more permissive)
[profiles.dev]
fs_read_roots = ["./", "~/projects"]
fs_write_roots = ["./", "~/projects/output", "./build"]
deny_paths = ["~/.ssh", "~/.aws", "~/.gnupg"]  # Still protect critical paths
allowed_commands = ["bash", "python", "node", "git", "curl", "npm", "pip"]
deny_shell = false
network = true
allow_env = true

# Testing profile (isolated)
[profiles.test]
fs_read_roots = ["./tests", "./fixtures"]
fs_write_roots = ["./test-output", "./.pytest_cache"]
deny_paths = ["~/.ssh", "~/.aws", "~/"]
allowed_commands = ["pytest", "coverage", "rg"]
deny_shell = true
network = false
allow_env = false

# CI/CD profile
[profiles.ci]
fs_read_roots = ["./", "/tmp/ci"]
fs_write_roots = ["./build", "./dist", "/tmp/ci"]
deny_paths = ["~/.ssh", "~/.aws"]
allowed_commands = ["npm", "python", "pytest", "git", "docker"]
deny_shell = false
network = true  # May need to fetch dependencies
allow_env = true  # CI environment variables needed
```

---

### Option 2: Profile files

Place profile files under `~/.oasr/profile/<name>.toml`. Each file contains only the profile keys (no `[profiles.<name>]` table):

```toml
fs_read_roots = ["./", "~/projects"]
fs_write_roots = ["./out"]
deny_paths = ["~/.ssh"]
allowed_commands = ["rg", "cat"]
deny_shell = true
network = false
allow_env = false
```

Inline config profiles override profile files with the same name.

## Using Profiles

### Select Profile Per Execution

```bash
# Use default profile
oasr exec my-skill -p "prompt"

# Override with specific profile
oasr exec my-skill -p "prompt" --profile dev

# Use profile from environment variable
export OASR_PROFILE=test
oasr exec my-skill -p "prompt"
```

### Select Default Profile Interactively

```bash
oasr profile
```

### Precedence

```
--profile flag > OASR_PROFILE env var > config file default_profile > "safe"
```

---

## Confirmation Flow

OASR requires user confirmation for risky execution contexts:

**Confirmation is required when:**
1. Input from stdin (non-interactive)
2. Prompt loaded from file (`-i/--instructions`)
3. Non-safe profile in use
4. Environment variable access enabled
5. Network access enabled
6. Shell execution allowed
7. `--confirm` flag used (force confirmation)

**Confirmation is NOT required for:**
- Interactive prompts (`-p "text"`)
- Safe profile with no risky flags
- When `--yes` flag is present (skip confirmation)

**Example confirmation screen:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTION POLICY REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Skill:             my-skill
Agent:             codex
Profile:           dev
Network:           allowed
Environment:       allowed
Shell:             allowed
Allowed commands:  bash, python, node, git...
Read roots:        ./, ~/projects
Write roots:       ./, ~/projects/output
Deny paths:        ~/.ssh, ~/.aws, ~/.gnupg

⚠  This execution requires confirmation due to:
   - Input from stdin (non-interactive)
   - Non-safe profile 'dev' in use
   - Network access enabled

Proceed? [y/N]
```

---

## Path Resolution

**Tilde expansion:**
- `~/documents` → `/home/user/documents`

**Relative paths:**
- `./data` → Relative to current working directory
- Resolved to absolute path internally

**Absolute paths:**
- `/usr/local/bin` → Used as-is

---

## Security Best Practices

### 1. Always Protect Sensitive Directories

```toml
deny_paths = [
    "~/.ssh",      # SSH keys
    "~/.aws",      # AWS credentials
    "~/.gnupg",    # GPG keys
    "~/.config",   # Application configs
    ".env",        # Environment secrets
]
```

### 2. Use Most Restrictive Profile That Works

Start with `safe`, add permissions as needed:

```bash
# Try with safe first
oasr exec skill -p "prompt"

# If it fails, try dev
oasr exec skill -p "prompt" --profile dev

# Create custom profile for the specific use case
```

### 3. Create Project-Specific Profiles

```toml
[profiles.python-project]
fs_read_roots = ["./"]
fs_write_roots = ["./build", "./dist"]
deny_paths = ["~/.ssh", "~/.aws"]
allowed_commands = ["python", "pytest", "pip", "rg"]
deny_shell = false
network = false
allow_env = false
```

### 4. Review Policy Before Confirming

Read the policy summary carefully before typing "yes" to confirm execution.

### 5. Use `--yes` Sparingly

Only use `--yes` to skip confirmation when:
- You trust the skill completely
- You've reviewed the skill's SKILL.md
- You understand what the skill will do
- You're in a CI/CD environment with appropriate isolation

---

## Validation

OASR validates profile references:

```bash
oasr config set oasr.default_profile nonexistent
# Error: Profile 'nonexistent' not found. Available profiles: safe, dev
```

**Bypass validation** (to set before creating profile):
```bash
oasr config set --force oasr.default_profile new-profile
# Then create [profiles.new-profile] in config.toml
```

---

## Examples

### Read-Only Analysis Profile

```toml
[profiles.readonly]
fs_read_roots = ["./data", "./documents"]
fs_write_roots = []  # No writes
deny_paths = ["~/.ssh", "~/.aws"]
allowed_commands = ["rg", "fd", "cat", "jq"]
deny_shell = true
network = false
allow_env = false
```

### Web Scraping Profile

```toml
[profiles.scraper]
fs_read_roots = ["./"]
fs_write_roots = ["./output", "./downloads"]
deny_paths = ["~/.ssh", "~/.aws"]
allowed_commands = ["curl", "wget", "python", "rg"]
deny_shell = false
network = true  # Required for scraping
allow_env = false
```

### Documentation Generation Profile

```toml
[profiles.docs]
fs_read_roots = ["./src", "./docs"]
fs_write_roots = ["./docs", "./build/docs"]
deny_paths = ["~/.ssh", "~/.aws"]
allowed_commands = ["python", "node", "rg", "fd"]
deny_shell = false
network = false
allow_env = false
```

---

## Troubleshooting

### Skill Fails with Safe Profile

**Symptom:** Skill execution fails or produces errors

**Solution:** Check policy summary to see what's denied, then:

1. Try with `dev` profile:
   ```bash
   oasr exec skill -p "prompt" --profile dev
   ```

2. Or create a custom profile with specific permissions needed

### Confirmation Always Required

**Symptom:** Always prompted for confirmation

**Cause:** Using non-safe profile or risky input method

**Solution:**
- Use `--yes` flag (if you trust the skill)
- Use safe profile for routine tasks
- Use `-p "text"` instead of piping stdin

### Profile Not Found

**Symptom:** `Profile 'name' not found`

**Solution:**
1. Check spelling: `oasr config list`
2. Create the profile in `~/.oasr/config.toml`
3. Or use built-in `safe` profile

---

## Related

- [Configuration Overview](README.md) - Full config guide
- [EXEC Command](../commands/EXEC.md) - Execution and security model
- [Environment Variables](environment-variables.md) - OASR_PROFILE details
- [Examples](examples/development.toml) - Ready-to-use profile examples
