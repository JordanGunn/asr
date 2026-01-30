"""Remote skill fetch and copy operations."""

import shutil
import tempfile
from pathlib import Path

from remote import fetch_remote_to_temp


def is_remote_source(source: str) -> bool:
    """Check if source is a remote URL.
    
    Args:
        source: Path or URL string
    
    Returns:
        True if source is a URL, False otherwise
    """
    return isinstance(source, str) and (
        source.startswith("http://") or source.startswith("https://")
    )


def copy_remote_skill(url: str, dest: Path, *, validate: bool = True) -> Path:
    """Copy a skill from remote URL to destination.
    
    Fetches the skill to a temporary directory, then copies to destination.
    Automatically cleans up temporary directory.
    
    Args:
        url: Remote skill URL
        dest: Destination directory
        validate: Whether to validate skill structure (reserved for future)
    
    Returns:
        Path to copied skill directory
    
    Raises:
        ValueError: If URL is invalid
        OSError: If fetch or copy operation fails
    """
    # Fetch to temporary directory
    temp_dir = fetch_remote_to_temp(url)
    
    try:
        dest = dest.resolve()
        
        # Remove existing destination if it exists
        if dest.exists():
            shutil.rmtree(dest)
        
        # Copy from temp to destination
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(temp_dir, dest)
        
        return dest
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
