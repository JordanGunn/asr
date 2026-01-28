# Quickstart

## Install with uv (recommended)

```bash
git clone https://github.com/OWNER/asr.git
cd asr
uv pip install -e .
```

## Install with pip

```bash
git clone https://github.com/OWNER/asr.git
cd asr
pip install -e .
```

## Global Installation

To make `asr` available system-wide:

```bash
# macOS/Linux
./install.sh

# Windows (PowerShell)
.\install.ps1
```

This installs into an isolated environment and adds shims to your PATH (`~/.local/bin` on Unix, `%LOCALAPPDATA%\asr\bin` on Windows).

## Verify Installation

```bash
asr --version
```

## First Steps

```bash
# Register a skill
asr add /path/to/your/skill

# List registered skills
asr list

# Generate IDE adapters
asr adapter cursor
```

See [COMMANDS.md](COMMANDS.md) for the full command reference.
