#!/usr/bin/env bash
# Linting script - run locally or in CI

set -e

echo "=== Running ruff linter ==="
ruff check src/ "$@"

echo ""
echo "=== Running ruff formatter check ==="
ruff format --check src/ "$@"

echo ""
echo "✓ All checks passed!"
