"""Tests for multi-skill repo detection."""

import tempfile
from pathlib import Path

from commands.add import _add_single_remote_skill, _find_skill_dirs


class TestFindSkillDirs:
    """Test _find_skill_dirs function."""

    def test_find_single_skill_at_root(self):
        """Find single SKILL.md at root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "SKILL.md").write_text("# Skill\n")

            skill_dirs = _find_skill_dirs(root)

            assert len(skill_dirs) == 1
            assert skill_dirs[0] == root

    def test_find_multiple_skills(self):
        """Find multiple SKILL.md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "skill-one").mkdir()
            (root / "skill-one" / "SKILL.md").write_text("# Skill One\n")
            (root / "skill-two").mkdir()
            (root / "skill-two" / "SKILL.md").write_text("# Skill Two\n")

            skill_dirs = _find_skill_dirs(root)

            assert len(skill_dirs) == 2
            names = [d.name for d in skill_dirs]
            assert "skill-one" in names
            assert "skill-two" in names

    def test_find_nested_skills(self):
        """Find nested SKILL.md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "category" / "skill-one").mkdir(parents=True)
            (root / "category" / "skill-one" / "SKILL.md").write_text("# Skill\n")
            (root / "skill-two").mkdir()
            (root / "skill-two" / "SKILL.md").write_text("# Skill Two\n")

            skill_dirs = _find_skill_dirs(root)

            assert len(skill_dirs) == 2

    def test_find_no_skills(self):
        """Return empty list when no SKILL.md found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("# No skills here\n")

            skill_dirs = _find_skill_dirs(root)

            assert skill_dirs == []

    def test_sort_by_depth_then_name(self):
        """Skills sorted by depth (shallowest first), then alphabetically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create skills at different depths
            (root / "z-skill").mkdir()
            (root / "z-skill" / "SKILL.md").write_text("# Z\n")

            (root / "a-skill").mkdir()
            (root / "a-skill" / "SKILL.md").write_text("# A\n")

            (root / "nested" / "deep-skill").mkdir(parents=True)
            (root / "nested" / "deep-skill" / "SKILL.md").write_text("# Deep\n")

            skill_dirs = _find_skill_dirs(root)

            assert len(skill_dirs) == 3
            # Should be: a-skill, z-skill (depth 1), then deep-skill (depth 2)
            assert skill_dirs[0].name == "a-skill"
            assert skill_dirs[1].name == "z-skill"
            assert skill_dirs[2].name == "deep-skill"


class TestAddSingleRemoteSkill:
    """Test _add_single_remote_skill function."""

    def test_add_valid_skill(self):
        """Add a valid skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test-skill"
            skill_dir.mkdir()

            # Create minimal valid skill
            (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: Test skill
---

# Test Skill

Test content.
""")

            from unittest.mock import MagicMock, patch

            args = MagicMock()
            args.quiet = True
            args.json = False
            args.strict = False

            results = []

            with patch("commands.add.add_skill") as mock_add:
                mock_add.return_value = True  # is_new

                result = _add_single_remote_skill(
                    skill_dir,
                    "https://example.com/test-skill",
                    "https://example.com",
                    args,
                    max_lines=500,
                    results=results,
                )

                assert result["added"] is True
                assert result["name"] == "test-skill"
                assert len(results) == 1
                mock_add.assert_called_once()

    def test_skip_invalid_skill(self):
        """Skip skill with validation errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "bad-skill"
            skill_dir.mkdir()

            # Create invalid skill (missing SKILL.md)
            (skill_dir / "README.md").write_text("Not a skill")

            from unittest.mock import MagicMock

            args = MagicMock()
            args.quiet = True
            args.json = False
            args.strict = False

            results = []
            result = _add_single_remote_skill(
                skill_dir,
                "https://example.com/bad-skill",
                "https://example.com",
                args,
                max_lines=500,
                results=results,
            )

            assert result["added"] is False
            assert "validation errors" in result["reason"]
