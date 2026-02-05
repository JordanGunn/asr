"""`oasr about` command."""

from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("about", help="Show version and credits")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    from cli import __version__

    print(
        f"""oasr v{__version__}
Open Agent Skill Registry

A CLI tool for managing AI agent skills across IDEs.
https://github.com/JordanGunn/oasr

Licensed under MIT."""
    )
    return 0
