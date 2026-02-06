"""`oasr profile` command."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import questionary

import output as output_mod
from config import CONFIG_FILE, load_config, save_config
from output import error, require_confirmation
from profiles import (
    BUILTIN_DESCRIPTIONS,
    BUILTIN_PROFILES,
    delete_profile,
    format_profile_summary,
    get_profile_path,
    is_builtin_profile,
    normalize_profile_name,
    render_profile_template,
    save_profile,
    sorted_profile_names,
    validate_profile_data,
)


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "profile",
        help="List or set execution profiles",
        description=(
            "Manage execution policy profiles.\n\n"
            "Usage:\n"
            "  oasr profile                # Interactive selector\n"
            "  oasr profile <name>         # Set default profile\n"
            "  oasr profile list           # List profiles\n"
            "  oasr profile show [name]    # Show profile config\n"
            "  oasr profile edit [name]    # Edit profile\n"
            "  oasr profile edit -s        # Select profile to edit\n"
            "  oasr profile new <name>     # Create profile\n"
            "  oasr profile new <name> -c <source>\n"
            "  oasr profile rm <name>      # Delete profile\n"
            "  oasr profile wizard         # Guided creation\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Subcommand or profile name",
    )
    parser.set_defaults(func=run)


def _get_config_path(args: argparse.Namespace) -> Path:
    return getattr(args, "config", None) or CONFIG_FILE


def _load_profiles(config_path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    config = load_config(config_path=config_path)
    profiles = config.get("profiles", {})
    current = config.get("oasr", {}).get("default_profile", "safe")
    return profiles, current


def _print_profiles(profiles: dict[str, dict[str, Any]], current: str) -> None:
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


def _build_profile_choices(profiles: dict[str, dict[str, Any]], names: list[str]) -> list[questionary.Choice]:
    choices: list[questionary.Choice] = []
    for name in names:
        profile = profiles.get(name, {})
        summary = format_profile_summary(name, profile)
        builtin_desc = BUILTIN_DESCRIPTIONS.get(name)
        description = builtin_desc or summary
        choices.append(questionary.Choice(title=name, value=name, description=description))
    return choices


def _select_profile(
    profiles: dict[str, dict[str, Any]],
    names: list[str],
    current: str,
    *,
    prompt: str,
) -> str | None:
    default_choice = current if current in names else (names[0] if names else None)
    if not default_choice:
        return None
    choices = _build_profile_choices(profiles, names)
    response = questionary.select(
        prompt,
        choices=choices,
        default=default_choice,
    ).ask()
    return response


def _set_default_profile(config_path: Path, profile_name: str) -> int:
    config = load_config(config_path=config_path)
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        error(f"Profile '{profile_name}' not found.", hint="Run 'oasr profile list' to list available profiles")
        return 1

    config["oasr"]["default_profile"] = profile_name
    save_config(config, config_path=config_path)
    print(f"✓ Default profile set to: {profile_name}")
    return 0


def _write_profile_template(path: Path, template: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template, encoding="utf-8")


def _open_editor(path: Path, config_path: Path | None = None) -> int:
    # Priority: config > $EDITOR > $VISUAL > system default
    editor = None
    if config_path:
        config = load_config(config_path=config_path)
        editor = config.get("oasr", {}).get("editor")
    if not editor:
        editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        editor = "notepad" if os.name == "nt" else "vi"
    cmd = shlex.split(editor) + [str(path)]
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError:
        error(f"Editor not found: {editor}", hint="Set $EDITOR, $VISUAL, or `oasr config set oasr.editor <editor>`")
        return 1
    return result.returncode


def _non_interactive_hint(message: str) -> None:
    output_mod.info(message, file=sys.stdout)


def _load_profile_file(path: Path) -> dict[str, Any] | None:
    try:
        import tomllib
    except ImportError:  # pragma: no cover - py311 default
        import tomli as tomllib  # type: ignore[no-redef]

    if not path.exists():
        error(f"Profile file not found: {path}")
        return None
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception as exc:
        error(f"Failed to parse profile file: {path}", hint=str(exc))
        return None
    if not isinstance(data, dict):
        error(f"Profile file {path} must contain a TOML table")
        return None
    return data


def _resolve_profile_name(args: argparse.Namespace, profiles: dict[str, dict[str, Any]], current: str) -> str | None:
    if args.select == "__select__":
        names = sorted_profile_names(profiles)
        return _select_profile(profiles, names, current, prompt="Select a profile to edit:")
    if args.select:
        return args.select
    return current


def _parse_command_list(value: str) -> list[str]:
    if not value.strip():
        return []
    lowered = value.strip().lower()
    if lowered in {"*", "all"}:
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


def run(args: argparse.Namespace) -> int:
    config_path = _get_config_path(args)
    profiles, current = _load_profiles(config_path)
    parsed = _parse_args(args.args or [])
    if parsed["error"]:
        return 1

    if parsed["wizard"]:
        return _run_wizard(config_path, profiles)

    if parsed["list"]:
        _print_profiles(profiles, current)
        return 0

    if parsed["show"] is not None:
        return _run_show(config_path, profiles, current, parsed["show"])

    if parsed["rm"] is not None:
        if not parsed["rm"]:
            return 1
        return _run_rm(config_path, profiles, current, parsed["rm"], parsed["yes"])

    if parsed["new"]:
        return _run_new(config_path, profiles, parsed["new"], parsed["copy_from"])

    if parsed["edit"]:
        if not sys.stdout.isatty() or not sys.stdin.isatty():
            error("Profile edit requires an interactive terminal.")
            return 1
        return _run_edit(config_path, profiles, current, parsed["select"])

    if parsed["name"]:
        return _set_default_profile(config_path, parsed["name"])

    if not sys.stdout.isatty() or not sys.stdin.isatty():
        _print_profiles(profiles, current)
        _non_interactive_hint("\nTip: run `oasr profile <name>` to set the default profile.")
        return 0

    names = sorted_profile_names(profiles)
    choice = _select_profile(profiles, names, current, prompt="Select a default profile:")
    if not choice:
        error("No profiles available.")
        return 1

    return _set_default_profile(config_path, choice)


def _parse_args(argv: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {
        "name": None,
        "list": False,
        "show": None,
        "edit": False,
        "select": None,
        "new": None,
        "copy_from": None,
        "rm": None,
        "wizard": False,
        "yes": False,
        "error": False,
    }
    if not argv:
        return parsed
    first = argv[0]

    if first in {"list", "show", "edit", "rm", "new", "wizard"}:
        sub = first
        rest = argv[1:]
        if sub == "list":
            if rest:
                error("Unexpected arguments for list.")
                parsed["error"] = True
            parsed["list"] = True
            return parsed
        if sub == "wizard":
            if rest:
                error("Unexpected arguments for wizard.")
                parsed["error"] = True
            parsed["wizard"] = True
            return parsed
        if sub == "show":
            if len(rest) > 1:
                error("Too many arguments for show.")
                parsed["error"] = True
            if rest and rest[0].startswith("-"):
                error("Unexpected flag for show.")
                parsed["error"] = True
            parsed["show"] = rest[0] if rest else "__active__"
            return parsed
        if sub == "rm":
            name = None
            extra = []
            for token in rest:
                if token in {"-y", "--yes"}:
                    parsed["yes"] = True
                    continue
                if token.startswith("-"):
                    error(f"Unknown flag for rm: {token}")
                    parsed["error"] = True
                    continue
                if name is None:
                    name = token
                else:
                    extra.append(token)
            parsed["rm"] = name or ""
            if not name:
                error("Profile name is required for rm.")
                parsed["error"] = True
            if extra:
                error("Too many arguments for rm.")
                parsed["error"] = True
            return parsed
        if sub == "new":
            name = None
            i = 0
            extra = []
            while i < len(rest):
                token = rest[i]
                if token in {"-c", "--copy-from"}:
                    if i + 1 >= len(rest):
                        error("Copy source required for --copy-from.")
                        parsed["error"] = True
                        break
                    parsed["copy_from"] = rest[i + 1]
                    i += 2
                    continue
                if token.startswith("-"):
                    error(f"Unknown flag for new: {token}")
                    parsed["error"] = True
                    i += 1
                    continue
                if name is None:
                    name = token
                else:
                    extra.append(token)
                i += 1
            parsed["new"] = name or ""
            if not name:
                error("Profile name is required for new.")
                parsed["error"] = True
            if extra:
                error("Too many arguments for new.")
                parsed["error"] = True
            return parsed
        if sub == "edit":
            parsed["edit"] = True
            if "-s" in rest:
                idx = rest.index("-s")
                parsed["select"] = rest[idx + 1] if idx + 1 < len(rest) else "__select__"
                rest = rest[:idx] + rest[idx + 2 :]
            elif "--select" in rest:
                idx = rest.index("--select")
                parsed["select"] = rest[idx + 1] if idx + 1 < len(rest) else "__select__"
                rest = rest[:idx] + rest[idx + 2 :]
            else:
                for token in list(rest):
                    if token.startswith("-"):
                        error(f"Unknown flag for edit: {token}")
                        parsed["error"] = True
                        rest.remove(token)
                if rest:
                    parsed["select"] = rest[0]
                    rest = rest[1:]
            if rest:
                error("Unexpected arguments for edit.")
                parsed["error"] = True
            return parsed

    if len(argv) > 1:
        error("Too many arguments. Use `oasr profile --help` for usage.")
        parsed["error"] = True
        return parsed

    if first.startswith("-"):
        error(f"Unknown option: {first}")
        parsed["error"] = True
        return parsed

    parsed["name"] = first
    return parsed


def _run_show(
    config_path: Path,
    profiles: dict[str, dict[str, Any]],
    current: str,
    name: str | None,
) -> int:
    profile_name = current if name == "__active__" or not name else name
    profile = profiles.get(profile_name)
    if not profile:
        error(f"Profile '{profile_name}' not found.", hint="Run 'oasr profile --list' to see available profiles")
        return 1
    print(f"# Profile: {profile_name}")
    print(render_profile_template(profile))
    return 0


def _run_edit(
    config_path: Path,
    profiles: dict[str, dict[str, Any]],
    current: str,
    select: str | None,
) -> int:
    args = argparse.Namespace(select=select)
    name = _resolve_profile_name(args, profiles, current)
    if not name:
        error("No profiles available.")
        return 1
    if is_builtin_profile(name):
        error(
            f"Cannot edit built-in profile '{name}'.",
            hint=f"Copy it first with `oasr profile --new {name}-custom -c {name}`",
        )
        return 1
    path = get_profile_path(name)
    if not path.exists():
        error(f"Profile '{name}' not found.", hint="Run 'oasr profile --list' to see available profiles")
        return 1

    result = _open_editor(path, config_path)
    if result != 0:
        return result

    data = _load_profile_file(path)
    if data is None:
        return 1
    try:
        validate_profile_data(name, data)
    except ValueError as exc:
        error(str(exc))
        return 1
    print(f"✓ Profile updated: {path}")
    return 0


def _run_rm(
    config_path: Path,
    profiles: dict[str, dict[str, Any]],
    current: str,
    name: str,
    yes_flag: bool,
) -> int:
    if name not in profiles:
        error(f"Profile '{name}' not found.", hint="Run 'oasr profile --list' to see available profiles")
        return 1
    if is_builtin_profile(name):
        error(
            f"Cannot delete built-in profile '{name}'.",
            hint=f"Copy it first with `oasr profile --new {name}-custom -c {name}`",
        )
        return 1
    if not require_confirmation(f"Delete profile '{name}'?", yes_flag=yes_flag, default=False):
        return 1
    if not delete_profile(name):
        error(f"Profile file for '{name}' was not found.")
        return 1
    if current == name:
        config = load_config(config_path=config_path)
        config["oasr"]["default_profile"] = "safe"
        save_config(config, config_path=config_path)
        _non_interactive_hint("Default profile reset to 'safe'.")
    print(f"✓ Profile deleted: {name}")
    return 0


def _run_new(
    config_path: Path,
    profiles: dict[str, dict[str, Any]],
    name: str,
    copy_from: str | None,
) -> int:
    normalized = normalize_profile_name(name)
    if normalized != name:
        _non_interactive_hint(f"Normalized to: {normalized}")
    if normalized in profiles:
        error(f"Profile '{normalized}' already exists.")
        return 1

    base_profile: dict[str, Any] = {}
    if copy_from:
        if copy_from not in profiles:
            error(f"Profile '{copy_from}' not found.", hint="Run 'oasr profile --list' to see available profiles")
            return 1
        base_profile = profiles[copy_from]

    if not sys.stdout.isatty() or not sys.stdin.isatty():
        error("Profile creation requires an interactive terminal.")
        return 1

    template = render_profile_template(base_profile)
    with tempfile.TemporaryDirectory(prefix="oasr-profile-") as temp_dir:
        temp_path = Path(temp_dir) / f"{normalized}.toml"
        _write_profile_template(temp_path, template)

        if _open_editor(temp_path, config_path) != 0:
            return 1

        data = _load_profile_file(temp_path)
    if data is None:
        return 1
    try:
        validate_profile_data(normalized, data)
    except ValueError as exc:
        error(str(exc))
        return 1

    path = save_profile(normalized, data)
    print(f"✓ Profile saved: {path}")
    return 0


def _run_wizard(config_path: Path, profiles: dict[str, dict[str, Any]]) -> int:
    if not sys.stdout.isatty() or not sys.stdin.isatty():
        error("Profile wizard requires an interactive terminal.")
        return 1
    name_raw = questionary.text("Profile name:").ask()
    if not name_raw:
        error("Profile name is required.")
        return 1
    name = normalize_profile_name(name_raw)
    if name != name_raw:
        _non_interactive_hint(f"Normalized to: {name}")
    if name in profiles:
        error(f"Profile '{name}' already exists.")
        return 1

    network_choice = questionary.select(
        "Network access?",
        choices=["Disabled", "Enabled"],
        default="Disabled",
    ).ask()
    shell_choice = questionary.select(
        "Shell access?",
        choices=["Denied", "Allowed"],
        default="Denied",
    ).ask()
    commands = questionary.text("Allowed commands (comma-separated, or 'all'):", default="rg, fd, jq, cat").ask()
    cwd = str(Path.cwd())
    read_roots = questionary.text("Readable directories (comma-separated):", default=cwd).ask()
    write_roots = questionary.text("Writable directories (comma-separated):", default="./out, ./.oasr").ask()
    deny_paths = questionary.text(
        "Denied paths (glob patterns, comma-separated):",
        default="~/.ssh, ~/.aws, **/.env, **/secrets/**",
    ).ask()
    allow_env = questionary.confirm("Expose environment variables?", default=False).ask()
    set_default = questionary.confirm("Set as default profile?", default=False).ask()

    profile_data = {
        "fs_read_roots": _parse_command_list(read_roots),
        "fs_write_roots": _parse_command_list(write_roots),
        "deny_paths": _parse_command_list(deny_paths),
        "allowed_commands": _parse_command_list(commands),
        "deny_shell": shell_choice == "Denied",
        "network": network_choice == "Enabled",
        "allow_env": bool(allow_env),
    }
    try:
        validate_profile_data(name, profile_data)
    except ValueError as exc:
        error(str(exc))
        return 1

    path = save_profile(name, profile_data)
    print(f"✓ Profile saved: {path}")

    if set_default:
        config = load_config(config_path=config_path)
        config["oasr"]["default_profile"] = name
        save_config(config, config_path=config_path)
        print("✓ Set as default profile")
    return 0
