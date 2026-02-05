"""CLI entry point (argparse wiring + dispatch).

Command implementations live under `src/commands/`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from commands import about, adapter, clone, config, diff, exec, find, profile, registry, status, sync, update, validate
from commands import help as help_cmd
from output import (
    EXIT_FAILURE,
    EXIT_INTERRUPT,
    EXIT_UNEXPECTED,
    json_enabled,
    json_output,
    json_v2,
)
from output import (
    configure as configure_output,
)

__version__ = "1.0.0"

COMMAND_GROUPS = {
    "Registry Management": ["registry", "add", "rm", "list", "validate", "status"],
    "Skill Operations": ["clone", "sync", "diff", "exec"],
    "Configuration": ["config", "profile", "adapter"],
    "Maintenance": ["update", "completion", "about"],
    "Help": ["help"],
}


class GroupedHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _metavar_formatter(self, action, default_metavar):
        if action.dest == "command":
            return lambda *_: (default_metavar,)
        return super()._metavar_formatter(action, default_metavar)


def _build_command_help(subparsers: argparse._SubParsersAction) -> str:
    lines = []
    for group, commands in COMMAND_GROUPS.items():
        lines.append(f"\n{group}:")
        for cmd in commands:
            parser = subparsers.choices.get(cmd)
            if not parser:
                continue
            help_text = ""
            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    continue
                if action.dest == "help":
                    continue
                if action.help:
                    help_text = action.help
                    break
            help_text = help_text.splitlines()[0] if help_text else ""
            lines.append(f"  {cmd:12} {help_text}")
    lines.append("\nRun 'oasr help <command>' for detailed usage.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return EXIT_FAILURE

    use_color = not getattr(args, "no_color", False) and os.environ.get("NO_COLOR") is None
    if os.environ.get("OASR_NO_COLOR"):
        use_color = False
    use_unicode = not getattr(args, "no_unicode", False) and os.environ.get("OASR_NO_UNICODE") is None
    quiet = getattr(args, "quiet", False)
    configure_output(color=use_color, unicode=use_unicode, quiet=quiet)

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return EXIT_INTERRUPT
    except Exception as e:
        if json_enabled(getattr(args, "json", None)):
            if json_v2(getattr(args, "json", None)):
                json_output(
                    None,
                    command=getattr(args, "command", "unknown"),
                    success=False,
                    error_message=str(e),
                    error_hint=None,
                    v2=True,
                    file=sys.stderr,
                )
            else:
                print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return EXIT_UNEXPECTED


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="oasr",
        description="oasr — Open Agent Skill Registry\n\nManage agent skills across IDE integrations.",
        formatter_class=GroupedHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Override config file path",
    )
    parser.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format (v2 for new envelope format)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress info and warnings",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in output",
    )
    parser.add_argument(
        "--no-unicode",
        action="store_true",
        help="Disable unicode symbols in output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # New taxonomy (v0.3.0+)
    registry.register(subparsers)  # Registry operations (add, rm, sync, list)
    diff.register(subparsers)  # Show tracked skill status
    sync.register(subparsers)  # Refresh tracked skills
    config.register(subparsers)  # Configuration management
    profile.register(subparsers)  # Profile selection
    clone.register(subparsers)  # Clone skills to directory
    exec.register(subparsers)  # Execute skills with agent CLI
    status.register(subparsers)  # Show manifest status

    find.register(subparsers)
    validate.register(subparsers)
    adapter.register(subparsers)
    update.register(subparsers)
    about.register(subparsers)

    # Import and register info command
    from commands import info as info_cmd

    info_cmd.register(subparsers)

    # Import and register completion command
    from commands import completion as completion_cmd

    completion_cmd.register_parser(subparsers)

    help_cmd.register(subparsers, parser)

    parser.epilog = _build_command_help(subparsers)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
