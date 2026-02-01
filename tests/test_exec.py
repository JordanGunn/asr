"""Tests for the exec command."""

import argparse
from io import StringIO
from unittest import mock

import pytest

from commands import exec as exec_cmd
from registry import SkillEntry


@pytest.fixture
def mock_registry(tmp_path):
    """Create a mock registry with a test skill."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("# Test Skill\n\nThis is a test skill.")

    # Registry returns list of SkillEntry objects
    test_skill = SkillEntry(
        path=str(skill_dir),
        name="test-skill",
        description="A test skill",
    )

    missing_skill_dir = tmp_path / "missing-skill"
    missing_skill_dir.mkdir()
    # No SKILL.md file in this one

    missing_skill = SkillEntry(
        path=str(missing_skill_dir),
        name="missing-source-skill",
        description="Skill with no SKILL.md",
    )

    registry = [test_skill, missing_skill]
    return registry, skill_file


@pytest.fixture
def mock_config_with_agent():
    """Return a config with a default agent."""
    return {
        "agent": {"default": "codex"},
        "validation": {"reference_max_lines": 500, "strict": False},
    }


@pytest.fixture
def mock_config_no_agent():
    """Return a config with no default agent."""
    return {
        "agent": {},
        "validation": {"reference_max_lines": 500, "strict": False},
    }


class TestExecCommand:
    """Test the exec command."""

    def test_exec_skill_not_found(self, capsys):
        """Test exec with a skill that doesn't exist in registry."""
        args = argparse.Namespace(
            skill_name="nonexistent-skill",
            prompt="Do something",
            instructions=None,
            agent="codex",
        )

        with mock.patch("commands.exec.load_registry", return_value={}):
            result = exec_cmd.run(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Skill 'nonexistent-skill' not found in registry" in captured.err

    def test_exec_skill_file_not_found(self, capsys, mock_registry):
        """Test exec with a skill whose SKILL.md file doesn't exist."""
        registry, _ = mock_registry

        args = argparse.Namespace(
            skill_name="missing-source-skill",
            prompt="Do something",
            instructions=None,
            agent="codex",
        )

        with mock.patch("commands.exec.load_registry", return_value=registry):
            result = exec_cmd.run(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Skill file not found" in captured.err
        assert "oasr sync" in captured.err

    def test_exec_success(self, capsys, mock_registry, mock_config_with_agent):
        """Test successful skill execution."""
        registry, skill_file = mock_registry

        args = argparse.Namespace(
            skill_name="test-skill",
            prompt="Do something",
            instructions=None,
            agent=None,  # Use default from config
        )

        mock_result = mock.Mock()
        mock_result.returncode = 0  # Success

        mock_driver = mock.Mock()
        mock_driver.execute.return_value = mock_result

        with (
            mock.patch("commands.exec.load_registry", return_value=registry),
            mock.patch("commands.exec.load_config", return_value=mock_config_with_agent),
            mock.patch("commands.exec.get_driver", return_value=mock_driver),
        ):
            result = exec_cmd.run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Executing skill 'test-skill' with codex" in captured.err

        # Verify driver was called with skill content and prompt
        mock_driver.execute.assert_called_once()
        call_args = mock_driver.execute.call_args[0]
        assert "This is a test skill" in call_args[0]  # skill content
        assert call_args[1] == "Do something"  # user prompt

    def test_exec_failure(self, capsys, mock_registry, mock_config_with_agent):
        """Test failed skill execution."""
        registry, skill_file = mock_registry

        args = argparse.Namespace(
            skill_name="test-skill",
            prompt="Do something",
            instructions=None,
            agent=None,
        )

        mock_result = mock.Mock()
        mock_result.returncode = 1  # Failure

        mock_driver = mock.Mock()
        mock_driver.execute.return_value = mock_result

        with (
            mock.patch("commands.exec.load_registry", return_value=registry),
            mock.patch("commands.exec.load_config", return_value=mock_config_with_agent),
            mock.patch("commands.exec.get_driver", return_value=mock_driver),
        ):
            result = exec_cmd.run(args)

        assert result == 1

    def test_exec_with_explicit_agent(self, capsys, mock_registry):
        """Test exec with explicit agent flag."""
        registry, skill_file = mock_registry

        args = argparse.Namespace(
            skill_name="test-skill",
            prompt="Do something",
            instructions=None,
            agent="copilot",  # Explicit agent
        )

        mock_result = mock.Mock()
        mock_result.returncode = 0  # Success

        mock_driver = mock.Mock()
        mock_driver.execute.return_value = mock_result

        available_agents = {
            "codex": True,
            "copilot": True,
            "claude": False,
            "opencode": False,
        }

        with (
            mock.patch("commands.exec.load_registry", return_value=registry),
            mock.patch("commands.exec.get_driver", return_value=mock_driver),
            mock.patch("commands.exec.detect_available_agents", return_value=available_agents),
        ):
            result = exec_cmd.run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Executing skill 'test-skill' with copilot" in captured.err


class TestGetUserPrompt:
    """Test the _get_user_prompt helper function."""

    def test_inline_prompt(self, capsys):
        """Test getting prompt from --prompt flag."""
        args = argparse.Namespace(
            prompt="My inline prompt",
            instructions=None,
        )

        result = exec_cmd._get_user_prompt(args)

        assert result == "My inline prompt"

    def test_file_prompt(self, tmp_path, capsys):
        """Test getting prompt from --instructions file."""
        instructions_file = tmp_path / "instructions.txt"
        instructions_file.write_text("My file-based prompt")

        args = argparse.Namespace(
            prompt=None,
            instructions=str(instructions_file),
        )

        result = exec_cmd._get_user_prompt(args)

        assert result == "My file-based prompt"

    def test_file_prompt_not_found(self, capsys):
        """Test error when instructions file doesn't exist."""
        args = argparse.Namespace(
            prompt=None,
            instructions="/nonexistent/file.txt",
        )

        result = exec_cmd._get_user_prompt(args)

        assert result is None
        captured = capsys.readouterr()
        assert "Instructions file not found" in captured.err

    def test_stdin_prompt(self, capsys):
        """Test getting prompt from stdin."""
        args = argparse.Namespace(
            prompt=None,
            instructions=None,
        )

        mock_stdin = StringIO("Prompt from stdin")

        with mock.patch("sys.stdin", mock_stdin):
            with mock.patch("sys.stdin.isatty", return_value=False):
                result = exec_cmd._get_user_prompt(args)

        assert result == "Prompt from stdin"

    def test_no_prompt_provided(self, capsys):
        """Test error when no prompt is provided."""
        args = argparse.Namespace(
            prompt=None,
            instructions=None,
        )

        with mock.patch("sys.stdin.isatty", return_value=True):
            result = exec_cmd._get_user_prompt(args)

        assert result is None
        captured = capsys.readouterr()
        assert "No prompt provided" in captured.err
        assert "--prompt" in captured.err
        assert "--instructions" in captured.err

    def test_conflicting_prompt_sources(self, capsys):
        """Test error when both --prompt and --instructions are provided."""
        args = argparse.Namespace(
            prompt="Inline prompt",
            instructions="file.txt",
        )

        result = exec_cmd._get_user_prompt(args)

        assert result is None
        captured = capsys.readouterr()
        assert "Cannot use both --prompt and --instructions" in captured.err


class TestGetAgentName:
    """Test the _get_agent_name helper function."""

    def test_explicit_agent_available(self, capsys):
        """Test getting agent from --agent flag when available."""
        args = argparse.Namespace(agent="codex")

        available_agents = {
            "codex": True,
            "copilot": False,
            "claude": False,
            "opencode": False,
        }

        with mock.patch("commands.exec.detect_available_agents", return_value=available_agents):
            result = exec_cmd._get_agent_name(args)

        assert result == "codex"

    def test_explicit_agent_unavailable(self, capsys):
        """Test error when explicit agent is not available."""
        args = argparse.Namespace(agent="copilot")

        available_agents = {
            "codex": True,
            "copilot": False,  # Not available
            "claude": False,
            "opencode": False,
        }

        with mock.patch("commands.exec.detect_available_agents", return_value=available_agents):
            result = exec_cmd._get_agent_name(args)

        assert result is None
        captured = capsys.readouterr()
        assert "Agent 'copilot' is not available" in captured.err
        assert "✓ codex" in captured.err
        assert "✗ copilot" in captured.err

    def test_default_from_config(self, capsys):
        """Test getting default agent from config."""
        args = argparse.Namespace(agent=None)

        config = {
            "agent": {"default": "codex"},
        }

        with mock.patch("commands.exec.load_config", return_value=config):
            result = exec_cmd._get_agent_name(args)

        assert result == "codex"

    def test_no_agent_configured(self, capsys):
        """Test error when no agent is configured."""
        args = argparse.Namespace(agent=None)

        config = {
            "agent": {},
        }

        available_agents = {
            "codex": True,
            "copilot": False,
            "claude": False,
            "opencode": False,
        }

        with (
            mock.patch("commands.exec.load_config", return_value=config),
            mock.patch("commands.exec.detect_available_agents", return_value=available_agents),
        ):
            result = exec_cmd._get_agent_name(args)

        assert result is None
        captured = capsys.readouterr()
        assert "No agent configured" in captured.err
        assert "oasr config set agent" in captured.err
        assert "oasr exec --agent" in captured.err
        assert "✓ codex" in captured.err

    def test_agent_name_case_insensitive(self, capsys):
        """Test that agent names are case-insensitive."""
        args = argparse.Namespace(agent="CODEX")

        available_agents = {
            "codex": True,
            "copilot": False,
            "claude": False,
            "opencode": False,
        }

        with mock.patch("commands.exec.detect_available_agents", return_value=available_agents):
            result = exec_cmd._get_agent_name(args)

        assert result == "codex"
