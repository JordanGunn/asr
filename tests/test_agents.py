"""Tests for agent driver system."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from agents import (
    ClaudeDriver,
    CodexDriver,
    CopilotDriver,
    OpenCodeDriver,
    detect_available_agents,
    get_all_agent_names,
    get_driver,
)
from agents.base import AgentDriver


class TestAgentDriverInterface:
    """Test the abstract AgentDriver interface."""

    def test_codex_driver_name(self):
        """Codex driver returns correct name."""
        driver = CodexDriver()
        assert driver.get_name() == "codex"
        assert driver.get_binary_name() == "codex"

    def test_copilot_driver_name(self):
        """Copilot driver returns correct name."""
        driver = CopilotDriver()
        assert driver.get_name() == "copilot"
        assert driver.get_binary_name() == "copilot"

    def test_claude_driver_name(self):
        """Claude driver returns correct name."""
        driver = ClaudeDriver()
        assert driver.get_name() == "claude"
        assert driver.get_binary_name() == "claude"

    def test_opencode_driver_name(self):
        """OpenCode driver returns correct name."""
        driver = OpenCodeDriver()
        assert driver.get_name() == "opencode"
        assert driver.get_binary_name() == "opencode"


class TestAgentDetection:
    """Test agent binary detection."""

    @patch("shutil.which")
    def test_detect_when_binary_exists(self, mock_which):
        """detect() returns True when binary exists."""
        mock_which.return_value = "/usr/bin/codex"
        driver = CodexDriver()
        assert driver.detect() is True
        mock_which.assert_called_with("codex")

    @patch("shutil.which")
    def test_detect_when_binary_missing(self, mock_which):
        """detect() returns False when binary not found."""
        mock_which.return_value = None
        driver = CodexDriver()
        assert driver.detect() is False
        mock_which.assert_called_with("codex")


class TestCommandBuilding:
    """Test command building for each agent."""

    def test_codex_build_command(self):
        """Codex builds correct command format."""
        driver = CodexDriver()
        cwd = Path("/tmp")
        cmd = driver.build_command("skill content", "do something", cwd)

        assert cmd[0] == "codex"
        assert cmd[1] == "exec"
        assert "skill content" in cmd[2]
        assert "do something" in cmd[2]
        assert "SKILL INSTRUCTIONS" in cmd[2]

    def test_copilot_build_command(self):
        """Copilot builds correct command format."""
        driver = CopilotDriver()
        cwd = Path("/tmp")
        cmd = driver.build_command("skill content", "do something", cwd)

        assert cmd[0] == "copilot"
        assert cmd[1] == "-p"
        assert "skill content" in cmd[2]
        assert "do something" in cmd[2]

    def test_claude_build_command(self):
        """Claude builds correct command format."""
        driver = ClaudeDriver()
        cwd = Path("/tmp")
        cmd = driver.build_command("skill content", "do something", cwd)

        assert cmd[0] == "claude"
        assert cmd[2] == "-p"
        assert "skill content" in cmd[1]
        assert "do something" in cmd[1]

    def test_opencode_build_command(self):
        """OpenCode builds correct command format."""
        driver = OpenCodeDriver()
        cwd = Path("/tmp")
        cmd = driver.build_command("skill content", "do something", cwd)

        assert cmd[0] == "opencode"
        assert cmd[1] == "run"
        assert "skill content" in cmd[2]
        assert "do something" in cmd[2]


class TestPromptInjection:
    """Test prompt injection formatting."""

    def test_format_injected_prompt_includes_skill(self):
        """Injected prompt includes skill content."""
        driver = CodexDriver()
        prompt = driver.format_injected_prompt("SKILL TEXT", "USER TEXT", Path("/tmp"))

        assert "SKILL TEXT" in prompt
        assert "SKILL INSTRUCTIONS" in prompt
        assert "END SKILL" in prompt

    def test_format_injected_prompt_includes_user_request(self):
        """Injected prompt includes user request."""
        driver = CodexDriver()
        prompt = driver.format_injected_prompt("skill", "update csv", Path("/tmp"))

        assert "USER REQUEST: update csv" in prompt

    def test_format_injected_prompt_includes_cwd(self):
        """Injected prompt includes working directory."""
        driver = CodexDriver()
        cwd = Path("/home/user/project")
        prompt = driver.format_injected_prompt("skill", "request", cwd)

        assert str(cwd) in prompt
        assert "Working directory:" in prompt


class TestAgentExecution:
    """Test agent execution."""

    @patch("agents.base.AgentDriver.detect")
    @patch("subprocess.run")
    def test_execute_success(self, mock_run, mock_detect):
        """Execute runs command successfully."""
        mock_detect.return_value = True
        mock_run.return_value = subprocess.CompletedProcess([], 0, "", "")

        driver = CodexDriver()
        result = driver.execute("skill", "prompt", Path("/tmp"))

        assert result.returncode == 0
        mock_run.assert_called_once()

    @patch("agents.base.AgentDriver.detect")
    def test_execute_raises_when_binary_missing(self, mock_detect):
        """Execute raises FileNotFoundError when binary not found."""
        mock_detect.return_value = False

        driver = CodexDriver()
        with pytest.raises(FileNotFoundError, match="codex binary 'codex' not found"):
            driver.execute("skill", "prompt", Path("/tmp"))

    @patch("agents.base.AgentDriver.detect")
    @patch("subprocess.run")
    def test_execute_uses_cwd(self, mock_run, mock_detect):
        """Execute uses provided working directory."""
        mock_detect.return_value = True
        mock_run.return_value = subprocess.CompletedProcess([], 0, "", "")

        driver = CodexDriver()
        cwd = Path("/custom/dir")
        driver.execute("skill", "prompt", cwd)

        call_args = mock_run.call_args
        assert call_args.kwargs["cwd"] == cwd

    @patch("agents.base.AgentDriver.detect")
    @patch("subprocess.run")
    def test_execute_defaults_to_current_dir(self, mock_run, mock_detect):
        """Execute defaults to current directory when cwd not provided."""
        mock_detect.return_value = True
        mock_run.return_value = subprocess.CompletedProcess([], 0, "", "")

        driver = CodexDriver()
        driver.execute("skill", "prompt")

        call_args = mock_run.call_args
        assert call_args.kwargs["cwd"] == Path.cwd()


class TestAgentRegistry:
    """Test agent registry and factory."""

    def test_get_driver_codex(self):
        """get_driver returns Codex driver."""
        driver = get_driver("codex")
        assert isinstance(driver, CodexDriver)

    def test_get_driver_copilot(self):
        """get_driver returns Copilot driver."""
        driver = get_driver("copilot")
        assert isinstance(driver, CopilotDriver)

    def test_get_driver_claude(self):
        """get_driver returns Claude driver."""
        driver = get_driver("claude")
        assert isinstance(driver, ClaudeDriver)

    def test_get_driver_opencode(self):
        """get_driver returns OpenCode driver."""
        driver = get_driver("opencode")
        assert isinstance(driver, OpenCodeDriver)

    def test_get_driver_invalid_raises(self):
        """get_driver raises ValueError for invalid agent."""
        with pytest.raises(ValueError, match="Invalid agent 'invalid'"):
            get_driver("invalid")

    def test_get_all_agent_names(self):
        """get_all_agent_names returns all supported agents."""
        names = get_all_agent_names()
        assert names == ["claude", "codex", "copilot", "opencode"]

    @patch("shutil.which")
    def test_detect_available_agents_all(self, mock_which):
        """detect_available_agents finds all when present."""
        mock_which.return_value = "/usr/bin/agent"
        available = detect_available_agents()
        assert set(available) == {"claude", "codex", "copilot", "opencode"}

    @patch("shutil.which")
    def test_detect_available_agents_none(self, mock_which):
        """detect_available_agents returns empty when none present."""
        mock_which.return_value = None
        available = detect_available_agents()
        assert available == []

    @patch("shutil.which")
    def test_detect_available_agents_partial(self, mock_which):
        """detect_available_agents finds subset of agents."""

        def which_side_effect(binary):
            return "/usr/bin/codex" if binary == "codex" else None

        mock_which.side_effect = which_side_effect
        available = detect_available_agents()
        assert available == ["codex"]


class TestDriverIsAbstract:
    """Test that AgentDriver is properly abstract."""

    def test_cannot_instantiate_base_driver(self):
        """Cannot instantiate AgentDriver directly."""
        with pytest.raises(TypeError):
            AgentDriver()
