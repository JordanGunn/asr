# Quickstart

## Install with uv (recommended)

```bash
git clone https://github.com/OWNER/oasr.git
cd oasr
uv pip install -e .
```

## Install with pip

```bash
git clone https://github.com/OWNER/oasr.git
cd oasr
pip install -e .
```

## Global Installation

To make `oasr` available system-wide:

```bash
# macOS/Linux
./install.sh

# Windows (PowerShell)
.\install.ps1
```

This installs into an isolated environment and adds shims to your PATH (`~/.local/bin` on Unix, `%LOCALAPPDATA%\oasr\bin` on Windows).

## Verify Installation

```bash
oasr --version
```

## First Steps

```bash
# Register a skill
oasr add /path/to/your/skill

# List registered skills
oasr list

# Generate IDE adapters
oasr adapter cursor
```

See [COMMANDS.md](COMMANDS.md) for the full command reference.
