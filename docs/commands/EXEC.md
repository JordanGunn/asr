# `oasr exec`

Execute skills as CLI tools from anywhere on your system. Run skills with agent-driven execution without needing to clone them first.

## Usage

```bash
oasr exec <skill-name> [options]
```

## Options

- `-p, --prompt TEXT` — Inline prompt/instructions for the agent
- `-i, --instructions FILE` — Read prompt from a file
- `-a, --agent AGENT` — Override the default agent (codex, copilot, claude, opencode)

## Features

### Execute Skills Anywhere

Run skills from any directory without cloning:

```bash
# No need to be in a specific directory
cd ~/projects/data-analysis
oasr exec csv-analyzer -p "Summarize sales data from report.csv"
```

### Multiple Prompt Input Methods

#### 1. Inline Prompt (`-p`)
Quick, one-line prompts:
```bash
oasr exec code-reviewer -p "Review this file for security issues"
```

#### 2. File-based Instructions (`-i`)
Complex, multi-line instructions:
```bash
oasr exec api-generator -i requirements.txt
```

Where `requirements.txt` contains:
```
Create a REST API with the following endpoints:
- GET /users - List all users
- POST /users - Create a user
- GET /users/:id - Get user by ID
Include error handling and validation.
```

#### 3. Stdin (Pipe)
Pipeline integration:
```bash
echo "Explain these changes" | oasr exec code-explainer

git diff | oasr exec code-reviewer -p "Review for bugs"

cat api-spec.yaml | oasr exec api-generator
```

### Agent Selection

#### Default Agent (from config)
```bash
# Set default once
oasr config set agent codex

# Use without specifying agent
oasr exec my-skill -p "Do something"
```

#### Override Agent (per-execution)
```bash
oasr exec my-skill --agent copilot -p "Generate code"
```

### Skill Execution Flow

1. **Load skill** from registry by name
2. **Read prompt** from `-p`, `-i`, or stdin
3. **Select agent** from `--agent` flag or config default
4. **Inject skill** content into agent prompt
5. **Execute** agent CLI with formatted prompt
6. **Stream output** to stdout

## Examples

### Basic Execution

```bash
# Execute with inline prompt
oasr exec csv-analyzer -p "Analyze sales trends"

# Execute with file-based instructions
oasr exec code-generator -i requirements.txt

# Execute with stdin
git log --oneline -10 | oasr exec commit-summarizer
```

### Real-World Workflows

#### Data Analysis
```bash
cd ~/data
oasr exec csv-analyzer -p "Generate summary statistics for all CSV files"
```

#### Code Review
```bash
git diff main..feature-branch | oasr exec code-reviewer -p "Review for security and performance"
```

#### Documentation Generation
```bash
oasr exec doc-generator -p "Generate API documentation for src/api.py"
```

#### Test Generation
```bash
oasr exec test-generator -p "Create pytest tests for src/utils.py"
```

### Multi-step Workflows

Combine with shell scripting:

```bash
#!/bin/bash
# analyze-project.sh

echo "Analyzing codebase..."
oasr exec code-analyzer -p "Analyze project structure" > analysis.txt

echo "Generating tests..."
oasr exec test-generator -i analysis.txt > tests.py

echo "Reviewing tests..."
cat tests.py | oasr exec code-reviewer -p "Review test coverage"
```

### Agent-specific Execution

```bash
# Use Codex for code generation
oasr exec api-generator --agent codex -p "Create REST API"

# Use Copilot for suggestions
oasr exec refactor-helper --agent copilot -p "Suggest improvements"

# Use Claude for analysis
oasr exec code-explainer --agent claude -p "Explain this pattern"
```

## Error Handling

### Skill Not Found

```bash
oasr exec nonexistent-skill -p "test"
```

Output:
```
Error: Skill 'nonexistent-skill' not found in registry

Use 'oasr registry list' to see available skills.
```

### No Agent Configured

```bash
oasr exec my-skill -p "test"
```

Output:
```
Error: No agent configured

Configure a default agent with:
  oasr config set agent <agent-name>

Or specify an agent for this command:
  oasr exec --agent <agent-name> <skill>

Available agents:
  ✓ codex
  ✗ copilot
  ✗ claude
  ✗ opencode
```

### Agent Binary Not Available

```bash
oasr exec my-skill --agent copilot -p "test"
```

Output:
```
Error: Agent 'copilot' is not available

Available agents:
  ✓ codex
  ✗ copilot
  ✗ claude
  ✗ opencode
```

### No Prompt Provided

```bash
oasr exec my-skill
```

Output:
```
Error: No prompt provided

Provide a prompt using one of:
  -p/--prompt 'Your prompt here'
  -i/--instructions path/to/file.txt
  echo 'Your prompt' | oasr exec <skill>
```

