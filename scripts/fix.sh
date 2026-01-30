#!/usr/bin/env bash
# Auto-fix linting issues

set -e

echo "=== Auto-fixing with ruff ==="
ruff check src/ --fix

echo ""
echo "=== Auto-formatting with ruff ==="
ruff format src/

echo ""
echo "✓ Auto-fix complete!"
echo ""
echo "Run './scripts/lint.sh' to verify all issues are fixed."
