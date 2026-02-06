# Roadmap

## v1.1.0 — Profiles First-Class

**Theme:** Make profiles the centerpiece for security, project isolation, and user guidance.

### Why Profiles Matter

Profiles are the primary defense against:
- **Prompt injection** — restrict what commands a skill can request
- **Accidental damage** — block destructive operations by default
- **Credential exposure** — deny access to sensitive paths (`~/.ssh`, `~/.aws`)

They also enable:
- **Project isolation** — different rules for work vs personal projects
- **Team sharing** — commit `.oasr/profiles/project.toml` to a repo
- **Progressive trust** — start with `strict`, graduate to `dev` as confidence grows

### Profile Command Enhancements

| Command | Description |
|---------|-------------|
| `oasr profile` | Interactive selector with descriptions (enhanced) |
| `oasr profile <name>` | Set active profile (existing) |
| `oasr profile list` | List profiles with summaries |
| `oasr profile show [name]` | Display profile config (active if omitted) |
| `oasr profile edit [-s name]` | **New:** Edit profile in `$EDITOR` |
| `oasr profile wizard` | **New:** Interactive step-by-step creation |
| `oasr profile new <name>` | **New:** Open editor with commented template |
| `oasr profile new <name> -c <source>` | **New:** Copy from existing profile |
| `oasr profile rm <name>` | **New:** Delete profile (with confirmation) |

### Wizard Flow

```
$ oasr profile wizard

🧙 Profile Wizard

Profile name: My Project
  → Normalized to: my-project

Network access?
  ❯ Disabled (no outbound requests)
    Enabled (allow HTTP/HTTPS)

Shell access?
  ❯ Denied (command whitelist only)
    Allowed (full shell access)

Allowed commands (comma-separated, or 'all'):
  > bash, python, git, npm

Readable directories (recursive, comma-separated):
  > ./, ~/projects

Writable directories (recursive, comma-separated):
  > ./out, ./.oasr

Denied paths (glob patterns, comma-separated):
  > ~/.ssh, ~/.aws, **/.env, **/secrets/**

Expose environment variables? [y/N]: n

Set as default profile? [y/N]: y

✓ Profile saved: ~/.oasr/profiles/my-project.toml
✓ Set as default profile
```

### Interactive Selector Enhancement

When using `oasr profile` (no args), show description below each highlighted item:

```
? Select a default profile:
  ❯ safe
    strict
    dev
    unsafe

  ┌─────────────────────────────────────────────────────┐
  │ safe (built-in)                                     │
  │ Read: ./  Write: ./out  Network: ✗  Shell: ✗       │
  │ Commands: rg, fd, jq, cat                           │
  └─────────────────────────────────────────────────────┘
```

### Config vs Profile Separation

**Config** (`~/.oasr/config.toml`) — global defaults:
- `agent` — default agent for `oasr exec`
- `oasr.default_profile` — which profile loads by default
- `oasr.completions` — shell completion behavior
- `validation.strict` — strict validation mode

**Profiles** (`~/.oasr/profiles/*.toml`) — execution policies:
- `fs_read_roots` / `fs_write_roots` — filesystem access (recursive)
- `deny_paths` — blocked paths with glob support (`~/.ssh`, `**/.env`)
- `respect_gitignore` — auto-deny paths in `.gitignore` (convenience)
- `allowed_commands` — whitelist of commands
- `deny_shell` — block shell access
- `network` — allow network requests (enabled/disabled)
- `allow_env` — expose environment variables
- `adapter.*` — **migrate from config** (project-specific)

### Built-in Profile Protection

Built-in profiles (`safe`, `strict`, `dev`, `unsafe`) cannot be deleted. They serve as reference implementations and starting points for custom profiles.

```
$ oasr profile rm safe
✗ Cannot delete built-in profile 'safe'
  Hint: Copy it first with `oasr profile new my-safe -c safe`, then customize.
```

### Documentation Updates

- **Profiles guide** — comprehensive explanation of each setting
- **Security guide** — prompt injection defense, least-privilege principles
- **Migration guide** — moving adapter settings from config to profiles

---

## v1.2.0 — Stability & QoL (Tentative)

- `oasr doctor` — diagnose common issues
- Dry-run mode for destructive commands
- Improved error messages with actionable hints
- Windows path handling audit
- Increased test coverage for edge cases

---

## Future Considerations

- `oasr registry export/import` — backup/restore
- Glob support in more commands (`oasr info "git-*"`)
- Remote profile sharing (fetch from URL)
- Profile inheritance (extend from another profile)
