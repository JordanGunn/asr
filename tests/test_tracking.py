"""Tests for tracking metadata functionality."""

import yaml

from tracking import extract_metadata, inject_metadata, strip_tracking_metadata


def test_inject_metadata_success(tmp_path):
    """Test successful metadata injection."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    # Create valid SKILL.md with frontmatter
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: Test skill
---

# Test Skill

Content here.
""",
        encoding="utf-8",
    )

    # Inject metadata
    result = inject_metadata(skill_dir, "abc123hash", "/source/path")

    assert result is True

    # Verify metadata was injected
    metadata = extract_metadata(skill_dir)
    assert metadata is not None
    assert metadata["hash"] == "abc123hash"
    assert metadata["source"] == "/source/path"
    assert "synced" in metadata


def test_inject_metadata_no_skill_md(tmp_path):
    """Test injection fails gracefully when SKILL.md missing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    result = inject_metadata(skill_dir, "abc123", "/source")
    assert result is False


def test_inject_metadata_no_frontmatter(tmp_path):
    """Test injection fails when no frontmatter."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("# Just markdown\n\nNo frontmatter.", encoding="utf-8")

    result = inject_metadata(skill_dir, "abc123", "/source")
    assert result is False


def test_extract_metadata_success(tmp_path):
    """Test successful metadata extraction."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
metadata:
  oasr:
    hash: abc123
    source: /source/path
    synced: 2026-01-30T10:00:00Z
---

# Content
""",
        encoding="utf-8",
    )

    metadata = extract_metadata(skill_dir)
    assert metadata is not None
    assert metadata["hash"] == "abc123"
    assert metadata["source"] == "/source/path"


def test_extract_metadata_missing_fields(tmp_path):
    """Test extraction returns None when required fields missing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
metadata:
  oasr:
    source: /source/path
---
""",
        encoding="utf-8",
    )

    metadata = extract_metadata(skill_dir)
    assert metadata is None  # Missing 'hash' field


def test_extract_metadata_corrupted(tmp_path):
    """Test extraction handles corrupted metadata gracefully."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
metadata: "not a dict"
---
""",
        encoding="utf-8",
    )

    metadata = extract_metadata(skill_dir)
    assert metadata is None


def test_extract_metadata_no_file(tmp_path):
    """Test extraction returns None when SKILL.md missing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    metadata = extract_metadata(skill_dir)
    assert metadata is None


def test_strip_tracking_metadata():
    """Test stripping metadata.oasr from frontmatter."""
    frontmatter = {
        "name": "test-skill",
        "description": "Test",
        "metadata": {"oasr": {"hash": "abc", "source": "/path"}, "other": "data"},
    }

    cleaned = strip_tracking_metadata(frontmatter)

    assert "oasr" not in cleaned.get("metadata", {})
    assert cleaned["metadata"]["other"] == "data"


def test_strip_tracking_metadata_removes_empty_metadata():
    """Test stripping removes metadata field if empty after removal."""
    frontmatter = {"name": "test-skill", "metadata": {"oasr": {"hash": "abc"}}}

    cleaned = strip_tracking_metadata(frontmatter)

    assert "metadata" not in cleaned


def test_inject_metadata_creates_metadata_field(tmp_path):
    """Test injection creates metadata field if missing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
description: No metadata field
---
""",
        encoding="utf-8",
    )

    result = inject_metadata(skill_dir, "hash123", "/source")
    assert result is True

    # Verify metadata field was created
    content = skill_md.read_text(encoding="utf-8")
    data = yaml.safe_load(content.split("---")[1])
    assert "metadata" in data
    assert "oasr" in data["metadata"]
