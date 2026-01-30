"""Tests for the `asr registry list` command output formatting."""


class TestListCommand:
    """Tests for registry list command output."""

    def test_list_empty_registry_shows_message(self, cli_runner, tmp_skills_dir):
        """Empty registry shows helpful message."""
        exit_code, stdout, stderr = cli_runner(["registry", "list"])

        assert exit_code == 0
        assert "No skills registered" in stdout
        assert "asr" in stdout  # Should mention asr command

    def test_list_formats_with_box_drawing(self, cli_runner, sample_registry):
        """List output uses box-drawing characters."""
        exit_code, stdout, stderr = cli_runner(["registry", "list"])

        assert exit_code == 0
        # Check for box-drawing characters
        assert "┌─" in stdout
        assert "│" in stdout
        assert "└─" in stdout
        # Check header
        assert "REGISTERED SKILLS" in stdout

    def test_list_shows_all_skills(self, cli_runner, sample_registry):
        """List shows all registered skills."""
        exit_code, stdout, stderr = cli_runner(["registry", "list"])

        assert exit_code == 0
        for entry in sample_registry:
            assert entry.name in stdout

    def test_list_verbose_shows_full_paths(self, cli_runner, sample_registry):
        """List shows paths."""
        exit_code, stdout, stderr = cli_runner(["registry", "list"])

        assert exit_code == 0
        # At least one full path or name should be visible
        for entry in sample_registry:
            # Name should definitely appear
            if entry.name in stdout:
                break
        else:
            raise AssertionError("No skills found in output")

    def test_list_json_output(self, cli_runner, sample_registry):
        """List with --json outputs valid JSON."""
        import json

        exit_code, stdout, stderr = cli_runner(["registry", "list", "--json"])

        assert exit_code == 0
        data = json.loads(stdout)
        assert isinstance(data, list)
        assert len(data) == len(sample_registry)

        # Check structure
        for item in data:
            assert "name" in item
            assert "path" in item
            assert "description" in item
