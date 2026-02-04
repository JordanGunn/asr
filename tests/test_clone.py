"""Tests for clone command."""

import json
from pathlib import Path


def test_clone_glob_patterns(cli_runner, sample_registry, tmp_output_dir):
    """Clone supports glob pattern matching."""
    exit_code, stdout, stderr = cli_runner(["clone", "git-*", "-d", str(tmp_output_dir)])

    assert exit_code == 0
    assert (tmp_output_dir / "git-commit").exists()
    assert (tmp_output_dir / "git-review").exists()
    assert not (tmp_output_dir / "code-format").exists()


def test_clone_no_match_warns(cli_runner, sample_registry, tmp_output_dir):
    """Clone with no matches warns but does not crash."""
    exit_code, stdout, stderr = cli_runner(["clone", "nonexistent-*", "-d", str(tmp_output_dir)])

    assert exit_code in [0, 1]
    assert "No skills matched" in stderr or "not found" in stderr.lower()


def test_clone_json_output(cli_runner, sample_registry, tmp_output_dir):
    """Clone JSON output includes copied skill info."""
    exit_code, stdout, stderr = cli_runner(["clone", "git-commit", "-d", str(tmp_output_dir), "--json"])

    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["copied"] == 1
    assert payload["skills"][0]["name"] == "git-commit"
