# `oasr completion`

Enable shell tab completion for OASR commands, subcommands, and dynamic resources (skills, agents, profiles).

---

## Overview

The `oasr completion` command provides intelligent tab completion across all major shells:

- **Bash** — Traditional completion with dynamic skill/agent/profile suggestions
- **Zsh** — Rich completions with descriptions and type hints
- **Fish** — Native Fish completions with helper functions
- **PowerShell** — ArgumentCompleter with tooltips

Completions are **dynamic**: skill names, agents, and profiles are fetched live from your registry.

---

## Usage

```bash
# Output completion script for current shell (auto-detected)
oasr completion

# Output for specific shell
oasr completion bash
oasr completion zsh
oasr completion fish
oasr completion powershell

# Install to standard location for current shell
oasr completion install

# Install for specific shell
oasr completion install bash
oasr completion bash --install  # Shortcut for install
oasr completion install --force  # Overwrite existing

# Uninstall
oasr completion uninstall

# Dry run (show what would be done)
oasr completion install --dry-run
```

---

## Installation

### Automatic (Recommended)

```bash
# Auto-detect shell and install
oasr completion install

# Install for a specific shell (shortcut)
oasr completion zsh --install

# Restart your shell or source the completion file
# Bash:
source ~/.bash_completion.d/oasr

# Zsh:
# Ensure fpath is set and compinit is initialized (recommended):
#   fpath=(~/.zsh/completion $fpath)
#   autoload -Uz compinit && compinit

# Fish: (automatically loaded)

# PowerShell: (add to profile if not present)
. ~/.config/powershell/oasr_completion.ps1
```

### Manual Installation

If you prefer manual control, output the script and place it yourself:

```bash
# Bash
oasr completion bash > ~/.bash_completion.d/oasr
source ~/.bash_completion.d/oasr

# Zsh
oasr completion zsh > ~/.zsh/completion/_oasr
# Add to ~/.zshrc before compinit:
# fpath=(~/.zsh/completion $fpath)
# autoload -Uz compinit && compinit

# Fish
oasr completion fish > ~/.config/fish/completions/oasr.fish

# PowerShell
oasr completion powershell > ~/.config/powershell/oasr_completion.ps1
# Add to $PROFILE:
# . ~/.config/powershell/oasr_completion.ps1
```

---

## What Gets Completed

### Commands & Subcommands

```bash
oasr <TAB>
# Shows: add, about, adapter, clone, completion, config, diff, exec, find, help, info, list, registry, rm, status, sync, update, validate

oasr registry <TAB>
# Shows: add, list, prune, rm, sync, validate

oasr profile <TAB>
# Shows: list, show, edit, rm, new, wizard

oasr profile rm <TAB>
# Shows: safe, dev, custom-profile, ...

oasr profile edit <TAB>
# Shows: -s, --select, safe, dev, custom-profile, ...

oasr config <TAB>
# Shows: get, list, set, unset, validate
```

### Dynamic Resources

```bash
# Skill names (from your registry)
oasr info <TAB>
# Shows: git-commit, code-review, doc-generator, ...

oasr exec <TAB>
# Shows: git-commit, code-review, doc-generator, ...

# Agent types
oasr config set agent <TAB>
# Shows: codex, copilot, claude, openai, gemini

# Profiles
oasr exec --profile <TAB>
# Shows: safe, default, permissive, ...

# Config keys
oasr config get <TAB>
# Shows: agent, profile, validation.strict, adapter.default, ...
```

### Flags & Options

All commands provide flag completion:

```bash
oasr add --<TAB>
# Shows: --source, --no-track, --help

oasr exec --<TAB>
# Shows: --profile, --yes, --confirm, --help

oasr adapter --<TAB>
# Shows: --output-dir, --adapter, --force, --help
```

---

## Configuration

### Enable/Disable via Config

```toml
# ~/.config/oasr/config.toml
[oasr]
completions = true  # Enable (default)
# completions = false  # Disable
```

Or via environment variable:

```bash
export OASR_OASR_COMPLETIONS=true
```

