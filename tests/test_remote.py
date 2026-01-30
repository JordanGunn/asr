"""Tests for remote module."""

import pytest

from remote import (
    InvalidRemoteUrlError,
    derive_skill_name,
    parse_github_url,
    parse_gitlab_url,
    validate_remote_url,
)


class TestURLParsing:
    """Test URL parsing functions."""

    def test_parse_github_url_full(self):
        """Test parsing complete GitHub URL."""
        url = "https://github.com/user/repo/tree/main/skills/my-skill"
        result = parse_github_url(url)

        assert result is not None
        assert result["owner"] == "user"
        assert result["repo"] == "repo"
        assert result["ref"] == "main"
        assert result["path"] == "skills/my-skill"

    def test_parse_github_url_minimal(self):
        """Test parsing minimal GitHub URL."""
        url = "https://github.com/user/repo"
        result = parse_github_url(url)

        assert result is not None
        assert result["owner"] == "user"
        assert result["repo"] == "repo"
        assert result["ref"] == "main"  # Default
        assert result["path"] == ""

    def test_parse_github_url_with_blob(self):
        """Test parsing GitHub blob URL."""
        url = "https://github.com/user/repo/blob/dev/path/to/file.md"
        result = parse_github_url(url)

        assert result is not None
        assert result["ref"] == "dev"
        assert result["path"] == "path/to/file.md"

    def test_parse_gitlab_url_full(self):
        """Test parsing complete GitLab URL."""
        url = "https://gitlab.com/org/project/tree/main/skills/cool-skill"
        result = parse_gitlab_url(url)

        assert result is not None
        assert result["owner"] == "org"
        assert result["repo"] == "project"
        assert result["ref"] == "main"
        assert result["path"] == "skills/cool-skill"

    def test_parse_gitlab_url_with_dash_tree(self):
        """Test parsing GitLab URL with /-/tree/ pattern."""
        url = "https://gitlab.com/org/project/-/tree/dev/path"
        result = parse_gitlab_url(url)

        assert result is not None
        assert result["ref"] == "dev"
        assert result["path"] == "path"

    def test_parse_invalid_url(self):
        """Test parsing invalid URLs."""
        assert parse_github_url("https://example.com/path") is None
        assert parse_gitlab_url("https://github.com/user/repo") is None


class TestNameDerivation:
    """Test skill name derivation."""

    def test_derive_name_github_with_path(self):
        """Test deriving name from GitHub URL with path."""
        url = "https://github.com/user/awesome-repo/tree/main/skills/cool-skill"
        name = derive_skill_name(url)

        assert name == "awesome-repo-cool-skill"

    def test_derive_name_github_root(self):
        """Test deriving name from GitHub URL at root."""
        url = "https://github.com/user/my-skill"
        name = derive_skill_name(url)

        assert name == "my-skill"

    def test_derive_name_gitlab(self):
        """Test deriving name from GitLab URL."""
        url = "https://gitlab.com/org/project/tree/main/my-skill"
        name = derive_skill_name(url)

        assert name == "project-my-skill"

    def test_derive_name_normalizes_case(self):
        """Test that name derivation normalizes to lowercase."""
        url = "https://github.com/User/MyRepo/tree/main/MySkill"
        name = derive_skill_name(url)

        assert name == "myrepo-myskill"

    def test_derive_name_invalid_url(self):
        """Test error on invalid URL."""
        with pytest.raises(InvalidRemoteUrlError):
            derive_skill_name("https://example.com/invalid")


class TestURLValidation:
    """Test URL validation."""

    def test_validate_github_url(self):
        """Test validating GitHub URL."""
        valid, msg = validate_remote_url("https://github.com/user/repo/tree/main/skill")

        assert valid
        assert msg == ""

    def test_validate_gitlab_url(self):
        """Test validating GitLab URL."""
        valid, msg = validate_remote_url("https://gitlab.com/org/project")

        assert valid
        assert msg == ""

    def test_validate_invalid_protocol(self):
        """Test invalid protocol."""
        valid, msg = validate_remote_url("ftp://example.com/path")

        assert not valid
        assert "http" in msg.lower()

    def test_validate_invalid_host(self):
        """Test invalid host."""
        valid, msg = validate_remote_url("https://example.com/path")

        assert not valid
        assert "github" in msg.lower() or "gitlab" in msg.lower()

    def test_validate_empty_url(self):
        """Test empty URL."""
        valid, msg = validate_remote_url("")

        assert not valid
        assert "empty" in msg.lower()
