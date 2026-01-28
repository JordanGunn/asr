# Contributing

Thanks for taking the time to contribute!

## Quick Start (local dev)

This project uses `uv` + `hatch`:

```bash
cd oasr
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Running tests

```bash
cd oasr
hatch run dev:test
```

## What to include in a PR

- A clear description of the problem and the approach.
- Updates to docs (`README.md`, `CHANGELOG.md`) when behavior or UX changes.
- If you change CLI behavior, include a minimal reproduction / example invocation in the PR description.

## Code style

- Keep changes focused and avoid drive-by refactors.
- Prefer small, composable functions with clear names.
- Keep `src/cli.py` focused on argparse wiring; command logic should live under `src/commands/`.

## License / attribution

By contributing, you agree that your contributions will be licensed under the
project’s license (see `LICENSE`) and that redistributions should retain
attribution notices (see `NOTICE`).

