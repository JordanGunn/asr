"""Tests for update command."""

import argparse
import json
from unittest import mock

from commands import update as update_cmd


def test_check_json_no_update(capsys):
    """--check JSON output when already up to date."""
    args = argparse.Namespace(json="v1", quiet=False, yes=False, check=True)

    with mock.patch("commands.update.get_installed_version", return_value="0.6.2"):
        with mock.patch("commands.update.get_latest_pypi_version", return_value="0.6.2"):
            result = update_cmd.run(args)

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["update_available"] is False
    assert payload["updated"] is False
    assert payload["success"] is True


def test_check_console_update_available(capsys):
    """--check prints update availability to stdout."""
    args = argparse.Namespace(json=None, quiet=False, yes=False, check=True)

    with mock.patch("commands.update.get_installed_version", return_value="0.6.1"):
        with mock.patch("commands.update.get_latest_pypi_version", return_value="0.6.2"):
            result = update_cmd.run(args)

    assert result == 0
    out = capsys.readouterr().out
    assert "Update available" in out


def test_update_json_requires_yes(capsys):
    """JSON updates require --yes to proceed."""
    args = argparse.Namespace(json="v1", quiet=False, yes=False, check=False)

    with mock.patch("commands.update.get_installed_version", return_value="0.6.1"):
        with mock.patch("commands.update.get_latest_pypi_version", return_value="0.6.2"):
            result = update_cmd.run(args)

    assert result == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["success"] is False
    assert "Confirmation required" in payload["error"]
