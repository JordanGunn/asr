# Validation Rules

ASR validates skill directories to catch structural issues, missing metadata, and potential problems before they cause silent failures.

Run validation with:

```bash
oasr validate /path/to/skill       # Single skill
oasr validate --all                # All registered skills
oasr validate --all --strict       # Treat warnings as errors
```
