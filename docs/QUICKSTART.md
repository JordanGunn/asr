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

```bash
# Register a skill
oasr registry add /path/to/your/skill

# List registered skills
oasr registry list

# Copy a skill to your workspace (with tracking)
oasr use my-skill

# Check status of tracked skills
oasr diff

# Generate IDE adapters
oasr adapter cursor
```

See [Command Documentation](commands/.INDEX.md) for the full command reference.
