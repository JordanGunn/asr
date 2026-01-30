#!/usr/bin/env bash
# Test script - run locally or in CI

set -e

echo "=== Running pytest ==="
pytest -v --cov=src --cov-report=term-missing "$@"

echo ""
echo "✓ All tests passed!"
