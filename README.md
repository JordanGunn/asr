# ASR

**Agent Skill Registry** — Manage reusable AI agent skills across IDEs without drift.

---

## The Problem

You've built useful skills for your AI coding assistant. They work great in Cursor. Now you want them in Windsurf. And Claude. And Copilot.

Each tool expects skills in different locations with different formats:
- Cursor: `.cursor/skills/`
- Windsurf: `.windsurf/skills/`
- Claude: `.claude/commands/`
- Copilot: `.github/.md`

So you copy your skills everywhere. Then you improve one. Now the copies are stale. You forget which version is current. Some break silently. This is **skill drift**.

## The Solution

ASR keeps your skills in one place and generates thin adapters for each IDE.

```
┌─────────────────────────────────────────────────────────┐
│           Your Skills (canonical source)                │
│           ~/skills/git-commit/SKILL.md                  │
│           ~/skills/code-review/SKILL.md                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
                   asr adapter
                        │
        ┌───────────────┼──────────────┐...───────────────┐
        ▼               ▼              ▼                  ▼
   .cursor/        .windsurf/       .claude/           <vendor>/
   commands/       workflows/       commands/           skills/
```

No copying. No drift. One source of truth.

---

## Quick Example

```bash
# Register your skills
asr add ~/skills/git-commit
asr add ~/skills/code-review

# Generate adapters for a project
asr adapter --output-dir ~/projects/my-app

# Result:
# ~/projects/my-app/.cursor/commands/git-commit.md
# ~/projects/my-app/.windsurf/workflows/git-commit.md
# ~/projects/my-app/.claude/commands/git-commit.md
```

---

## Documentation

- **[Quickstart](docs/QUICKSTART.md)** — Installation and first steps
- **[Commands](docs/COMMANDS.md)** — Full command reference
- **[Validation](docs/VALIDATION.md)** — Validation rules and error codes

---

## Supported `asr adapter` IDEs

| IDE | Adapter | Output |
|-----|---------|--------|
| Cursor | `cursor` | `.cursor/commands/*.md` |
| Windsurf | `windsurf` | `.windsurf/workflows/*.md` |
| Codex | `codex` | `.codex/skills/*.md` |
| GitHub Copilot | `copilot` | `.github/prompts/*.prompt.md` |
| Claude Code | `claude` | `.claude/commands/*.md` |

---

## License

See [LICENSE](LICENSE).
