"""Tests for profile helper utilities."""

from pathlib import Path

from profiles.builtins import BUILTIN_DESCRIPTIONS, is_builtin_profile
from profiles.loader import delete_profile, get_profile_path, save_profile
from commands import profile as profile_cmd
from profiles.summary import normalize_profile_name, render_profile_template


def test_normalize_profile_name():
    assert normalize_profile_name("My Profile") == "my-profile"
    assert normalize_profile_name("  DEV__PROFILE  ") == "dev-profile"
    assert normalize_profile_name("!!!") == "profile"


def test_builtin_profiles_have_descriptions():
    assert is_builtin_profile("safe")
    assert not is_builtin_profile("custom")
    assert all(BUILTIN_DESCRIPTIONS.values())


def test_save_and_delete_profile(tmp_path):
    data = {
        "fs_read_roots": ["./"],
        "fs_write_roots": ["./out"],
        "deny_paths": ["~/.ssh"],
        "allowed_commands": ["rg"],
        "deny_shell": True,
        "network": False,
        "allow_env": False,
    }
    path = save_profile("custom", data, profile_dir=tmp_path)
    assert path == get_profile_path("custom", profile_dir=tmp_path)
    assert path.exists()

    assert delete_profile("custom", profile_dir=tmp_path) is True
    assert delete_profile("custom", profile_dir=tmp_path) is False


def test_render_profile_template_contains_keys():
    template = render_profile_template({})
    for key in [
        "fs_read_roots",
        "fs_write_roots",
        "deny_paths",
        "allowed_commands",
        "deny_shell",
        "network",
        "allow_env",
    ]:
        assert key in template


def test_build_profile_choices_includes_descriptions():
    profiles = {
        "safe": {"network": False, "allow_env": False, "deny_shell": True},
        "custom": {"network": True, "allow_env": True, "deny_shell": False},
    }
    names = ["safe", "custom"]
    choices = profile_cmd._build_profile_choices(profiles, names)
    assert choices[0].value == "safe"
    assert choices[0].description
    assert choices[1].description
