"""Tests for config command."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from commands.config import run_get, run_list, run_path, run_set
from config import load_config, save_config


class MockArgs:
    """Mock argparse.Namespace for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestConfigSet:
    """Test config set command."""

    def test_set_agent_codex(self, capsys):
        """Set agent to codex."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="agent", value="codex", config=config_path)

            result = run_set(args)

            assert result == 0
            captured = capsys.readouterr()
            assert "Default agent set to: codex" in captured.out

            # Verify saved
            config = load_config(config_path)
            assert config["agent"]["default"] == "codex"

    def test_set_agent_copilot(self):
        """Set agent to copilot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="agent", value="copilot", config=config_path)

            result = run_set(args)

            assert result == 0
            config = load_config(config_path)
            assert config["agent"]["default"] == "copilot"

    def test_set_agent_invalid(self, capsys):
        """Set agent to invalid value fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="agent", value="invalid", config=config_path)

            result = run_set(args)

            assert result == 1
            captured = capsys.readouterr()
            assert "Invalid agent 'invalid'" in captured.err

    def test_set_unsupported_key(self, capsys):
        """Set unsupported key fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="unsupported", value="value", config=config_path)

            result = run_set(args)

            assert result == 1
            captured = capsys.readouterr()
            assert "Unsupported config key" in captured.err

    @patch("commands.config.detect_available_agents")
    def test_set_agent_warns_when_binary_missing(self, mock_detect, capsys):
        """Set agent shows warning when binary not in PATH."""
        mock_detect.return_value = []  # No agents available

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="agent", value="codex", config=config_path)

            result = run_set(args)

            assert result == 0
            captured = capsys.readouterr()
            assert "Warning" in captured.err
            assert "binary not found" in captured.err


class TestConfigGet:
    """Test config get command."""

    def test_get_agent_when_set(self, capsys):
        """Get agent when configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = {"agent": {"default": "codex"}, "validation": {}, "adapter": {}}
            save_config(config, config_path)

            args = MockArgs(key="agent", config=config_path)
            result = run_get(args)

            assert result == 0
            captured = capsys.readouterr()
            assert captured.out.strip() == "codex"

    def test_get_agent_when_not_set(self, capsys):
        """Get agent when not configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="agent", config=config_path)

            result = run_get(args)

            assert result == 1
            captured = capsys.readouterr()
            assert "No default agent configured" in captured.err

    def test_get_unsupported_key(self, capsys):
        """Get unsupported key fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(key="unsupported", config=config_path)

            result = run_get(args)

            assert result == 1
            captured = capsys.readouterr()
            assert "Unsupported config key" in captured.err


class TestConfigList:
    """Test config list command."""

    def test_list_with_agent_configured(self, capsys):
        """List config when agent is configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = {
                "agent": {"default": "codex"},
                "validation": {"reference_max_lines": 500, "strict": False},
                "adapter": {"default_targets": ["cursor", "windsurf"]},
            }
            save_config(config, config_path)

            args = MockArgs(config=config_path)
            result = run_list(args)

            assert result == 0
            captured = capsys.readouterr()
            assert "default = codex" in captured.out
            assert "[agent]" in captured.out
            assert "[validation]" in captured.out
            assert "[adapter]" in captured.out

    def test_list_without_agent_configured(self, capsys):
        """List config when agent is not configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(config=config_path)

            result = run_list(args)

            assert result == 0
            captured = capsys.readouterr()
            assert "(not set)" in captured.out

    @patch("commands.config.detect_available_agents")
    def test_list_shows_available_agents(self, mock_detect, capsys):
        """List shows available agents."""
        mock_detect.return_value = ["codex", "claude"]

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            args = MockArgs(config=config_path)

            result = run_list(args)

            assert result == 0
            captured = capsys.readouterr()
            assert "codex" in captured.out
            assert "claude" in captured.out


class TestConfigPath:
    """Test config path command."""

    def test_path_shows_default(self, capsys):
        """Path shows default config location."""
        args = MockArgs()
        result = run_path(args)

        assert result == 0
        captured = capsys.readouterr()
        assert ".oasr/config.toml" in captured.out

    def test_path_shows_override(self, capsys):
        """Path shows override config location."""
        custom_path = Path("/custom/config.toml")
        args = MockArgs(config=custom_path)
        result = run_path(args)

        assert result == 0
        captured = capsys.readouterr()
        assert str(custom_path) in captured.out
