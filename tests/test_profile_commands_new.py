"""Tests for new profile subcommands."""

from pathlib import Path

from commands import profile as profile_cmd
from config import save_config


class MockArgs:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def _write_config(path: Path) -> None:
    config = {
        "agent": {"default": "codex"},
        "validation": {"reference_max_lines": 500, "strict": False},
        "adapter": {"default_targets": ["cursor"]},
        "oasr": {"default_profile": "safe", "completions": True},
        "profiles": {
            "safe": {
                "fs_read_roots": ["./"],
                "fs_write_roots": ["./out"],
                "deny_paths": ["~/.ssh"],
                "allowed_commands": ["rg"],
                "deny_shell": True,
                "network": False,
                "allow_env": False,
            },
            "dev": {"network": True, "allow_env": True, "deny_shell": False, "fs_read_roots": ["./"]},
        },
    }
    save_config(config, path)


def test_profile_show_defaults_to_active(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    _write_config(config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)
    monkeypatch.setattr(profile_cmd.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(profile_cmd.sys.stdin, "isatty", lambda: True)

    args = MockArgs(args=["show"])
    result = profile_cmd.run(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "Profile: safe" in captured.out


def test_profile_rm_blocks_builtin(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    _write_config(config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)

    args = MockArgs(args=["rm", "safe", "-y"])
    result = profile_cmd.run(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Cannot delete built-in profile" in captured.err


def test_profile_new_normalizes_name(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    _write_config(config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)
    monkeypatch.setattr(profile_cmd, "_open_editor", lambda path, config_path=None: 0)
    monkeypatch.setattr(profile_cmd.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(profile_cmd.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(profile_cmd, "save_profile", lambda name, data: tmp_path / f"{name}.toml")

    def _load(path: Path):
        return {
            "fs_read_roots": ["./"],
            "fs_write_roots": ["./out"],
            "deny_paths": ["~/.ssh"],
            "allowed_commands": ["rg"],
            "deny_shell": True,
            "network": False,
            "allow_env": False,
        }

    monkeypatch.setattr(profile_cmd, "_load_profile_file", _load)

    args = MockArgs(args=["new", "My Profile"])
    result = profile_cmd.run(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "Normalized to: my-profile" in captured.out


def test_profile_edit_blocks_builtin(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    _write_config(config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)
    monkeypatch.setattr(profile_cmd.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(profile_cmd.sys.stdin, "isatty", lambda: True)

    args = MockArgs(args=["edit"])
    result = profile_cmd.run(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Cannot edit built-in profile" in captured.err


def test_profile_edit_missing_file(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    _write_config(config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)
    monkeypatch.setattr(profile_cmd.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(profile_cmd.sys.stdin, "isatty", lambda: True)

    args = MockArgs(args=["edit", "--select", "custom"])
    result = profile_cmd.run(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Profile 'custom' not found" in captured.err
