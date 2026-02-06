# OASR Features

OASR (Open Agent Skill Registry) is a CLI tool for managing agent skills across your development environment. This guide highlights the key features that make OASR powerful and easy to use.

---

## 1. Centralized Registry with Drift Detection

Keep your skills organized in a single registry while preserving your source implementations.

**How it works:**
- Skills are registered from their source path (local directory or remote repo)
- Content hashing detects when source skills have changed
- Your source implementations stay safe—OASR tracks, not moves

```bash
# Register a skill from your source directory
oasr registry add ~/skills/my-analyzer

# Check for changes across all registered skills
oasr registry sync

# Example output:
# ✓ grep: OK - up to date
# ⚠ my-analyzer: outdated (source changed)
# ✓ find: OK - up to date
```

**Benefits:**
- Single source of truth for all your skills
- Automatic detection of stale or modified skills
- Non-destructive—your source files are never modified

---

## 2. Clone Skills Anywhere

Create registry-tracked copies of your skills in any directory.

**How it works:**
- Clone registered skills to your current working directory
- Clones are automatically tracked by OASR
- Enables validation, synchronization, pruning, and change detection

```bash
# Clone a single skill to current directory
oasr clone my-analyzer

# Clone multiple skills at once
oasr clone grep find code-reviewer

# Clone to a specific directory
oasr clone my-analyzer --target ./skills/
```

**Benefits:**
- Keep project-specific skill copies organized
- Tracked clones stay in sync with your registry
- Easy cleanup with `oasr sync --prune`

---

## 3. Generate Adapters for Agentic Tools

Create skill integrations for popular AI coding assistants.

**How it works:**
- Generate OASR clones formatted for specific tools
- Supports Cursor, Windsurf, Claude, Codex, and more
- Tools with custom command support get thin invocation layers

```bash
# Generate adapters for default targets
oasr adapter generate

# Generate for specific tools
oasr adapter generate --target cursor
oasr adapter generate --target windsurf

# List available adapter targets
oasr adapter list
```

**Supported integrations:**
- **Cursor** — Custom commands for skill invocation
- **Windsurf** — Workflow integration
- **Claude** — Project skill configuration
- **Codex** — Compatible skill format

**Benefits:**
- Use your skills across multiple AI assistants
- Automatic format conversion per tool
- Custom command layers for seamless invocation

---

## 4. Local Synchronization and Drift Detection

Detect and resolve drift between your working directory and registry.

**How it works:**
- OASR auto-detects skills tracked in your current project
- Compare local copies against your registry state
- Sync changes from source to your working directory

```bash
# From your project directory
cd ~/projects/my-app

# Check status of tracked skills
oasr diff
# my-analyzer: outdated (registry updated)
# grep: OK

# Sync all tracked skills with registry
oasr sync
# ✓ my-analyzer: updated
# ✓ grep: up to date

# Remove skills no longer in registry
oasr sync --prune
```

**Workflow example:**
1. You're working in `~/projects/my-app`
2. You switch to `~/skills/my-analyzer` and make improvements
3. Back in your project, run `oasr sync` to pull the changes
4. Your project now has the updated skill

---

## 5. Local and Remote Skill Registration

Register skills from local paths or remote repositories with consistent validation.

**Local skills:**
```bash
# Register from a local directory
oasr registry add ./skills/code-reviewer
oasr registry add ~/shared-skills/formatter
```

**Remote skills (GitHub/GitLab):**
```bash
# Register directly from a repository
oasr registry add https://github.com/org/awesome-skill
oasr registry add https://gitlab.com/team/analyzer-skill

# Works with any default branch (main, master, etc.)
```

**What OASR validates:**
- Skill manifest structure and required fields
- Content integrity via hashing
- Remote accessibility and format

```bash
# Validate all registered skills
oasr registry validate

# Example output:
# ✓ grep: valid
# ✓ awesome-skill: valid (remote)
# ✗ broken-skill: missing manifest.yaml
```

---

## 6. Execute Skills Like CLI Commands

Run any registered skill from anywhere on your system.

**Basic execution:**
```bash
# Execute a skill by name
oasr exec grep "find all TODO comments"
oasr exec code-reviewer "review the auth module"

# Works from any directory
cd /tmp && oasr exec my-skill "do something"
```

**Configure your default agent:**
```bash
# Set your preferred agent CLI
oasr config set agent.default "aider"
oasr config set agent.default "claude"

# Now skills execute through your agent
oasr exec analyzer "check for security issues"
```

**Security through profiles:**

Skills execute under configurable security policies that protect against:
- **Prompt injection** — restricted command execution
- **Destructive operations** — controlled filesystem access
- **Network exposure** — optional network capability
- **Unintended side effects** — scoped read/write roots

```bash
# Execute with a specific security profile
oasr exec --profile strict my-skill "sensitive task"

# Or set a default profile
oasr config set oasr.default_profile safe
```

---

## 7. Configurable Security Profiles

Customize your runtime environment with flexible security policies.

**Built-in profiles:**

| Profile | Use Case | Filesystem | Shell | Network |
|---------|----------|------------|-------|---------|
| `safe` | Default, balanced | Read: `./`, Write: `./out` | Restricted | Disabled |
| `strict` | Maximum security | Read: `./`, Write: none | Denied | Disabled |
| `dev` | Development work | Read/Write: `./` | Allowed | Enabled |
| `unsafe` | Full access (use carefully) | Unrestricted | Allowed | Enabled |

**Switch profiles:**
```bash
# Interactive profile selector
oasr profile

# Set directly
oasr profile dev

# View current profile settings
oasr profile show
```

**Create custom profiles:**

```bash
# Create from template
oasr profile new my-project

# Copy and customize an existing profile
oasr profile new prod-safe -c safe

# Interactive wizard with guided prompts
oasr profile wizard
```

**Profile settings you can configure:**
- `fs_read_roots` — Directories allowed for reading
- `fs_write_roots` — Directories allowed for writing
- `deny_paths` — Explicitly blocked paths (supports globs like `**/.env`)
- `allowed_commands` — Whitelisted shell commands
- `deny_shell` — Block all shell execution
- `network` — Enable/disable network access
- `allow_env` — Expose environment variables

**Example custom profile:**
```toml
# ~/.oasr/profiles/my-project.toml
fs_read_roots = ["/home/user/projects/my-app"]
fs_write_roots = ["/home/user/projects/my-app/src"]
deny_paths = ["**/.env", "**/secrets/**", "~/.ssh"]
allowed_commands = ["rg", "fd", "jq", "cat", "git"]
deny_shell = false
network = false
allow_env = false
```

---

## Quick Start

```bash
# Install
pip install oasr

# Register your first skill
oasr registry add ./my-skill

# Clone to your project
cd ~/my-project
oasr clone my-skill

# Execute it
oasr exec my-skill "do the thing"

# Keep it synced
oasr sync
```

---

## Learn More

- [Quickstart Guide](QUICKSTART.md) — Get up and running
- [Command Reference](commands/.INDEX.md) — All available commands
- [Configuration Guide](configuration/README.md) — Customize OASR
- [Security Profiles](configuration/profiles.md) — Deep dive on profiles
