# `oasr use`

Copy skills to a target directory. Supports glob patterns. Works with both local and remote skills.

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
