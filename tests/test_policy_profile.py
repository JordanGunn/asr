"""Tests for policy.profile module."""

from pathlib import Path

import policy
from policy import Profile
from profiles.builtins import SAFE


class TestProfile:
    """Test Profile dataclass."""

    def test_default_profile_creation(self):
        """Test creating profile with all defaults."""
        profile = Profile(name="test")
        assert profile.name == "test"
        assert profile.deny_shell is True
        assert profile.network is False
        assert profile.allow_env is False
        assert len(profile.allowed_commands) > 0

    def test_custom_profile_creation(self):
        """Test creating profile with custom values."""
        profile = Profile(
            name="custom",
            network=True,
            allow_env=True,
            deny_shell=False,
            allowed_commands=["bash", "python"],
        )
        assert profile.network is True
        assert profile.allow_env is True
        assert profile.deny_shell is False
        assert profile.allowed_commands == ["bash", "python"]

    def test_path_resolution_expands_tilde(self):
        """Test that ~ is expanded in paths."""
        # Use real home path - just verify ~ was expanded
        profile = Profile(name="test", fs_read_roots=["~/documents"])
        # Should not contain ~ anymore, should be absolute
        assert "~" not in profile.fs_read_roots[0]
        assert profile.fs_read_roots[0].endswith("documents")
        assert Path(profile.fs_read_roots[0]).is_absolute()

    def test_path_resolution_makes_relative_absolute(self, tmp_path, monkeypatch):
        """Test that relative paths become absolute."""
        monkeypatch.chdir(tmp_path)
        profile = Profile(name="test", fs_read_roots=["./data"])
        assert str(tmp_path / "data") in profile.fs_read_roots[0]


class TestLoadProfile:
    """Test policy.load() function."""

    def test_load_safe_default_when_no_config(self):
        """Test loading safe profile with empty config."""
        profile = policy.load({}, "safe")
        assert profile.name == "safe"
        assert profile.deny_shell is True
        assert profile.network is False
        assert profile.allow_env is False

    def test_load_safe_default_when_profile_missing(self):
        """Test loading missing profile falls back to safe defaults."""
        config = {"profiles": {"dev": {"network": True}}}
        profile = policy.load(config, "production")  # doesn't exist
        assert profile.name == "production"
        # Should use safe defaults
        assert profile.network is False
        assert profile.deny_shell is True

    def test_load_user_defined_profile(self):
        """Test loading user-defined profile from config."""
        config = {
            "profiles": {
                "dev": {
                    "network": True,
                    "allow_env": True,
                    "deny_shell": False,
                    "allowed_commands": ["bash", "curl", "git"],
                }
            }
        }
        profile = policy.load(config, "dev")
        assert profile.name == "dev"
        assert profile.network is True
        assert profile.allow_env is True
        assert profile.deny_shell is False
        assert "bash" in profile.allowed_commands
        assert "curl" in profile.allowed_commands

    def test_load_partial_profile_merges_with_defaults(self):
        """Test that partial profiles merge with safe defaults."""
        config = {"profiles": {"custom": {"network": True}}}  # Only override network
        profile = policy.load(config, "custom")
        assert profile.network is True  # overridden
        assert profile.deny_shell is True  # default
        assert profile.allow_env is False  # default

    def test_malformed_config_falls_back_to_safe(self):
        """Test that errors in config parsing fall back to safe."""
        config = {"profiles": {"broken": "not a dict"}}
        profile = policy.load(config, "broken")
        # Should use safe defaults despite error
        assert profile.deny_shell is True
        assert profile.network is False


class TestSummarizeProfile:
    """Test policy.summarize() function."""

    def test_summary_includes_key_info(self):
        """Test that summary includes skill, agent, profile names."""
        profile = Profile(name="safe")
        summary = policy.summarize(profile, "test-skill", "codex")
        assert "test-skill" in summary
        assert "codex" in summary
        assert "safe" in summary

    def test_summary_shows_policy_settings(self):
        """Test that summary shows network, env, shell settings."""
        profile = Profile(name="dev", network=True, allow_env=True, deny_shell=False)
        summary = policy.summarize(profile, "test-skill", "codex")
        assert "network" in summary.lower()
        assert "allowed" in summary.lower()  # network allowed
        assert "environment" in summary.lower()
        assert "shell" in summary.lower()

    def test_summary_shows_allowed_commands(self):
        """Test that summary lists allowed commands."""
        profile = Profile(name="custom", allowed_commands=["rg", "fd", "jq"])
        summary = policy.summarize(profile, "test-skill", "codex")
        assert "rg" in summary
        assert "fd" in summary
        assert "jq" in summary

    def test_summary_truncates_long_command_lists(self):
        """Test that very long command lists are truncated."""
        profile = Profile(name="permissive", allowed_commands=["cmd" + str(i) for i in range(50)])
        summary = policy.summarize(profile, "test-skill", "codex")
        assert "..." in summary  # should be truncated

    def test_summary_shows_paths(self):
        """Test that summary shows read/write roots and deny paths."""
        profile = Profile(
            name="custom",
            fs_read_roots=["./data"],
            fs_write_roots=["./output"],
            deny_paths=["~/.ssh", "~/.aws"],
        )
        summary = policy.summarize(profile, "test-skill", "codex")
        assert "read roots" in summary.lower() or "read" in summary.lower()
        assert "write roots" in summary.lower() or "write" in summary.lower()
        assert "deny" in summary.lower()


class TestSafeDefaults:
    """Test SAFE default constants."""

    def test_safe_defaults_are_conservative(self):
        """Test that safe defaults are appropriately restrictive."""
        assert SAFE["deny_shell"] is True
        assert SAFE["network"] is False
        assert SAFE["allow_env"] is False

    def test_safe_defaults_include_sensitive_deny_paths(self):
        """Test that safe defaults protect sensitive directories."""
        deny_paths = SAFE["deny_paths"]
        assert any("ssh" in p.lower() for p in deny_paths)
        assert any("aws" in p.lower() for p in deny_paths)
        assert any(".env" in p for p in deny_paths)

    def test_safe_defaults_have_minimal_allowed_commands(self):
        """Test that safe defaults allow only minimal commands."""
        allowed = SAFE["allowed_commands"]
        # Should be a small set of read-only tools
        assert len(allowed) <= 10
        # Should not include dangerous commands
        assert "bash" not in allowed
        assert "sh" not in allowed
        assert "rm" not in allowed
