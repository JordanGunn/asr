"""Tests for the `asr help` subcommand."""

class TestHelpCommand:
    """Tests for help subcommand functionality."""

    def test_help_no_args_shows_general_help(self, cli_runner, tmp_skills_dir):
        """Running `asr help` with no args shows general help."""
        exit_code, stdout, stderr = cli_runner(["help"])
        
        assert exit_code == 0
        assert "asr" in stdout.lower()
        assert "Available commands" in stdout or "positional arguments" in stdout.lower()

    def test_help_valid_command_shows_command_help(self, cli_runner, tmp_skills_dir):
        """Running `asr help list` shows help for the list command."""
        exit_code, stdout, stderr = cli_runner(["help", "list"])
        
        assert exit_code == 0
        assert "list" in stdout.lower()
        # Should mention json flag which is common to list
        assert "--json" in stdout

    def test_help_invalid_command_returns_error(self, cli_runner, tmp_skills_dir):
        """Running `asr help bogus` returns error and shows available commands."""
        exit_code, stdout, stderr = cli_runner(["help", "nonexistent_command"])
        
        assert exit_code == 1
        assert "Unknown command" in stdout or "unknown" in stdout.lower()
        assert "Available commands" in stdout or "list" in stdout
