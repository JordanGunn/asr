# Agent Configuration

Configure which AI agent OASR uses to execute skills.

---

## Overview

OASR supports multiple AI agent backends. You can configure a default agent and override it per-execution.

**Available agents:**
- `codex` - GitHub Copilot CLI (codex)
- `copilot` - GitHub Copilot CLI (copilot)
- `claude` - Anthropic Claude CLI
- `opencode` - Custom OpenCode agent

---

## Setting Default Agent

### Via CLI

```bash
# Set default agent
oasr config set agent codex

# Verify
oasr config get agent
```

### Via Environment Variable

```bash
# Temporary (current session)
export OASR_AGENT=copilot

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OASR_AGENT=copilot' >> ~/.bashrc
```

### Via Config File

Edit `~/.oasr/config.toml`:

```toml
[agent]
default = "codex"
```

---

## Overriding Default

Use the `--agent` flag to override for a single execution:

```bash
# Config has codex, but use copilot for this execution
oasr exec my-skill -p "prompt" --agent copilot
```

**Precedence:** `--agent` flag > `OASR_AGENT` > config file > no default

---

## Agent Availability

OASR checks if agent binaries are installed:

```bash
oasr config list
```

**Output example:**
```
Available Agents
  ✓ codex         (installed)
  ✓ copilot       (installed)
  ✗ claude        (not installed)
  ✗ opencode      (not installed)
```

**Install agents:**
```bash
# GitHub Copilot CLI
npm install -g @github/copilot-cli

# Anthropic Claude CLI
pip install anthropic-cli

# Custom agents - check agent documentation
```

---

## No Default Agent

If no default is configured:

```bash
oasr exec skill -p "prompt"
# Error: No agent configured. Set OASR_AGENT, use --agent flag, or run:
#   oasr config set agent <name>
```

**Resolution:**
```bash
# Option 1: Set default
oasr config set agent codex

# Option 2: Use flag
oasr exec skill -p "prompt" --agent codex

# Option 3: Use env var
export OASR_AGENT=codex
oasr exec skill -p "prompt"
```

---

## Agent-Specific Settings

Currently, OASR treats all agents uniformly. Future versions may support agent-specific configuration:

```toml
# Future (not yet implemented)
[agent.codex]
model = "gpt-4"
temperature = 0.7

[agent.claude]
model = "claude-3-opus"
```

---

## Validation

OASR validates agent names when setting:

```bash
oasr config set agent invalid
# Error: Invalid agent 'invalid'. Valid agents: codex, copilot, claude, opencode
```

**Bypass validation** (use carefully):
```bash
oasr config set --force agent custom-agent
```

---

## Examples

### Development Workflow

```bash
# Set default for the project
export OASR_AGENT=codex

# Try different agent for comparison
oasr exec skill -p "refactor code" --agent copilot
oasr exec skill -p "refactor code" --agent claude
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
env:
  OASR_AGENT: codex

steps:
  - run: oasr exec test-skill -p "run tests"
```

### Multiple Projects

```bash
# Project A uses codex
cd ~/projects/project-a
export OASR_AGENT=codex
oasr exec skill -p "prompt"

# Project B uses copilot
cd ~/projects/project-b
export OASR_AGENT=copilot
oasr exec skill -p "prompt"
```

---

## Related

- [Configuration Overview](README.md) - Full config guide
- [Environment Variables](environment-variables.md) - OASR_AGENT details
- [Configuration Precedence](precedence.md) - How overrides work
