"""Unified interface for copying skills (local or remote).

This module provides a single entry point for copying skills from any source
(local filesystem or remote URL) to a destination directory.
"""

from pathlib import Path

from .local import copy_local_skill
from .remote import copy_remote_skill, is_remote_source


def copy_skill(source: str, dest: Path, *, validate: bool = True) -> Path:
    """Copy a skill from source (path or URL) to destination.
    
    Args:
        source: Local path or remote URL
        dest: Destination directory
        validate: Whether to validate skill structure after copy
    
    Returns:
        Path to copied skill directory
    
    Raises:
        ValueError: If source is invalid
        OSError: If copy operation fails
    """
    if is_remote_source(source):
        return copy_remote_skill(source, dest, validate=validate)
    else:
        return copy_local_skill(source, dest, validate=validate)


__all__ = ["copy_skill", "is_remote_source"]
