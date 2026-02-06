# `oasr profile`

List and manage execution policy profiles.

```bash
oasr profile                      # Interactive selector (TTY only)
oasr profile <name>               # Set default profile
oasr profile list                 # List profiles
oasr profile show [name]          # Show profile config
oasr profile edit                 # Edit active profile in $EDITOR
oasr profile edit -s              # Select a profile to edit
oasr profile edit -s dev          # Edit a specific profile
oasr profile new <name>           # Create new profile
oasr profile new <name> -c safe   # Copy from safe
oasr profile rm <name>            # Delete profile
oasr profile rm <name> -y         # Delete without confirmation
oasr profile wizard               # Create profile via prompts
```

**Non-interactive behavior:** prints profiles and exits with a hint.

**Notes:**
- `oasr profile show` uses the active profile when no name is provided.
- Built-in profiles (`safe`, `strict`, `dev`, `unsafe`) cannot be edited or deleted.

## Examples

```bash
# List interactively
oasr profile

# List explicitly
oasr profile list

# Show profile config
oasr profile show dev

# Show active profile
oasr profile show

# Create from template
oasr profile new my-project

# Copy from built-in and edit
oasr profile new my-dev -c dev

# Edit active profile
oasr profile edit

# Edit a specific profile
oasr profile edit dev

# Delete custom profile
oasr profile rm my-project

# Delete without confirmation
oasr profile rm my-project -y
```

## Related

- [Policy Profiles](../configuration/profiles.md)
- [Config command](CONFIG.md)
