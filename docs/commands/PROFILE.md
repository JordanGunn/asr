# `oasr profile`

List and select execution policy profiles.

```bash
oasr profile              # Interactive selector (TTY only)
oasr profile <name>       # Set default profile
```

**Non-interactive behavior:** prints profiles and exits with a hint.

## Examples

```bash
# List and select interactively
oasr profile

# Set default profile
oasr profile dev
```

## Related

- [Policy Profiles](../configuration/profiles.md)
- [Config command](CONFIG.md)
