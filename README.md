# OASR

**Open Agent Skill Registry** — Manage reusable AI agent skills across IDEs without drift.

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

```text
┌─────────────────────────────────────────────────────────┐
│           Your Skills (canonical source)                │
│           ~/skills/git-commit/SKILL.md                  │
│           ~/skills/code-review/SKILL.md                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
                   oasr adapter
                        │
        ┌───────────────┼──────────────┐...───────────────┐
        ▼               ▼              ▼                  ▼
   .cursor/        .windsurf/       .claude/           <vendor>/
   commands/       workflows/       commands/           skills/
```

No copying. No drift. One source of truth.

---

## Quick Example

![oasr list screenshot](docs/.images/list.png)
*List all registered skills with metadata*

```bash
# Register local skills
oasr add ~/skills/git-commit
oasr add ~/skills/code-review

# Register remote skills from GitHub/GitLab
oasr add https://github.com/user/skills-repo/tree/main/my-skill
oasr add https://gitlab.com/org/project/tree/main/cool-skill

# Generate adapters for a project
oasr adapter --output-dir ~/projects/my-app

# Result:
# ~/projects/my-app/.cursor/commands/git-commit.md
# ~/projects/my-app/.windsurf/workflows/git-commit.md
# ~/projects/my-app/.claude/commands/git-commit.md
```

---

## Remote Skills

![oasr add remote screenshot](docs/.images/add-remote.png)
*Register skills directly from GitHub or GitLab*

ASR supports registering skills directly from GitHub and GitLab repositories:

```bash
# Add a skill from GitHub
oasr add https://github.com/user/repo/tree/main/skills/my-skill

# Add a skill from GitLab
oasr add https://gitlab.com/org/project/tree/dev/cool-skill

# Sync remote skills (check for updates)
oasr sync

# Use remote skills
oasr use my-skill -d ./output
```

**Authentication** (optional, for private repos and higher rate limits):

```bash
export GITHUB_TOKEN=ghp_your_token_here
export GITLAB_TOKEN=glpat_your_token_here
```

Remote skills are fetched on-demand during `adapter` and `use` operations. The registry stores the URL, and `sync` checks if the remote source has changed.

---

## Documentation

- **[Quickstart](docs/QUICKSTART.md)** — Installation and first steps
- **[Commands](docs/commands/.INDEX.md)** — Full command reference
- **[Validation](docs/validation/.INDEX.md)** — Validation rules and error codes

---

## Supported `asr adapter` IDEs

| IDE            | Adapter    | Output                        |
|----------------|------------|-------------------------------|
| Cursor         | `cursor`   | `.cursor/commands/*.md`       |
| Windsurf       | `windsurf` | `.windsurf/workflows/*.md`    |
| Codex          | `codex`    | `.codex/skills/*.md`          |
| GitHub Copilot | `copilot`  | `.github/prompts/*.prompt.md` |
| Claude Code    | `claude`   | `.claude/commands/*.md`       |

---

## License

See [LICENSE](LICENSE).

## Screenshots

### Command Examples

| Command | Screenshot |
|---------|-----------|
| **oasr list** | ![list](docs/.images/list.png) |
| **oasr add** (local) | ![add](docs/.images/add.png) |
| **oasr add** (remote) | ![add-remote](docs/.images/add-remote.png) |
| **oasr sync** | ![sync](docs/.images/sync.png) |
| **oasr status** | ![status](docs/.images/status.png) |
| **oasr find** | ![find](docs/.images/find.png) |
| **oasr adapter** | ![adapter](docs/.images/adapter.png) |

See [docs/.images/](docs/.images/) for all screenshots.
