"""Tests for policy.enforcement module."""

from unittest import mock

import policy
from policy import Profile


class TestAssessRisk:
    """Test policy.assess_risk() function."""

    def test_safe_profile_interactive_no_confirmation(self):
        """Test that safe profile with interactive input needs no confirmation."""
        profile = Profile(name="safe")
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=False,
            force_confirm=False,
        )
        assert needs_confirm is False
        assert len(reasons) == 0

    def test_stdin_triggers_confirmation(self):
        """Test that stdin input triggers confirmation."""
        profile = Profile(name="safe")
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=True,
            instructions_file_used=False,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert "stdin" in " ".join(reasons).lower()

    def test_file_instructions_trigger_confirmation(self):
        """Test that file-based prompts trigger confirmation."""
        profile = Profile(name="safe")
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=True,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert "file" in " ".join(reasons).lower()

    def test_non_safe_profile_triggers_confirmation(self):
        """Test that non-safe profiles trigger confirmation."""
        profile = Profile(name="dev")
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=False,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert "dev" in " ".join(reasons).lower()

    def test_network_enabled_triggers_confirmation(self):
        """Test that network access triggers confirmation."""
        profile = Profile(name="safe", network=True)
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=False,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert "network" in " ".join(reasons).lower()

    def test_env_enabled_triggers_confirmation(self):
        """Test that environment access triggers confirmation."""
        profile = Profile(name="safe", allow_env=True)
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=False,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert "environment" in " ".join(reasons).lower()

    def test_shell_enabled_triggers_confirmation(self):
        """Test that shell access triggers confirmation."""
        profile = Profile(name="safe", deny_shell=False)
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=False,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert "shell" in " ".join(reasons).lower()

    def test_force_confirm_flag_triggers_confirmation(self):
        """Test that --confirm flag triggers confirmation."""
        profile = Profile(name="safe")
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=False,
            instructions_file_used=False,
            force_confirm=True,
        )
        assert needs_confirm is True
        assert "explicit" in " ".join(reasons).lower() or "confirm" in " ".join(reasons).lower()

    def test_multiple_triggers_list_all_reasons(self):
        """Test that multiple risk triggers are all listed."""
        profile = Profile(name="dev", network=True, allow_env=True)
        needs_confirm, reasons = policy.assess_risk(
            profile=profile,
            stdin_used=True,
            instructions_file_used=True,
            force_confirm=False,
        )
        assert needs_confirm is True
        assert len(reasons) >= 4  # stdin, file, profile, network, env


class TestPromptConfirmation:
    """Test policy.prompt_confirmation() function."""

    def test_confirmation_yes_returns_true(self):
        """Test that 'y' or 'yes' returns True."""
        with mock.patch("builtins.input", return_value="y"):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is True

        with mock.patch("builtins.input", return_value="yes"):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is True

    def test_confirmation_no_returns_false(self):
        """Test that 'n', 'no', or empty returns False."""
        with mock.patch("builtins.input", return_value="n"):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is False

        with mock.patch("builtins.input", return_value="no"):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is False

        with mock.patch("builtins.input", return_value=""):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is False

    def test_confirmation_ctrl_c_returns_false(self):
        """Test that Ctrl+C (KeyboardInterrupt) returns False."""
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is False

    def test_confirmation_eof_returns_false(self):
        """Test that EOF (EOFError) returns False."""
        with mock.patch("builtins.input", side_effect=EOFError):
            result = policy.prompt_confirmation("Summary", ["reason1"])
            assert result is False
