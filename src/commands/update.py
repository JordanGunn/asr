"""`oasr update` command - Update ASR tool from GitHub."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from importlib import metadata
from pathlib import Path


def find_asr_repo() -> Path | None:
    """Find the ASR git repository path.

    Returns:
        Path to ASR repo, or None if not found.
    """
    # Try to find via current module location
    try:
        import cli

        cli_file = Path(cli.__file__).resolve()

        # Walk up to find .git directory
        current = cli_file.parent
        for _ in range(5):  # Max 5 levels up
            if (current / ".git").exists():
                return current
            if current.parent == current:  # Reached root
                break
            current = current.parent
    except Exception:
        pass

    return None


def get_git_remote_url(repo_path: Path) -> str | None:
    """Get the git remote URL.

    Args:
        repo_path: Path to git repository.

    Returns:
        Remote URL or None.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_current_commit(repo_path: Path) -> str | None:
    """Get current git commit hash.

    Args:
        repo_path: Path to git repository.

    Returns:
        Commit hash or None.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def check_working_tree_clean(repo_path: Path) -> bool:
    """Check if git working tree is clean.

    Args:
        repo_path: Path to git repository.

    Returns:
        True if clean, False if dirty.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and not result.stdout.strip()
    except Exception:
        return False


def pull_updates(repo_path: Path) -> tuple[bool, str]:
    """Pull updates from git remote.

    Args:
        repo_path: Path to git repository.

    Returns:
        Tuple of (success, message).
    """
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Check if already up to date
            if "Already up to date" in result.stdout or "Already up-to-date" in result.stdout:
                return True, "already_up_to_date"
            return True, "updated"
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Update timed out"
    except Exception as e:
        return False, str(e)