### Missing Skill File

```bash
oasr exec my-skill -p "test"
```

Output:
```
Error: Skill file not found: ~/.oasr/registry/my-skill/SKILL.md

Try running 'oasr sync' to update your skills.
```

## How It Works

### Prompt Injection

Skills are executed by injecting their content into the agent prompt:

```
You are executing a skill. Follow these instructions carefully:

━━━━━━━━ SKILL INSTRUCTIONS ━━━━━━━━
[Full SKILL.md content here]
━━━━━━━━ END SKILL ━━━━━━━━

USER REQUEST: [Your prompt here]

Working directory: [Current directory]
Execute the skill above for this request.
```

This ensures:
- Agent sees complete skill context
- User prompt is clearly separated
- Working directory is specified
- Instructions are unambiguous

### Agent CLI Commands

Each agent has a specific CLI format:

| Agent | Command |
|-------|---------|
| Codex | `codex exec "<injected-prompt>"` |
| Copilot | `copilot -p "<injected-prompt>"` |
| Claude | `claude <injected-prompt> -p` |
| OpenCode | `opencode run "<injected-prompt>"` |

### Execution Context

Skills execute in the **current working directory**:

```bash
cd ~/projects/my-app
oasr exec test-generator -p "Generate tests"
# Agent sees files in ~/projects/my-app
```

This allows skills to:
- Read local files
- Write output to current directory
- Execute project-specific commands

## Comparison with `oasr clone`

| Feature | `oasr exec` | `oasr clone` |
|---------|------------|-------------|
| **Use case** | Execute once | Reuse multiple times |
| **Requires cloning** | No | Yes |
| **Works anywhere** | Yes | No (destination required) |
| **Tracking metadata** | N/A | Yes |
| **Agent-driven** | Yes | No |
| **Best for** | Quick tasks, scripts | IDE integration, adapters |

### When to use `oasr exec`
- One-off tasks
- Shell scripts and automation
- Quick analysis or generation
- Pipeline integration

### When to use `oasr clone`
- IDE/editor integration
- Repeated manual use
- Tracking skill versions
- Working offline

## Configuration

### Set Default Agent

```bash
oasr config set agent codex
```

### Check Available Agents

```bash
oasr config list
```

Look for the **Available Agents** section.

## Related Commands

- [`oasr config`](CONFIG.md) — Configure default agent
- [`oasr clone`](CLONE.md) — Clone skills to directory
- [`oasr registry`](REGISTRY.md) — Manage skill registry

## Installation

Ensure your chosen agent CLI is installed and in PATH:

### Codex
```bash
# Install Codex CLI (example)
npm install -g @codex/cli
```

### Copilot
```bash
# Install GitHub Copilot CLI
gh extension install github/gh-copilot
```

### Claude
```bash
# Install Claude CLI (example)
pip install anthropic-cli
```

### OpenCode
```bash
# Install OpenCode CLI (example)
npm install -g opencode-cli
```

Check installation:
```bash
which codex copilot claude opencode
```

## Advanced Usage

### Stdin with Additional Prompt

Combine stdin with inline prompt:

```bash
git diff | oasr exec code-explainer -p "Focus on security implications"
```

The stdin content is used as the primary prompt, with `-p` adding context.

### Environment Variables

Pass environment context to skills:

```bash
export PROJECT_TYPE=react
oasr exec scaffold-generator -p "Generate component structure"
```

Skills can access environment variables through the agent.

### Output Redirection

Capture skill output:

```bash
oasr exec code-generator -p "Create API client" > api_client.py
oasr exec doc-generator -p "Document functions" > docs.md
```

### Error Handling in Scripts

Check exit codes:

```bash
if oasr exec validator -p "Check code quality"; then
    echo "✓ Validation passed"
else
    echo "✗ Validation failed"
    exit 1
fi
```

## Tips & Best Practices

1. **Be specific in prompts**: The more detailed your prompt, the better the output
2. **Use file-based instructions** for complex requirements
3. **Configure default agent** to avoid typing `--agent` repeatedly
4. **Chain commands** in scripts for powerful workflows
5. **Check agent availability** before relying on specific agents
6. **Use stdin** for seamless pipeline integration

## Troubleshooting

### Command Not Found: oasr

Ensure OASR is installed:
```bash
pip install oasr
```

### Skill Execution Hangs

Some agents may require confirmation or input. Check agent documentation.

### Permission Denied

Ensure agent CLI has necessary permissions:
```bash
chmod +x $(which codex)
```

### Skills Not Found

Sync registry:
```bash
oasr registry sync
```

Or add skills:
```bash
oasr registry add <skill-source>
```
