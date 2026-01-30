# GitHub Actions Workflows

This directory contains CI/CD workflows for OASR.

## Workflows

### test.yml
Runs automated tests on multiple Python versions (3.10-3.13).
- Triggers: Push to master/main, PRs
- Matrix testing across Python versions
- Coverage reporting

### lint.yml  
Runs code quality checks with ruff.
- Triggers: Push to master/main, PRs
- Linting with ruff
- Format checking

## Local Testing

Run tests locally:
```bash
source ~/.local/share/asr/venv/bin/activate
pytest -v
```

Run linting:
```bash
pip install ruff
ruff check src/
ruff format --check src/
```