def get_changelog(repo_path: Path, old_commit: str, new_commit: str, max_lines: int = 10) -> list[str]:
    """Get changelog between two commits.

    Args:
        repo_path: Path to git repository.
        old_commit: Old commit hash.
        new_commit: New commit hash.
        max_lines: Maximum number of commits to show.

    Returns:
        List of commit messages.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"{old_commit}..{new_commit}", f"-{max_lines}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")
    except Exception:
        pass
    return []


def get_stats(repo_path: Path, old_commit: str, new_commit: str) -> dict:
    """Get statistics about changes.

    Args:
        repo_path: Path to git repository.
        old_commit: Old commit hash.
        new_commit: New commit hash.

    Returns:
        Dictionary with stats (commits, files, insertions, deletions).
    """
    stats = {"commits": 0, "files": 0, "insertions": 0, "deletions": 0}

    try:
        # Count commits
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{old_commit}..{new_commit}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            stats["commits"] = int(result.stdout.strip())

        # Get file stats
        result = subprocess.run(
            ["git", "diff", "--shortstat", old_commit, new_commit],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse: "5 files changed, 123 insertions(+), 45 deletions(-)"
            output = result.stdout.strip()
            if "file" in output:
                parts = output.split(",")
                for part in parts:
                    if "file" in part:
                        stats["files"] = int(part.split()[0])
                    elif "insertion" in part:
                        stats["insertions"] = int(part.split()[0])
                    elif "deletion" in part:
                        stats["deletions"] = int(part.split()[0])
    except Exception:
        pass

    return stats


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


def upgrade_from_pypi(package: str = "oasr") -> tuple[bool, str]:
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
                return True, f"Updated with {runner}"
            last_error = result.stderr.strip() or result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            last_error = "Update timed out" if isinstance(sys.exc_info()[1], subprocess.TimeoutExpired) else last_error
            continue

    return False, last_error or "Failed to update with pip"


def reinstall_asr(repo_path: Path) -> tuple[bool, str]:
    """Reinstall ASR using uv or pip.

    Args:
        repo_path: Path to ASR repository.

    Returns:
        Tuple of (success, message).
    """
    # Try uv first
    try:
        result = subprocess.run(
            ["uv", "pip", "install", "-e", "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, "Reinstalled with uv"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fall back to pip
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return True, "Reinstalled with pip"
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def register(subparsers) -> None:
    """Register the update command."""
    p = subparsers.add_parser(
        "update",
        help="Update ASR tool from GitHub",
    )
    p.add_argument(
        "--no-reinstall",
        action="store_true",
        help="Skip reinstallation step",
    )
    p.add_argument(
        "--changelog",
        type=int,
        default=10,
        metavar="N",
        help="Number of changelog entries to show (default: 10)",
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
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Run the update command."""
    # Find ASR repository
    repo_path = find_asr_repo()

    if not repo_path:
        if args.json:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": "Could not find ASR git repository",
                        "hint": "Install from git or use pip to update",
                    }
                )
            )
            return 1

        print("✗ Could not find ASR git repository", file=sys.stderr)
        print("  This command updates git installs only.", file=sys.stderr)
        print("  To update PyPI installs:", file=sys.stderr)
        print("    pip install --upgrade oasr", file=sys.stderr)

        latest_version = get_latest_pypi_version()
        installed_version = get_installed_version()
        if latest_version and installed_version and latest_version != installed_version:
            print(
                f"\nUpdate available: {installed_version} → {latest_version}",
                file=sys.stderr,
            )
        return 1

    if not args.quiet and not args.json:
        print(f"Found ASR repository: {repo_path}")

    # Check if it's a git repository
    if not (repo_path / ".git").exists():
        if args.json:
            print(json.dumps({"success": False, "error": "Not a git repository"}))
            return 1
        print(f"✗ {repo_path} is not a git repository", file=sys.stderr)
        print("  Use pip to update PyPI installs:", file=sys.stderr)
        print("    pip install --upgrade oasr", file=sys.stderr)
        return 1

    # Get remote URL
    remote_url = get_git_remote_url(repo_path)
    if remote_url and not args.quiet and not args.json:
        print(f"Remote: {remote_url}")

    # Check working tree
    if not check_working_tree_clean(repo_path):
        if args.json:
            print(json.dumps({"success": False, "error": "Working tree has uncommitted changes"}))
        else:
            print("✗ Working tree has uncommitted changes", file=sys.stderr)
            print("  Commit or stash your changes before updating", file=sys.stderr)
        return 1

    # Get current commit before update
    old_commit = get_current_commit(repo_path)
    if not old_commit:
        if args.json:
            print(json.dumps({"success": False, "error": "Could not get current commit"}))
        else:
            print("✗ Could not get current commit", file=sys.stderr)
        return 1

    # Pull updates
    if not args.quiet and not args.json:
        print("Pulling updates from GitHub...")

    success, message = pull_updates(repo_path)

    if not success:
        if args.json:
            print(json.dumps({"success": False, "error": f"Git pull failed: {message}"}))
        else:
            print(f"✗ Git pull failed: {message}", file=sys.stderr)
        return 1

    # Check if already up to date
    if message == "already_up_to_date":
        latest_version = get_latest_pypi_version()
        installed_version = get_installed_version()

        if args.json:
            payload = {"success": True, "updated": False, "message": "Already up to date"}
            if latest_version and installed_version:
                payload["installed_version"] = installed_version
                payload["latest_version"] = latest_version
                payload["pypi_update_available"] = latest_version != installed_version
            print(json.dumps(payload))
        else:
            print("✓ Already up to date")
            if latest_version and installed_version and latest_version != installed_version:
                print(
                    f"\nPyPI update available: {installed_version} → {latest_version}",
                    file=sys.stderr,
                )
                print("Run: pip install --upgrade oasr", file=sys.stderr)
        return 0

    # Get new commit
    new_commit = get_current_commit(repo_path)
    if not new_commit or new_commit == old_commit:
        if args.json:
            print(json.dumps({"success": True, "updated": False, "message": "No changes"}))
        else:
            print("✓ No changes")
        return 0

    # Get statistics
    stats = get_stats(repo_path, old_commit, new_commit)

    # Get changelog
    changelog = get_changelog(repo_path, old_commit, new_commit, max_lines=args.changelog)

    if args.json:
        print(
            json.dumps(
                {
                    "success": True,
                    "updated": True,
                    "old_commit": old_commit[:7],
                    "new_commit": new_commit[:7],
                    "stats": stats,
                    "changelog": changelog,
                },
                indent=2,
            )
        )
    else:
        print(f"✓ Updated ASR from {old_commit[:7]} to {new_commit[:7]}")
        print(f"  {stats['commits']} commit(s), {stats['files']} file(s) changed", end="")
        if stats["insertions"] > 0:
            print(f", +{stats['insertions']}", end="")
        if stats["deletions"] > 0:
            print(f", -{stats['deletions']}", end="")
        print()

        if changelog:
            print("\nRecent changes:")
            for line in changelog:
                print(f"  {line}")

    # Reinstall if requested
    if not args.no_reinstall:
        if not args.quiet and not args.json:
            print("\nReinstalling ASR...")

        success, message = reinstall_asr(repo_path)

        if success:
            if not args.quiet and not args.json:
                print(f"✓ {message}")
        else:
            if args.json:
                print(json.dumps({"warning": f"Reinstall failed: {message}"}), file=sys.stderr)
            else:
                print(f"⚠ Reinstall failed: {message}", file=sys.stderr)
                print("  You may need to reinstall manually", file=sys.stderr)

    return 0
