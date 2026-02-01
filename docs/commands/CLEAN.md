# `oasr clean` (DEPRECATED)

> **⚠️ Warning: This command is deprecated and will be removed in v0.6.0.**  
> Use `oasr registry prune` instead.

Remove orphaned manifests and entries for missing skills.

```bash
oasr clean              # Shows deprecation warning
oasr registry prune     # New command (recommended)
```

This command now delegates to `oasr registry prune`. See [REGISTRY.md](./REGISTRY.md#oasr-registry-prune) for full documentation.
