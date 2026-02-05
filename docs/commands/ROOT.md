# Global Flags

| Flag              | Description                    |
|-------------------|--------------------------------|
| `--config <path>` | Override config file location  |
| `--json`          | Output in JSON format          |
| `--quiet`         | Suppress info/warnings         |
| `--no-color`      | Disable ANSI colors            |
| `--no-unicode`    | Disable unicode symbols        |
| `--version`       | Show version                   |

## JSON Output Versions

`--json` outputs legacy JSON for backward compatibility. Use `--json v2` for the new
envelope format with `version`, `success`, `command`, and `error` metadata.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Operation failed |
| 2 | Invalid input / usage error |
| 3 | Unexpected error |
| 130 | Interrupted (Ctrl+C) |
