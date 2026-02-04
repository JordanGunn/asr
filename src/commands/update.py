"""`oasr update` command - Update ASR tool from PyPI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from importlib import metadata


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
        action="store_true",
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
    latest_version = get_latest_pypi_version()
    installed_version = get_installed_version()
    update_available = bool(latest_version and installed_version and latest_version != installed_version)

    if args.json:
        payload = {
            "installed_version": installed_version,
            "latest_version": latest_version,
            "update_available": update_available,
        }
        if not installed_version:
            payload.update({"success": False, "error": "oasr is not installed via PyPI"})
            print(json.dumps(payload, indent=2))
            return 1
        if not latest_version:
            payload.update({"success": False, "error": "Unable to check PyPI for updates"})
            print(json.dumps(payload, indent=2))
            return 1
        if args.check or not update_available:
            payload.update({"success": True, "updated": False})
            print(json.dumps(payload, indent=2))
            return 0
        if not args.yes:
            payload.update({"success": False, "error": "Confirmation required. Re-run with --yes."})
            print(json.dumps(payload, indent=2))
            return 1
    else:
        if not installed_version:
            print("✗ oasr is not installed via PyPI", file=sys.stderr)
            print("  Install with: pip install oasr", file=sys.stderr)
            return 1

        if not latest_version:
            print("✗ Unable to check PyPI for updates", file=sys.stderr)
            return 1

        if not update_available:
            if not args.quiet:
                print(f"✓ Already up to date (v{installed_version})")
            return 0

        if args.check:
            if not args.quiet:
                print(f"Update available: {installed_version} → {latest_version}")
            return 0

        if not args.yes:
            try:
                response = input(f"Update oasr {installed_version} → {latest_version}? [y/N] ").strip().lower()
                if response not in ("y", "yes"):
                    print("Aborted.")
                    return 1
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                return 1

    success, runner, error = upgrade_from_pypi()

    if args.json:
        payload.update(
            {
                "success": success,
                "updated": success,
                "runner": runner if success else None,
                "error": error if not success else None,
            }
        )
        print(json.dumps(payload, indent=2))
        return 0 if success else 1

    if success:
        if not args.quiet:
            print(f"✓ Updated with {runner}")
        return 0

    print(f"✗ Update failed: {error}", file=sys.stderr)
    return 1