When disabled, `oasr completion install` will skip installation.

### Installation Paths

Completions are installed to standard shell-specific locations:

| Shell       | Path                                      |
|-------------|-------------------------------------------|
| Bash        | `~/.bash_completion.d/oasr`              |
| Zsh         | `~/.zsh/completion/_oasr`                |
| Fish        | `~/.config/fish/completions/oasr.fish`   |
| PowerShell  | `~/.config/powershell/oasr_completion.ps1` |

### Backup on Overwrite

If you run `oasr completion install` and a completion file already exists, it will:

1. **Without `--force`**: Prompt for confirmation
2. **With `--force`**: Create a backup at `<path>.backup` before overwriting

---

## Shell-Specific Notes

### Bash

- Requires `bash-completion` package on most systems
- Sources files from `~/.bash_completion.d/` automatically (if configured)
- Add to `~/.bashrc` if not auto-loaded:
  ```bash
  [ -f ~/.bash_completion.d/oasr ] && source ~/.bash_completion.d/oasr
  ```

### Zsh

- Uses `#compdef` directive for native Zsh completion system
- Provides rich descriptions for subcommands
- Add to `~/.zshrc` if not auto-loaded:
  ```zsh
  fpath=(~/.zsh/completion $fpath)
  autoload -Uz compinit && compinit
  ```

### Fish

- Uses native `complete -c` syntax
- Automatically loaded from `~/.config/fish/completions/`
- No additional configuration needed

### PowerShell

- Uses `Register-ArgumentCompleter` API
- Provides tooltips for commands
- Add to PowerShell profile:
  ```powershell
  . ~/.config/powershell/oasr_completion.ps1
  ```
- Find profile location: `echo $PROFILE`

---

## Troubleshooting

### Completions Not Working

1. **Verify installation**:
   ```bash
   oasr completion install
   ```

2. **Check shell detection**:
   ```bash
   oasr completion  # Should output script for current shell
   ```

3. **Restart shell** or source the completion file manually

4. **Check shell configuration**:
   - Bash: `~/.bashrc` should source `~/.bash_completion.d/oasr`
   - Zsh: `~/.zshrc` should have `fpath` and `compinit`
   - Fish: Automatically loaded
   - PowerShell: `$PROFILE` should source the completion script

### Dynamic Completions Slow

If skill/agent/profile completions are slow:

- Dynamic completions call `oasr` commands (e.g., `oasr registry list --quiet`)
- Large registries may cause slight delays
- Completions are generated on-demand (not cached)

### Wrong Shell Detected

Specify the shell explicitly:

```bash
oasr completion install zsh
```

Or set `$SHELL` environment variable:

```bash
export SHELL=/bin/zsh
oasr completion install
```

---

## Examples

### Install for Current Shell

```bash
$ oasr completion install
Installing completion for zsh...
Completion installed to: /home/user/.zsh/completion/_oasr

To activate:
  # Ensure fpath + compinit are set, then restart your shell
  fpath=(~/.zsh/completion $fpath)
  autoload -Uz compinit && compinit
```

### Generate Script for Manual Review

```bash
$ oasr completion bash > /tmp/oasr_completion.bash
$ less /tmp/oasr_completion.bash
# Review script before installing
$ cp /tmp/oasr_completion.bash ~/.bash_completion.d/oasr
```

### Install with Dry Run

```bash
$ oasr completion install --dry-run
[DRY RUN] Would install completion for zsh
[DRY RUN] Target path: /home/user/.zsh/completion/_oasr
[DRY RUN] File exists: False
[DRY RUN] Would create directory: /home/user/.zsh/completion
[DRY RUN] Would write 259 bytes
```

### Force Overwrite

```bash
$ oasr completion install --force
Backing up existing completion to: /home/user/.zsh/completion/_oasr.backup
Installing completion for zsh...
Completion installed to: /home/user/.zsh/completion/_oasr
```

---

## See Also

- [`oasr config`](CONFIG.md) — Configure completion behavior
- [`oasr help`](HELP.md) — Get help on commands
- [Commands Index](.INDEX.md) — All available commands
