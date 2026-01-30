# Development Scripts

This directory contains scripts for development tasks that run both locally and in CI.

## Scripts

### `lint.sh`
Run linting checks (ruff):
```bash
./scripts/lint.sh
```

Runs:
- `ruff check src/` - Code quality checks
- `ruff format --check src/` - Formatting checks

### `fix.sh`
Auto-fix linting issues:
```bash
./scripts/fix.sh
```

Runs:
- `ruff check src/ --fix` - Auto-fix code issues
- `ruff format src/` - Auto-format code

### `test.sh`
Run test suite:
```bash
./scripts/test.sh
```

Runs:
- `pytest -v --cov=src --cov-report=term-missing`

## Usage in CI

These scripts are used by GitHub Actions workflows:
- `.github/workflows/lint.yml` → `./scripts/lint.sh`
- `.github/workflows/test.yml` → `./scripts/test.sh`

This ensures consistency between local development and CI.

## Quick Start

```bash
# Install dev dependencies
source ~/.local/share/asr/venv/bin/activate
pip install pytest pytest-cov ruff

# Fix all auto-fixable issues
./scripts/fix.sh

# Verify everything passes
./scripts/lint.sh

# Run tests
./scripts/test.sh
```

## Pre-commit (Optional)

To run linting before every commit:
```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/lint.sh
EOF

chmod +x .git/hooks/pre-commit
```
