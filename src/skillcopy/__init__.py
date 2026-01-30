"""Unified interface for copying skills (local or remote).

This module provides a single entry point for copying skills from any source
(local filesystem or remote URL) to a destination directory.
"""

from pathlib import Path

from .local import copy_local_skill
from .remote import copy_remote_skill, is_remote_source


def copy_skill(
    source: str,
    dest: Path,
    *,
    validate: bool = True,
    show_progress: bool = False,
    skill_name: str = None,
    inject_tracking: bool = False,
    source_hash: str | None = None,
) -> Path:
    """Copy a skill from source (path or URL) to destination.

    Args:
        source: Local path or remote URL
        dest: Destination directory
        validate: Whether to validate skill structure after copy
        show_progress: If True, show progress messages for remote skills
        skill_name: Optional skill name for progress messages
        inject_tracking: If True, inject metadata.oasr tracking info
        source_hash: Optional content hash for tracking (required if inject_tracking=True)

    Returns:
        Path to copied skill directory

    Raises:
        ValueError: If source is invalid or inject_tracking=True without source_hash
        OSError: If copy operation fails
    """
    if inject_tracking and source_hash is None:
        raise ValueError("source_hash required when inject_tracking=True")

    if is_remote_source(source):
        dest_path = copy_remote_skill(
            source, dest, validate=validate, show_progress=show_progress, skill_name=skill_name
        )
    else:
        dest_path = copy_local_skill(source, dest, validate=validate)

    # Inject tracking metadata if requested
    if inject_tracking:
        try:
            from tracking import inject_metadata

            success = inject_metadata(dest_path, source_hash, source)
            if not success:
                # Log warning but don't fail the copy
                import sys

                print(f"Warning: Failed to inject tracking metadata for {dest_path.name}", file=sys.stderr)
        except Exception as e:
            # Log warning but don't fail the copy
            import sys

            print(f"Warning: Error injecting tracking metadata: {e}", file=sys.stderr)

    return dest_path


__all__ = ["copy_skill", "is_remote_source"]
