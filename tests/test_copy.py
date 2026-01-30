"""Tests for skillcopy module."""

import pytest

from skillcopy import copy_skill, is_remote_source
from skillcopy.local import copy_local_skill


def test_is_remote_source():
    """Test remote source detection."""
    assert is_remote_source("https://github.com/user/repo")
    assert is_remote_source("http://gitlab.com/user/repo")
    assert not is_remote_source("/path/to/skill")
    assert not is_remote_source("relative/path")
    assert not is_remote_source("")


def test_copy_local_skill(tmp_path):
    """Test copying local skill."""
    # Create source skill
    src = tmp_path / "source"
    src.mkdir()
    (src / "SKILL.md").write_text("# Test Skill")
    (src / "file.txt").write_text("content")

    # Copy to destination
    dest = tmp_path / "dest"
    result = copy_local_skill(str(src), dest)

    assert result == dest
    assert dest.exists()
    assert (dest / "SKILL.md").read_text() == "# Test Skill"
    assert (dest / "file.txt").read_text() == "content"


def test_copy_local_skill_overwrites_existing(tmp_path):
    """Test that copying overwrites existing destination."""
    src = tmp_path / "source"
    src.mkdir()
    (src / "SKILL.md").write_text("# New Version")

    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "old_file.txt").write_text("old")

    copy_local_skill(str(src), dest)

    assert (dest / "SKILL.md").exists()
    assert not (dest / "old_file.txt").exists()


def test_copy_local_skill_missing_source(tmp_path):
    """Test error handling for missing source."""
    dest = tmp_path / "dest"

    with pytest.raises(FileNotFoundError):
        copy_local_skill("/nonexistent/path", dest)


def test_copy_skill_dispatches_to_local(tmp_path):
    """Test that copy_skill dispatches to local for filesystem paths."""
    src = tmp_path / "source"
    src.mkdir()
    (src / "SKILL.md").write_text("# Test")

    dest = tmp_path / "dest"
    copy_skill(str(src), dest)

    assert dest.exists()
    assert (dest / "SKILL.md").exists()
