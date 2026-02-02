# Adapter Configuration

Configure IDE adapter targets and settings.

---

## Overview

OASR can generate IDE-specific configuration files (adapters) for tools like Cursor and Windsurf.

---

## Settings

### default_targets

**Default IDE targets for adapter generation.**

- **Type:** List of strings
- **Default:** `["cursor", "windsurf"]`
- **Valid values:** IDE names (`cursor`, `windsurf`, `vscode`, etc.)

**Via CLI:**
```bash
oasr config set adapter.default_targets cursor,vscode
```

**Via Environment Variable:**
```bash
export OASR_ADAPTER_TARGETS=cursor,windsurf,vscode
```

**Via Config File:**
```toml
[adapter]
default_targets = ["cursor", "windsurf", "vscode"]
```

---

## Usage

### Generate Adapters

```bash
# Use default targets from config
oasr adapter skill-name

# Override with specific targets
oasr adapter skill-name --targets cursor,vscode
```

### Common Configurations

**Cursor only:**
```toml
[adapter]
default_targets = ["cursor"]
```

**Multiple IDEs:**
```toml
[adapter]
default_targets = ["cursor", "windsurf", "vscode"]
```

---

## Related

- [Configuration Overview](README.md)
- [ADAPTER Command](../commands/ADAPTER.md)
