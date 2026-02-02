"""Tests for environment variable configuration support."""

import os
from unittest.mock import patch

import pytest

from config.env import (
    ENV_VAR_MAP,
    get_config_source,
    load_env_config,
    merge_configs,
    parse_bool,
    parse_int,
    parse_list,
    parse_value,
)


class TestParsing:
    """Test value parsing functions."""

    def test_parse_bool_true_variants(self):
        """Test boolean parsing for true values."""
        for value in ["true", "TRUE", "True", "1", "yes", "YES", "on", "ON"]:
            assert parse_bool(value) is True

    def test_parse_bool_false_variants(self):
        """Test boolean parsing for false values."""
        for value in ["false", "FALSE", "False", "0", "no", "NO", "off", "OFF"]:
            assert parse_bool(value) is False

    def test_parse_bool_invalid(self):
        """Test boolean parsing with invalid values."""
        with pytest.raises(ValueError):
            parse_bool("invalid")
        with pytest.raises(ValueError):
            parse_bool("2")
        with pytest.raises(ValueError):
            parse_bool("")

    def test_parse_int_valid(self):
        """Test integer parsing."""
        assert parse_int("42") == 42
        assert parse_int("0") == 0
        assert parse_int("-10") == -10

    def test_parse_int_invalid(self):
        """Test integer parsing with invalid values."""
        with pytest.raises(ValueError):
            parse_int("not a number")
        with pytest.raises(ValueError):
            parse_int("3.14")

    def test_parse_list_single_item(self):
        """Test list parsing with single item."""
        assert parse_list("item") == ["item"]

    def test_parse_list_multiple_items(self):
        """Test list parsing with multiple items."""
        assert parse_list("item1,item2,item3") == ["item1", "item2", "item3"]

    def test_parse_list_with_spaces(self):
        """Test list parsing trims whitespace."""
        assert parse_list("item1 , item2 , item3") == ["item1", "item2", "item3"]

    def test_parse_list_empty_items_ignored(self):
        """Test list parsing ignores empty items."""
        assert parse_list("item1,,item3") == ["item1", "item3"]
        assert parse_list("") == []

    def test_parse_value_string(self):
        """Test parse_value with string type."""
        assert parse_value("hello", str) == "hello"

    def test_parse_value_bool(self):
        """Test parse_value with bool type."""
        assert parse_value("true", bool) is True
        assert parse_value("false", bool) is False

    def test_parse_value_int(self):
        """Test parse_value with int type."""
        assert parse_value("42", int) == 42

    def test_parse_value_list(self):
        """Test parse_value with list type."""
        assert parse_value("a,b,c", list) == ["a", "b", "c"]


