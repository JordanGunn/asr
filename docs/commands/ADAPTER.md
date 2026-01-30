# `oasr adapter`

Generate IDE-specific adapter files that delegate to your canonical skills. All adapters are sourced from your `oasr` registry.

```bash
oasr adapter                              # All default targets
oasr adapter cursor                       # Cursor only
oasr adapter windsurf                     # Windsurf only
oasr adapter codex                        # Codex only
oasr adapter copilot                      # GitHub Copilot
oasr adapter claude                       # Claude Code
oasr adapter --exclude skill1,skill2
oasr adapter --output-dir /path/to/project
```

> **note**  
> The `--copy` flag is deprecated but kept for backward compatibility. Local copying is now the default behaviour.

**Behavior:**

- Skills are automatically copied to `.{ide}/skills/` directories
- Adapter files use relative paths to copied skills
- Remote skills are fetched during generation

**Output Structure:**

```text
.windsurf/
├── skills/my-skill/             ← copied from source (local or remote)
└── workflows/my-skill.md        → points to ../skills/my-skill/
```

## Adapter Outputs

| Target   | Output Path                      |
|----------|----------------------------------|
| cursor   | `.cursor/commands/{skill}.md`    |
| windsurf | `.windsurf/workflows/{skill}.md` |
| codex    | `.codex/skills/{skill}.md`       |
| copilot  | `.github/prompts/*.prompt.md`    |
| claude   | `.claude/commands/{skill}.md`    |

*Generating adapters*
![oasr adapter](../.images/adapter.png)