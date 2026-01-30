"""Tests for glob pattern support in `asr use` command."""


class TestUseGlobPatterns:
    """Tests for glob pattern matching in asr use."""

    def test_use_exact_match(self, cli_runner, sample_registry, tmp_output_dir):
        """Using exact skill name copies the skill."""
        exit_code, stdout, stderr = cli_runner(["use", "git-commit", "-d", str(tmp_output_dir)])

        assert exit_code == 0
        assert "git-commit" in stdout
        assert (tmp_output_dir / "git-commit").exists()

    def test_use_glob_wildcard_star(self, cli_runner, sample_registry, tmp_output_dir):
        """Using `git-*` pattern matches git-commit and git-review."""
        exit_code, stdout, stderr = cli_runner(["use", "git-*", "-d", str(tmp_output_dir)])

        assert exit_code == 0
        assert (tmp_output_dir / "git-commit").exists()
        assert (tmp_output_dir / "git-review").exists()
        # Should not copy non-matching skills
        assert not (tmp_output_dir / "code-format").exists()

    def test_use_glob_no_match_warns(self, cli_runner, sample_registry, tmp_output_dir):
        """Pattern that matches nothing produces a warning."""
        exit_code, stdout, stderr = cli_runner(["use", "nonexistent-*", "-d", str(tmp_output_dir)])

        # Should warn but not crash
        assert "No skills matched" in stderr or "not found" in stderr.lower()

    def test_use_mixed_exact_and_glob(self, cli_runner, sample_registry, tmp_output_dir):
        """Mixing exact names and glob patterns in same call."""
        exit_code, stdout, stderr = cli_runner(["use", "code-format", "git-*", "-d", str(tmp_output_dir)])

        assert exit_code == 0
        assert (tmp_output_dir / "code-format").exists()
        assert (tmp_output_dir / "git-commit").exists()
        assert (tmp_output_dir / "git-review").exists()
