# `oasr status` (Deprecated in v0.3.0)

> **⚠️ DEPRECATED**  
> As of v0.3.0, this functionality has been replaced by:
> - `oasr registry -v` - Validate registry skills with verbose output
> - `oasr diff` - Show status of tracked skills (copied with `oasr use`)

## Migration

### Registry Validation

```bash
# Old (v0.2.0)
oasr status

# New (v0.3.0)
oasr registry              # Basic validation
oasr registry -v           # Verbose (similar to old status)
```

See [oasr registry](REGISTRY.md) for registry validation.

### Tracked Skills Status

For skills copied with `oasr use`, use the new `oasr diff` command:

```bash
# New in v0.3.0
oasr diff                  # Show tracked skill status
oasr diff /path/to/project
```

See [oasr diff](DIFF.md) for tracked skill status.
