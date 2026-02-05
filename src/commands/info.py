"""Info command - show detailed information about a skill."""

import argparse
from datetime import datetime

from manifest import check_manifest, load_manifest
from output import Spinner, error, json_enabled, json_output, json_v2
from registry import load_registry
from skillcopy.remote import is_remote_source


def run(args: argparse.Namespace) -> int:
    """Show detailed information about a skill.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    skill_name = args.skill_name

    # Load registry to verify skill exists
    entries = load_registry()
    entry = None
    for e in entries:
        if e.name == skill_name:
            entry = e
            break

    if not entry:
        error(f"Skill '{skill_name}' not found", hint="Try: oasr list")
        return 1

    # Load manifest
    manifest = load_manifest(skill_name)
    if not manifest:
        error(f"No manifest found for: {skill_name}", hint="Run 'oasr registry' to rebuild manifests")
        return 1

    # Check if remote and show progress indicator
    is_remote = is_remote_source(manifest.source_path)
    if is_remote and not args.quiet and not json_enabled(args.json):
        platform = (
            "GitHub"
            if "github.com" in manifest.source_path
            else "GitLab"
            if "gitlab.com" in manifest.source_path
            else "remote"
        )
        with Spinner(f"Checking remote skill status from {platform}..."):
            status_result = check_manifest(manifest)
    else:
        status_result = check_manifest(manifest)

    # Determine type
    is_remote = is_remote_source(manifest.source_path)
    if is_remote:
        if "github.com" in manifest.source_path:
            skill_type = "Remote (GitHub)"
        elif "gitlab.com" in manifest.source_path:
            skill_type = "Remote (GitLab)"
        else:
            skill_type = "Remote"
    else:
        skill_type = "Local"

    # Format registered date
    try:
        reg_date = datetime.fromisoformat(manifest.registered_at.replace("Z", "+00:00"))
        reg_date_str = reg_date.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        reg_date_str = manifest.registered_at

    # Prepare data
    info = {
        "name": manifest.name,
        "description": manifest.description,
        "source": manifest.source_path,
        "type": skill_type,
        "status": status_result.status,
        "file_count": len(manifest.files),
        "content_hash": manifest.content_hash,
        "registered_at": reg_date_str,
    }

    if args.files:
        info["files"] = [{"path": f.path, "hash": f.hash} for f in manifest.files]

    # Output
    if json_enabled(args.json):
        payload = info if not json_v2(args.json) else {"skill": info}
        json_output(payload, command="info", v2=json_v2(args.json))
    else:
        # Human-readable format
        status_icon = {
            "valid": "✓",
            "modified": "↻",
            "missing": "✗",
        }.get(status_result.status, "?")

        print(f"\n[{manifest.name}]")
        print("---")
        print(manifest.description)
        print("---")
        print(f"Source: {manifest.source_path}")
        print(f"Type: {skill_type}")
        print(f"Status: {status_icon} {status_result.status.capitalize()}")
        if status_result.message:
            print(f"  {status_result.message}")
        print(f"Files: {len(manifest.files)}")
        print(f"Hash: {manifest.content_hash[:20]}...")
        print(f"Registered: {reg_date_str}")

        if args.files and manifest.files:
            print(f"\nFiles ({len(manifest.files)}):")
            for file_info in manifest.files:
                print(f"  - {file_info.path}")

        print()

    return 0


def register(subparsers):
    """Register the info command with argparse.

    Args:
        subparsers: Subparsers object from argparse
    """
    parser = subparsers.add_parser(
        "info",
        help="Show detailed information about a skill",
        description="Display detailed information about a registered skill including "
        "metadata, status, and optionally the list of files.",
    )

    parser.add_argument(
        "skill_name",
        help="Skill name to show information for",
    )
    parser.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )

    parser.add_argument(
        "--files",
        action="store_true",
        help="Show list of files in the skill",
    )

    parser.set_defaults(func=run)
