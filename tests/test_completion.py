"""Tests for shell completion functionality."""

import os
import platform
from pathlib import Path
from unittest import mock

import pytest

from commands import completion


class TestShellDetection:
    """Tests for detect_shell()."""

    def test_detect_bash_on_linux(self):
        """Test bash detection on Linux."""
        with mock.patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            with mock.patch("platform.system", return_value="Linux"):
                assert completion.detect_shell() == "bash"

    def test_detect_zsh_on_macos(self):
        """Test zsh detection on macOS."""
        with mock.patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
            with mock.patch("platform.system", return_value="Darwin"):
                assert completion.detect_shell() == "zsh"

    def test_detect_fish_on_linux(self):
        """Test fish detection on Linux."""
        with mock.patch.dict(os.environ, {"SHELL": "/usr/bin/fish"}):
            with mock.patch("platform.system", return_value="Linux"):
                assert completion.detect_shell() == "fish"

    def test_detect_powershell_on_windows(self):
        """Test PowerShell detection on Windows."""
        with mock.patch.dict(os.environ, {"PSModulePath": "some/path"}, clear=True):
            with mock.patch("platform.system", return_value="Windows"):
                assert completion.detect_shell() == "powershell"

    def test_detect_bash_on_windows_git_bash(self):
        """Test bash detection on Windows (Git Bash)."""
        with mock.patch.dict(os.environ, {"SHELL": "/usr/bin/bash"}, clear=True):
            with mock.patch("platform.system", return_value="Windows"):
                assert completion.detect_shell() == "bash"

    def test_detect_default_bash_on_linux(self):
        """Test default to bash on Linux with unknown shell."""
        with mock.patch.dict(os.environ, {"SHELL": "/bin/unknown"}, clear=True):
            with mock.patch("platform.system", return_value="Linux"):
                assert completion.detect_shell() == "bash"

    def test_detect_default_powershell_on_windows(self):
        """Test default to PowerShell on Windows with unknown shell."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("platform.system", return_value="Windows"):
                assert completion.detect_shell() == "powershell"


class TestCompletionPaths:
    """Tests for get_completion_path()."""

    def test_bash_user_path(self):
        """Test bash user completion path."""
        path = completion.get_completion_path("bash", system=False)
        assert path == Path.home() / ".bash_completion.d" / "oasr"

    def test_bash_system_path(self):
        """Test bash system completion path."""
        path = completion.get_completion_path("bash", system=True)
        assert path == Path("/etc/bash_completion.d/oasr")

    def test_zsh_user_path(self):
        """Test zsh user completion path."""
        path = completion.get_completion_path("zsh", system=False)
        assert path == Path.home() / ".zsh" / "completion" / "_oasr"

    def test_fish_user_path(self):
        """Test fish user completion path."""
        path = completion.get_completion_path("fish", system=False)
        assert path == Path.home() / ".config" / "fish" / "completions" / "oasr.fish"

    def test_powershell_path(self):
        """Test PowerShell completion path."""
        path = completion.get_completion_path("powershell", system=False)
        assert path == Path.home() / ".config" / "powershell" / "oasr_completion.ps1"

    def test_invalid_shell_returns_none(self):
        """Test invalid shell returns None."""
        path = completion.get_completion_path("invalid", system=False)
        assert path is None


class TestIsAlreadyInstalled:
    """Tests for is_already_installed()."""

    def test_not_installed_when_file_missing(self, tmp_path):
        """Test returns False when file doesn't exist."""
        with mock.patch(
            "commands.completion.get_completion_path",
            return_value=tmp_path / "nonexistent",
        ):
            assert completion.is_already_installed("bash") is False

    def test_not_installed_when_signature_missing(self, tmp_path):
        """Test returns False when file exists but no signature."""
        comp_file = tmp_path / "oasr"
        comp_file.write_text("# some other completion")

        with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
            assert completion.is_already_installed("bash") is False

    def test_installed_when_signature_present(self, tmp_path):
        """Test returns True when signature is present."""
        comp_file = tmp_path / "oasr"
        comp_file.write_text("# oasr completion script\ncomplete -F _oasr oasr")

        with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
            assert completion.is_already_installed("bash") is True


