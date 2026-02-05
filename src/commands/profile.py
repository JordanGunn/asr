"""`oasr profile` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import questionary

from config import CONFIG_FILE, load_config, save_config
from output import error, info
from profiles import BUILTIN_PROFILES, format_profile_summary, sorted_profile_names


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "profile",
        help="List or set execution profiles",
        description="List and select execution policy profiles",
    )
    parser.add_argument("name", nargs="?", help="Profile name to set as default")
    parser.set_defaults(func=run)


def _print_profiles(profiles: dict[str, dict[str, object]], current: str) -> None:
    names = sorted_profile_names(profiles)
    print("Profiles:")
    for name in names:
        summary = format_profile_summary(name, profiles[name])
        suffix = []
        if name == current:
            suffix.append("current")
        if name in BUILTIN_PROFILES:
            suffix.append("built-in")
        suffix_text = f" ({', '.join(suffix)})" if suffix else ""
        print(f"  {summary}{suffix_text}")


def _select_profile(names: list[str], current: str) -> str | None:
    default_choice = current if current in names else (names[0] if names else None)
    if not default_choice:
        return None
    response = questionary.select(
        "Select a default profile:",
        choices=names,
        default=default_choice,
    ).ask()
    return response


def _set_default_profile(config_path: Path, profile_name: str) -> int:
    config = load_config(config_path=config_path)
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        error(f"Profile '{profile_name}' not found.", hint="Run 'oasr profile' to list available profiles")
        return 1

    config["oasr"]["default_profile"] = profile_name
    save_config(config, config_path=config_path)
    print(f"✓ Default profile set to: {profile_name}")
    return 0


def run(args: argparse.Namespace) -> int:
    config_path = CONFIG_FILE
    config = load_config(config_path=config_path)
    profiles = config.get("profiles", {})
    current = config.get("oasr", {}).get("default_profile", "safe")

    if args.name:
        return _set_default_profile(config_path, args.name)

    if not sys.stdout.isatty() or not sys.stdin.isatty():
        _print_profiles(profiles, current)
        info("\nTip: run `oasr profile <name>` to set the default profile.")
        return 0

    names = sorted_profile_names(profiles)
    choice = _select_profile(names, current)
    if not choice:
        error("No profiles available.")
        return 1

    return _set_default_profile(config_path, choice)
