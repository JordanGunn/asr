# `oasr validate`

Validate skill structure and `SKILL.md` frontmatter.

```bash
oasr validate /path/to/skill
oasr validate --all                 # All registered skills
oasr validate --all --strict        # Treat warnings as errors
```

See [VALIDATION.md](VALIDATION.md) for validation error and warning codes.

> **note**  
> Validation is performed automatically when syncing manifests or adding skills to the `oasr` registry.
