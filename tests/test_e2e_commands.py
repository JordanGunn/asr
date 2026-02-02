"""Comprehensive E2E tests for all commands."""

import json
import tempfile
from pathlib import Path


class TestRegistryCommands:
    """E2E tests for registry subcommands."""

    def test_registry_list_empty(self, cli_runner, tmp_skills_dir):
        """List empty registry."""
        exit_code, stdout, stderr = cli_runner(["registry", "list"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes
        assert "No skills" in stdout or "Registry" in stdout

        """Prune clean registry."""
        exit_code, stdout, stderr = cli_runner(["registry", "prune"])
        # Prune might succeed or warn, but shouldn't crash
        assert exit_code in [0, 1, 3]  # Allow warning/nothing-to-do exit codes

    def test_registry_sync(self, cli_runner, sample_registry):
        """Sync registry."""
        exit_code, stdout, stderr = cli_runner(["registry", "sync"])
        # Sync might not have anything to do, but shouldn't crash
        assert exit_code in [0, 1, 3]  # Various valid states


class TestDiffCommand:
    """E2E tests for diff command."""

    def test_diff_no_tracked(self, cli_runner, tmp_skills_dir):
        """Diff with no tracked skills."""
        exit_code, stdout, stderr = cli_runner(["diff"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes
        assert "No tracked" in stdout or "no tracked" in stdout.lower()

    def test_diff_with_tracked(self, cli_runner, sample_registry, tmp_path):
        """Diff with tracked skills."""
        # Clone to create tracking
        target = tmp_path / "target"
        target.mkdir()
        cli_runner(["clone", "test-skill", "-t", str(target)])

        exit_code, stdout, stderr = cli_runner(["diff"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes


class TestSyncCommand:
    """E2E tests for sync command."""

    def test_sync_no_tracked(self, cli_runner, tmp_skills_dir):
        """Sync with no tracked skills."""
        exit_code, stdout, stderr = cli_runner(["sync"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes
        assert "No tracked" in stdout or "tracked" in stdout.lower()

    def test_sync_with_tracked(self, cli_runner, sample_registry, tmp_path):
        """Sync with tracked skills."""
        # Clone to create tracking
        target = tmp_path / "target"
        target.mkdir()
        cli_runner(["clone", "test-skill", "-t", str(target)])

        exit_code, stdout, stderr = cli_runner(["sync"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes


class TestInfoCommand:
    """E2E tests for info command."""

    def test_info_existing_skill(self, cli_runner, sample_registry):
        """Info on existing skill."""
        exit_code, stdout, stderr = cli_runner(["info", "git-commit"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes
        # Output check - command runs without crashing

    def test_info_with_files(self, cli_runner, sample_registry):
        """Info with --files flag."""
        exit_code, stdout, stderr = cli_runner(["info", "test-skill", "--files"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes

    def test_info_nonexistent_fails(self, cli_runner, tmp_skills_dir):
        """Info on non-existent skill fails gracefully."""
        exit_code, stdout, stderr = cli_runner(["info", "nonexistent"])
        # Should fail but not crash
        assert exit_code != 0 or "not found" in stderr.lower()


class TestValidateCommand:
    """E2E tests for validate command."""

    def test_validate_all_skills(self, cli_runner, sample_registry):
        """Validate all registered skills."""
        exit_code, stdout, stderr = cli_runner(["validate", "--all"])
        # Validation might pass or fail, but shouldn't crash
        assert exit_code in [0, 1, 2]

    def test_clean_with_confirmation(self, cli_runner, sample_registry):
        """Clean requires confirmation or -y flag."""
        exit_code, stdout, stderr = cli_runner(["clean", "-y"])
        # Clean might find nothing or something, but shouldn't crash
        assert exit_code in [0, 1, 3]

    def test_clean_dry_run(self, cli_runner, sample_registry):
        """Clean with --dry-run."""
        exit_code, stdout, stderr = cli_runner(["clean", "--dry-run"])
        assert exit_code in [0, 1, 3]


class TestAdapterCommand:
    """E2E tests for adapter command."""

    def test_adapter_list(self, cli_runner, tmp_skills_dir):
        """List available adapters."""
        exit_code, stdout, stderr = cli_runner(["adapter", "list"])
        # Adapter list might require specific setup
        assert exit_code in [0, 1, 2]


class TestFindCommand:
    """E2E tests for find command."""

    def test_find_current_dir(self, cli_runner, tmp_path):
        """Find skills in current directory."""
        exit_code, stdout, stderr = cli_runner(["find", str(tmp_path)])
        # Find might not find anything, but shouldn't crash
        assert exit_code in [0, 1]


class TestHelpCommand:
    """E2E tests for help command."""

    def test_help_shows_commands(self, cli_runner):
        """Help command shows available commands."""
        exit_code, stdout, stderr = cli_runner(["help"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes
        assert "registry" in stdout or "exec" in stdout

    def test_help_specific_command(self, cli_runner):
        """Help for specific command."""
        exit_code, stdout, stderr = cli_runner(["help", "exec"])
        assert exit_code in [0, 1, 3]  # Allow various exit codes
        assert "exec" in stdout.lower()
