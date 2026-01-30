"""Local filesystem skill copy operations."""

import shutil
from pathlib import Path


def copy_local_skill(source: str, dest: Path, *, validate: bool = True) -> Path:
    """Copy a skill from local filesystem to destination.

    Args:
        source: Local filesystem path
        dest: Destination directory
        validate: Whether to validate skill structure (reserved for future)

    Returns:
        Path to copied skill directory

    Raises:
        FileNotFoundError: If source doesn't exist
        OSError: If copy operation fails
    """
    src_path = Path(source).resolve()

    if not src_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    if not src_path.is_dir():
        raise ValueError(f"Source is not a directory: {source}")

    dest = dest.resolve()

    # Remove existing destination if it exists
    if dest.exists():
        shutil.rmtree(dest)

    # Copy skill directory
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_path, dest)

    return dest
