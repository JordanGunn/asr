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


def copy_remote_skill(url: str, dest: Path, *, validate: bool = True, force_refresh: bool = False) -> Path:
    """Copy a skill from remote URL to destination.
    
    Smart caching: If destination exists and content matches manifest hash,
    skip the fetch to avoid unnecessary API calls.
    
    Args:
        url: Remote skill URL
        dest: Destination directory
        validate: Whether to validate skill structure (reserved for future)
        force_refresh: If True, always fetch (ignore cache)
    
    Returns:
        Path to copied skill directory
    
    Raises:
        ValueError: If URL is invalid
        OSError: If fetch or copy operation fails
    """
    dest = dest.resolve()
    
    # Smart check: if destination exists and is up-to-date, skip fetch
    if not force_refresh and dest.exists():
        try:
            from manifest import load_manifest, hash_directory
            
            # Try to load manifest to get expected hash
            # Derive skill name from destination directory name
            skill_name = dest.name
            manifest = load_manifest(skill_name)
            
            # If manifest source matches this URL, compare hashes
            if manifest and manifest.source_path == url:
                current_hash, _ = hash_directory(dest)
                if current_hash == manifest.content_hash:
                    # Destination is up-to-date, no need to fetch
                    return dest
        except Exception:
            # If any error checking cache, proceed with fetch
            pass
    
    # Fetch to temporary directory
    temp_dir = fetch_remote_to_temp(url)
    
    try:
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
