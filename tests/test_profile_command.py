"""Tests for profile command."""

from commands import profile as profile_cmd
from config import load_config, save_config


class MockArgs:
    """Mock argparse.Namespace for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_profile_sets_default(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
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
    save_config(config, config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)
    monkeypatch.setattr(profile_cmd.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(profile_cmd.sys.stdin, "isatty", lambda: True)

    args = MockArgs(args=["dev"])
    result = profile_cmd.run(args)

    assert result == 0
    captured = capsys.readouterr()
    assert "Default profile set to: dev" in captured.out

    loaded = load_config(config_path)
    assert loaded["oasr"]["default_profile"] == "dev"


def test_profile_non_interactive_lists_profiles(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
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
            }
        },
    }
    save_config(config, config_path)
    monkeypatch.setattr(profile_cmd, "CONFIG_FILE", config_path)

    monkeypatch.setattr(profile_cmd.sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(profile_cmd.sys.stdin, "isatty", lambda: False)
    args = MockArgs(args=[])
    result = profile_cmd.run(args)

    assert result == 0
    captured = capsys.readouterr()
    assert "Profiles:" in captured.out
