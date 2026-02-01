# `oasr use` [DEPRECATED]

> **warning**  
> **This command is deprecated.** Use [`oasr clone`](CLONE.md) instead.  
> `oasr use` will be removed in v0.5.0.

Copy skills to a target directory. Supports glob patterns. Works with both local and remote skills.

## Migration

Replace `oasr use` with `oasr clone`:

```bash
# Old (deprecated)
oasr use skill-name

# New
oasr clone skill-name
```

All functionality is identical. See [`oasr clone`](CLONE.md) for full documentation.

## Why the Change?

The command was renamed to `clone` for clarity:
- **"clone"** better conveys the action (copying from source)
- Familiar terminology in the developer world (like `git clone`)
- Clearer distinction from execution (`oasr exec`)

## Legacy Documentation

> **note**  
> `oasr use` provides an open-closed extension mechanism for using skills with any agentic provider.

```bash
oasr use skill-name
oasr use skill-name -d /path/to/project
oasr use "git-*"                    # Glob pattern
oasr use skill-one skill-two        # Multiple skills
```

> **note**  
> Remote skills are automatically fetched during copy.

*Using skills*
![oasr use](../.images/use.png)

---

**See Also:**
- [`oasr clone`](CLONE.md) — Replacement command
- [`oasr exec`](EXEC.md) — Execute skills without cloning
