# GitHub Actions Workflows

This directory contains CI/CD workflows for the OASR project using a gitflow branching strategy.

## Workflows

### 1. `test.yml` - Continuous Integration
**Triggers:** Push/PR to `master`, `feat/**`, `hotfix/**`

**Purpose:** Fast feedback on code changes

**Jobs:**
- Runs test suite on Python 3.10, 3.11, 3.12, 3.13
- Generates coverage reports
- Uploads coverage to Codecov (optional)

### 2. `lint.yml` - Code Quality
**Triggers:** Push/PR to `master`, `feat/**`, `hotfix/**`

**Purpose:** Enforce code style and quality

**Jobs:**
- Runs ruff linting
- Checks code formatting
- Uses same scripts as local development

### 3. `release.yml` - Release Pipeline
**Triggers:** Push to `release/**` branches

**Purpose:** Validate release readiness before merging to master

**Jobs:**
1. Lint - Code quality checks
2. Test - Full test suite on all Python versions
3. Version Check - Ensures version was bumped and matches branch name
4. Build - Creates distribution packages
5. Validate Release - Checks CHANGELOG.md contains release notes

### 4. `publish.yml` - Publish Release
**Triggers:** Push of version tags (`v*`)

**Purpose:** Publish releases to PyPI and GitHub

**Jobs:**
1. Build - Creates distribution packages
2. Create Release - Creates GitHub release with changelog

## Gitflow Branching Strategy

### Branch Types

**Feature Branches (`feat/*`):**
- New features or enhancements
- Branch from: `master`
- Merge to: `master` (via PR)
- CI: Lint + Test
- Naming: `feat/feature-name`

**Hotfix Branches (`hotfix/*`):**
- Critical production fixes
- Branch from: `master`
- Merge to: `master` (via PR)
- CI: Lint + Test (fast)
- Naming: `hotfix/0.2.1-fix-name`

**Release Branches (`release/*`):**
- Prepare releases (version bump, changelog, docs)
- Branch from: `feat/*` or `master`
- Merge to: `master` (then tag)
- CI: Full pipeline (lint, test, build, validate)
- Naming: `release/X.Y.Z` (matches version)

## Version Management

**Single source of truth:**
- `src/cli.py` - `__version__` variable
- `pyproject.toml` - `version` field

Both must match and should be updated before creating a release branch.

## Local Development

Before pushing, run the same checks locally:

```bash
# Run linting
./scripts/lint.sh

# Auto-fix issues
./scripts/fix.sh

# Run tests
./scripts/test.sh
```