class TestLoadEnvConfig:
    """Test load_env_config function."""

    def test_no_env_vars_returns_empty(self):
        """Test with no environment variables set."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_env_config()
            assert config == {}

    def test_oasr_agent_env_var(self):
        """Test OASR_AGENT environment variable."""
        with patch.dict(os.environ, {"OASR_AGENT": "copilot"}, clear=True):
            config = load_env_config()
            assert config == {"agent": {"default": "copilot"}}

    def test_oasr_profile_env_var(self):
        """Test OASR_PROFILE environment variable."""
        with patch.dict(os.environ, {"OASR_PROFILE": "dev"}, clear=True):
            config = load_env_config()
            assert config == {"oasr": {"default_profile": "dev"}}

    def test_oasr_validation_strict_env_var(self):
        """Test OASR_VALIDATION_STRICT environment variable."""
        with patch.dict(os.environ, {"OASR_VALIDATION_STRICT": "true"}, clear=True):
            config = load_env_config()
            assert config == {"validation": {"strict": True}}

    def test_oasr_validation_max_lines_env_var(self):
        """Test OASR_VALIDATION_MAX_LINES environment variable."""
        with patch.dict(os.environ, {"OASR_VALIDATION_MAX_LINES": "1000"}, clear=True):
            config = load_env_config()
            assert config == {"validation": {"reference_max_lines": 1000}}

    def test_oasr_adapter_targets_env_var(self):
        """Test OASR_ADAPTER_TARGETS environment variable."""
        with patch.dict(os.environ, {"OASR_ADAPTER_TARGETS": "cursor,windsurf"}, clear=True):
            config = load_env_config()
            assert config == {"adapter": {"default_targets": ["cursor", "windsurf"]}}

    def test_multiple_env_vars(self):
        """Test multiple environment variables at once."""
        with patch.dict(
            os.environ,
            {
                "OASR_AGENT": "codex",
                "OASR_PROFILE": "dev",
                "OASR_VALIDATION_STRICT": "true",
            },
            clear=True,
        ):
            config = load_env_config()
            assert config == {
                "agent": {"default": "codex"},
                "oasr": {"default_profile": "dev"},
                "validation": {"strict": True},
            }

    def test_invalid_bool_value_skipped(self, capsys):
        """Test invalid boolean value is skipped with warning."""
        with patch.dict(os.environ, {"OASR_VALIDATION_STRICT": "invalid"}, clear=True):
            config = load_env_config()
            assert config == {}
            captured = capsys.readouterr()
            assert "Warning" in captured.err
            assert "OASR_VALIDATION_STRICT" in captured.err

    def test_invalid_int_value_skipped(self, capsys):
        """Test invalid integer value is skipped with warning."""
        with patch.dict(os.environ, {"OASR_VALIDATION_MAX_LINES": "not_a_number"}, clear=True):
            config = load_env_config()
            assert config == {}
            captured = capsys.readouterr()
            assert "Warning" in captured.err
            assert "OASR_VALIDATION_MAX_LINES" in captured.err

    def test_unknown_env_vars_ignored(self):
        """Test unknown OASR_* variables are ignored."""
        with patch.dict(
            os.environ,
            {"OASR_UNKNOWN_VAR": "value", "OASR_AGENT": "codex"},
            clear=True,
        ):
            config = load_env_config()
            # Only known var should be loaded
            assert config == {"agent": {"default": "codex"}}


class TestMergeConfigs:
    """Test merge_configs function."""

    def test_defaults_only(self):
        """Test merge with only defaults."""
        defaults = {"agent": {"default": "codex"}}
        result = merge_configs({}, {}, {}, defaults)
        assert result == defaults

    def test_file_overrides_defaults(self):
        """Test config file overrides defaults."""
        defaults = {"agent": {"default": "codex"}}
        file_config = {"agent": {"default": "copilot"}}
        result = merge_configs({}, {}, file_config, defaults)
        assert result == {"agent": {"default": "copilot"}}

    def test_env_overrides_file(self):
        """Test environment variables override config file."""
        defaults = {"agent": {"default": "codex"}}
        file_config = {"agent": {"default": "copilot"}}
        env_config = {"agent": {"default": "claude"}}
        result = merge_configs({}, env_config, file_config, defaults)
        assert result == {"agent": {"default": "claude"}}

    def test_cli_overrides_env(self):
        """Test CLI flags override environment variables."""
        defaults = {"agent": {"default": "codex"}}
        file_config = {"agent": {"default": "copilot"}}
        env_config = {"agent": {"default": "claude"}}
        cli_overrides = {"agent": {"default": "opencode"}}
        result = merge_configs(cli_overrides, env_config, file_config, defaults)
        assert result == {"agent": {"default": "opencode"}}

    def test_partial_overrides(self):
        """Test partial overrides preserve other values."""
        defaults = {
            "agent": {"default": "codex"},
            "validation": {"strict": False, "reference_max_lines": 500},
        }
        env_config = {"validation": {"strict": True}}
        result = merge_configs({}, env_config, {}, defaults)
        assert result == {
            "agent": {"default": "codex"},
            "validation": {"strict": True, "reference_max_lines": 500},
        }

    def test_multiple_sections(self):
        """Test merge with multiple sections."""
        defaults = {
            "agent": {"default": None},
            "validation": {"strict": False},
        }
        file_config = {"agent": {"default": "codex"}}
        env_config = {"validation": {"strict": True}}
        result = merge_configs({}, env_config, file_config, defaults)
        assert result == {
            "agent": {"default": "codex"},
            "validation": {"strict": True},
        }


class TestGetConfigSource:
    """Test get_config_source function."""

    def test_source_cli_flag(self):
        """Test source detection for CLI flag."""
        cli = {"agent": {"default": "codex"}}
        source = get_config_source("agent", "default", cli, {}, {})
        assert source == "cli flag"

    def test_source_env_var(self):
        """Test source detection for environment variable."""
        env = {"agent": {"default": "codex"}}
        source = get_config_source("agent", "default", {}, env, {})
        assert source == "env var"

    def test_source_config_file(self):
        """Test source detection for config file."""
        file = {"agent": {"default": "codex"}}
        source = get_config_source("agent", "default", {}, {}, file)
        assert source == "config file"

    def test_source_default(self):
        """Test source detection for default value."""
        source = get_config_source("agent", "default", {}, {}, {})
        assert source == "default"

    def test_cli_precedence_over_env(self):
        """Test CLI takes precedence over env in source detection."""
        cli = {"agent": {"default": "codex"}}
        env = {"agent": {"default": "copilot"}}
        source = get_config_source("agent", "default", cli, env, {})
        assert source == "cli flag"

    def test_env_precedence_over_file(self):
        """Test env takes precedence over file in source detection."""
        env = {"agent": {"default": "codex"}}
        file = {"agent": {"default": "copilot"}}
        source = get_config_source("agent", "default", {}, env, file)
        assert source == "env var"


class TestEnvVarMap:
    """Test ENV_VAR_MAP completeness."""

    def test_env_var_map_has_agent(self):
        """Test ENV_VAR_MAP includes agent setting."""
        assert "OASR_AGENT" in ENV_VAR_MAP
        assert ENV_VAR_MAP["OASR_AGENT"] == ("agent", "default")

    def test_env_var_map_has_profile(self):
        """Test ENV_VAR_MAP includes profile setting."""
        assert "OASR_PROFILE" in ENV_VAR_MAP
        assert ENV_VAR_MAP["OASR_PROFILE"] == ("oasr", "default_profile")

    def test_env_var_map_has_validation_strict(self):
        """Test ENV_VAR_MAP includes validation.strict."""
        assert "OASR_VALIDATION_STRICT" in ENV_VAR_MAP
        assert ENV_VAR_MAP["OASR_VALIDATION_STRICT"] == ("validation", "strict")

    def test_env_var_map_has_validation_max_lines(self):
        """Test ENV_VAR_MAP includes validation.reference_max_lines."""
        assert "OASR_VALIDATION_MAX_LINES" in ENV_VAR_MAP
        assert ENV_VAR_MAP["OASR_VALIDATION_MAX_LINES"] == (
            "validation",
            "reference_max_lines",
        )

    def test_env_var_map_has_adapter_targets(self):
        """Test ENV_VAR_MAP includes adapter.default_targets."""
        assert "OASR_ADAPTER_TARGETS" in ENV_VAR_MAP
        assert ENV_VAR_MAP["OASR_ADAPTER_TARGETS"] == ("adapter", "default_targets")