class TestGetCompletionScript:
    """Tests for get_completion_script()."""

    def test_bash_script_returned(self):
        """Test bash script is returned."""
        script = completion.get_completion_script("bash")
        assert "bash" in script.lower()

    def test_zsh_script_returned(self):
        """Test zsh script is returned."""
        script = completion.get_completion_script("zsh")
        assert "zsh" in script.lower()

    def test_fish_script_returned(self):
        """Test fish script is returned."""
        script = completion.get_completion_script("fish")
        assert "fish" in script.lower()

    def test_powershell_script_returned(self):
        """Test PowerShell script is returned."""
        script = completion.get_completion_script("powershell")
        assert "powershell" in script.lower()

    def test_invalid_shell_returns_empty(self):
        """Test invalid shell returns empty string."""
        script = completion.get_completion_script("invalid")
        assert script == ""


class MockArgs:
    """Mock arguments for testing."""

    def __init__(self, **kwargs):
        self.shell = kwargs.get("shell")
        self.force = kwargs.get("force", False)
        self.dry_run = kwargs.get("dry_run", False)


class TestRunOutput:
    """Tests for run_output()."""

    def test_output_script_to_stdout(self, capsys):
        """Test script is output to stdout."""
        completion.run_output("bash")
        captured = capsys.readouterr()
        assert "bash" in captured.out.lower()


class TestRunInstall:
    """Tests for run_install()."""

    def test_install_respects_config_disabled(self, tmp_path):
        """Test installation respects config setting."""
        args = MockArgs(shell="bash")

        with mock.patch("commands.completion.load_config", return_value={"oasr": {"completions": False}}):
            result = completion.run_install(args)
            assert result == 1

    def test_install_skips_if_already_installed(self, tmp_path):
        """Test installation is skipped if already installed."""
        args = MockArgs(shell="bash")
        comp_file = tmp_path / "oasr"
        comp_file.write_text("# oasr completion\ncomplete -F _oasr oasr")

        with mock.patch("commands.completion.load_config", return_value={}):
            with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
                result = completion.run_install(args)
                assert result == 0

    def test_install_with_force_reinstalls(self, tmp_path):
        """Test --force reinstalls even if already installed."""
        args = MockArgs(shell="bash", force=True)
        comp_file = tmp_path / "oasr"
        comp_file.parent.mkdir(parents=True, exist_ok=True)
        comp_file.write_text("# oasr completion\ncomplete -F _oasr oasr")

        with mock.patch("commands.completion.load_config", return_value={}):
            with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
                result = completion.run_install(args)
                assert result == 0

    def test_install_dry_run_shows_preview(self, tmp_path, capsys):
        """Test --dry-run shows preview without installing."""
        args = MockArgs(shell="bash", dry_run=True)
        comp_file = tmp_path / "oasr"

        with mock.patch("commands.completion.load_config", return_value={}):
            with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
                result = completion.run_install(args)
                assert result == 0
                assert not comp_file.exists()

                captured = capsys.readouterr()
                assert "Would install" in captured.out


class TestRunUninstall:
    """Tests for run_uninstall()."""

    def test_uninstall_removes_file(self, tmp_path):
        """Test uninstall removes completion file."""
        args = MockArgs(shell="bash")
        comp_file = tmp_path / "oasr"
        comp_file.write_text("# oasr completion")

        with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
            result = completion.run_uninstall(args)
            assert result == 0
            assert not comp_file.exists()

    def test_uninstall_handles_missing_file(self, tmp_path):
        """Test uninstall handles missing file gracefully."""
        args = MockArgs(shell="bash")
        comp_file = tmp_path / "nonexistent"

        with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
            result = completion.run_uninstall(args)
            assert result == 0

    def test_uninstall_dry_run_shows_preview(self, tmp_path, capsys):
        """Test --dry-run shows preview without removing."""
        args = MockArgs(shell="bash", dry_run=True)
        comp_file = tmp_path / "oasr"
        comp_file.write_text("# oasr completion")

        with mock.patch("commands.completion.get_completion_path", return_value=comp_file):
            result = completion.run_uninstall(args)
            assert result == 0
            assert comp_file.exists()

            captured = capsys.readouterr()
            assert "Would remove" in captured.out
