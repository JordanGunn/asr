"""Tests for use command deprecation shim."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from commands import use


class TestUseDeprecation:
    """Test use command deprecation."""

    @patch("commands.clone.run")
    def test_use_shows_deprecation_warning(self, mock_clone_run, capsys):
        """Use command shows deprecation warning."""
        mock_clone_run.return_value = 0

        args = MagicMock()
        args.names = ["test-skill"]
        args.output_dir = Path("/tmp")
        args.json = False
        args.quiet = False

        result = use.run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Warning: 'oasr use' is deprecated" in captured.err
        assert "Use 'oasr clone' instead" in captured.err
        assert "v0.5.0" in captured.err
        mock_clone_run.assert_called_once_with(args)

    @patch("commands.clone.run")
    def test_use_delegates_to_clone(self, mock_clone_run):
        """Use command delegates to clone."""
        mock_clone_run.return_value = 0

        args = MagicMock()
        args.names = ["test-skill"]
        args.output_dir = Path("/tmp")
        args.json = False
        args.quiet = False

        result = use.run(args)

        assert result == 0
        mock_clone_run.assert_called_once_with(args)

    @patch("commands.clone.run")
    def test_use_returns_clone_exit_code(self, mock_clone_run):
        """Use command returns clone's exit code."""
        mock_clone_run.return_value = 1

        args = MagicMock()
        args.names = ["test-skill"]
        args.output_dir = Path("/tmp")
        args.json = False
        args.quiet = False

        result = use.run(args)

        assert result == 1

    @patch("commands.clone.run")
    def test_use_quiet_suppresses_deprecation(self, mock_clone_run, capsys):
        """Use command with --quiet suppresses deprecation warning."""
        mock_clone_run.return_value = 0

        args = MagicMock()
        args.names = ["test-skill"]
        args.output_dir = Path("/tmp")
        args.json = False
        args.quiet = True

        result = use.run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "deprecated" not in captured.err.lower()

    @patch("commands.clone.run")
    def test_use_json_suppresses_deprecation(self, mock_clone_run, capsys):
        """Use command with --json suppresses deprecation warning."""
        mock_clone_run.return_value = 0

        args = MagicMock()
        args.names = ["test-skill"]
        args.output_dir = Path("/tmp")
        args.json = True
        args.quiet = False

        result = use.run(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "deprecated" not in captured.err.lower()
