# Quickstart

---

## Option A: Global Installation

To make `oasr` available system-wide:

```bash
# macOS/Linux
./install.sh

# Windows (PowerShell)
.\install.ps1
```

This installs into an isolated environment and adds shims to your PATH (`~/.local/bin` on Unix, `%LOCALAPPDATA%\oasr\bin` on Windows).

## Option B: Install from PyPI with `pip`

```bash
pip install oasr
```

## Option C: Install from PyPI with `uv`

```bash
uv pip install oasr
```

## Option D: Install from source

```bash
git clone https://github.com/JordanGunn/oasr.git
cd oasr
uv pip install -e .
```

---

## Verify Installation

```bash
oasr --version
```

---

## First Steps

### Basic Workflow

```bash
# Register a skill
oasr registry add /path/to/your/skill

# Or add from a remote repository
oasr registry add https://github.com/user/skill-repo

# List registered skills
oasr registry list

# Clone a skill to your workspace (with tracking)
oasr clone my-skill

# Check status of tracked skills
oasr diff
```

### Execute Skills (v0.4.0)

```bash
# Configure your preferred agent
oasr config set agent codex

# Execute a skill from anywhere
oasr exec my-skill -p "Your prompt here"

# Use with pipes for powerful workflows
git diff | oasr exec code-reviewer -p "Review these changes"
```

### IDE Integration

```bash
# Generate adapters for your IDE
oasr adapter cursor
oasr adapter windsurf
```

## Common Workflows

### Workflow 1: Clone and Use in IDE
Best for repeated manual use with IDE integration.

```bash
# Add skills to registry
oasr registry add https://github.com/user/skills

# Clone to your project
cd ~/my-project
oasr clone csv-analyzer

# Adapt for your IDE
oasr adapter cursor
```

### Workflow 2: Direct Execution
Best for automation, scripts, and one-off tasks.

```bash
# Configure default agent once
oasr config set agent codex

# Execute skills directly (no cloning needed)
oasr exec data-analyzer -p "Summarize report.csv"
oasr exec test-generator -p "Generate tests for api.py"

# Use in shell scripts
#!/bin/bash
git log -10 | oasr exec commit-summarizer > summary.txt
```

### Workflow 3: Multi-skill Repository
Work with repositories containing multiple skills.

```bash
# Add repository (auto-detects all skills)
oasr registry add https://github.com/org/skill-collection
# Found 5 skills. Add all? [Y/n]: y

# List added skills
oasr registry list

# Use any skill from the collection
oasr exec python-formatter -p "Format all Python files"
oasr exec doc-generator -p "Generate API docs"
```

See [Command Documentation](commands/.INDEX.md) for the full command reference.
