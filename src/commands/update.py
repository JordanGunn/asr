"""`oasr update` command - Update ASR tool from PyPI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from importlib import metadata

from output import Spinner, error, json_enabled, json_output, json_v2, require_confirmation, success, warn


def get_installed_version(package: str = "oasr") -> str | None:
    """Get installed package version."""
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None


def get_latest_pypi_version(package: str = "oasr") -> str | None:
    """Fetch the latest version from PyPI."""
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{package}/json", timeout=5) as response:
            data = json.load(response)
            return data.get("info", {}).get("version")
    except Exception:
        return None


def upgrade_from_pypi(package: str = "oasr") -> tuple[bool, str, str]:
    """Upgrade ASR using uv or pip."""
    commands = [
        ["uv", "pip", "install", "--upgrade", package],
        [sys.executable, "-m", "pip", "install", "--upgrade", package],
    ]
    last_error = ""

    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                runner = "uv" if cmd[0] == "uv" else "pip"
                return True, runner, ""
            last_error = result.stderr.strip() or result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            last_error = "Update timed out" if isinstance(sys.exc_info()[1], subprocess.TimeoutExpired) else last_error
            continue

    return False, "", last_error or "Failed to update with pip"


def register(subparsers) -> None:
    """Register the update command."""
    p = subparsers.add_parser(
        "update",
        help="Update ASR tool from PyPI",
    )
    p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress info messages",
    )
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Check for updates without upgrading",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Run the update command."""
    json_on = json_enabled(args.json)
    json_mode_v2 = json_v2(args.json)

    with Spinner("Checking PyPI for updates..."):
        latest_version = get_latest_pypi_version()
        installed_version = get_installed_version()
    update_available = bool(latest_version and installed_version and latest_version != installed_version)

    payload = {
        "installed_version": installed_version,
        "latest_version": latest_version,
        "update_available": update_available,
    }

    if not installed_version:
        if json_on:
            payload.update({"success": False, "error": "oasr is not installed via PyPI"})
            json_output(payload, command="update", v2=json_mode_v2)
        else:
            error("oasr is not installed via PyPI", hint="Install with: pip install oasr")
        return 1

    if not latest_version:
        if json_on:
            payload.update({"success": False, "error": "Unable to check PyPI for updates"})
            json_output(payload, command="update", v2=json_mode_v2)
        else:
            error("Unable to check PyPI for updates")
        return 1

    if args.check or not update_available:
        if json_on:
            payload.update({"success": True, "updated": False})
            json_output(payload, command="update", v2=json_mode_v2)
        else:
            if not update_available:
                if not args.quiet:
                    success(f"Already up to date (v{installed_version})")
            else:
                if not args.quiet:
                    print(f"Update available: {installed_version} → {latest_version}")
        return 0

    if json_on and not args.yes:
        payload.update({"success": False, "error": "Confirmation required. Re-run with --yes."})
        json_output(payload, command="update", v2=json_mode_v2)
        return 1

    if not require_confirmation(
        f"Update oasr {installed_version} → {latest_version}?",
        yes_flag=args.yes,
        default=False,
    ):
        if not json_on:
            warn("Aborted.")
        return 1

    success_flag, runner, error_msg = upgrade_from_pypi()

    if json_on:
        payload.update(
            {
                "success": success_flag,
                "updated": success_flag,
                "runner": runner if success_flag else None,
                "error": error_msg if not success_flag else None,
            }
        )
        json_output(payload, command="update", v2=json_mode_v2)
        return 0 if success_flag else 1

    if success_flag:
        if not args.quiet:
            success(f"Updated with {runner}")
        return 0

    error(f"Update failed: {error_msg}")
    return 1
