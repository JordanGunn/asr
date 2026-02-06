# Security Guide

OASR profiles are the primary defense against prompt injection, unsafe agent behavior, and accidental data loss. The goal is least privilege: give the agent only what it needs for the task.

---

## Core Principles

1. **Start restrictive** – begin with `safe`, open up only what is required.
2. **Prefer allowlists** – use `allowed_commands` instead of broad shell access.
3. **Protect secrets** – always keep sensitive paths in `deny_paths`.
4. **Assume instructions may be hostile** – profiles enforce boundaries even if the prompt is compromised.

---

## Recommended Defaults

These settings provide a safe baseline:

```toml
fs_read_roots = ["./"]
fs_write_roots = ["./out", "./.oasr"]
deny_paths = ["~/.ssh", "~/.aws", "~/.gnupg", "~/.config", ".env"]
allowed_commands = ["rg", "fd", "jq", "cat"]
deny_shell = true
network = false
allow_env = false
```

---

## Common Risk Areas

### 1. Network Access
Enabling `network` allows outbound HTTP/HTTPS requests. Use only when required.

### 2. Shell Access
Setting `deny_shell = false` allows arbitrary shell execution. Use with strict `allowed_commands`.

### 3. Environment Variables
Setting `allow_env = true` exposes all environment variables (including secrets). Avoid unless strictly needed.

### 4. File Access
- Keep `fs_read_roots` narrow
- Prefer dedicated write directories
- Use `deny_paths` even inside allowed roots

---

## Prompt Injection Defense

Profiles mitigate prompt injection by **enforcing at the host level** what a skill can do. Even if a skill instructs an agent to run unsafe commands or read secrets, the profile blocks the action.

---

## Best Practices

- Create project-specific profiles (`profiles.my-project`)
- Review policy summary before confirming execution
- Avoid `unsafe` unless in a fully isolated environment
- Use `--yes` sparingly

---

## Related

- [Policy Profiles](profiles.md)
- [Execution Command](../commands/EXEC.md)
