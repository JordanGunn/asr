"""Tests for config subpackage."""

import tempfile
from pathlib import Path

import pytest

from config import get_default_config, load_config, save_config
from config.schema import VALID_AGENTS, validate_config


class TestConfigDefaults:
    """Test default configuration."""

    def test_default_config_structure(self):
        """Default config has all required sections."""
        config = get_default_config()
        assert "validation" in config
        assert "adapter" in config
        assert "agent" in config

    def test_default_validation_settings(self):
        """Validation defaults are correct."""
        config = get_default_config()
        assert config["validation"]["reference_max_lines"] == 500
        assert config["validation"]["strict"] is False

    def test_default_adapter_settings(self):
        """Adapter defaults are correct."""
        config = get_default_config()
        assert config["adapter"]["default_targets"] == ["cursor", "windsurf"]

    def test_default_agent_settings(self):
        """Agent defaults are correct."""
        config = get_default_config()
        assert config["agent"]["default"] is None

    def test_default_config_is_copy(self):
        """get_default_config returns independent copies."""
        config1 = get_default_config()
        config2 = get_default_config()
        config1["agent"]["default"] = "codex"
        assert config2["agent"]["default"] is None


class TestConfigValidation:
    """Test configuration validation."""

    def test_valid_agent_codex(self):
        """Codex is a valid agent."""
        config = {"agent": {"default": "codex"}}
        validate_config(config)  # Should not raise

    def test_valid_agent_copilot(self):
        """Copilot is a valid agent."""
        config = {"agent": {"default": "copilot"}}
        validate_config(config)  # Should not raise

    def test_valid_agent_claude(self):
        """Claude is a valid agent."""
        config = {"agent": {"default": "claude"}}
        validate_config(config)  # Should not raise

    def test_valid_agent_none(self):
        """None is a valid agent (no default)."""
        config = {"agent": {"default": None}}
        validate_config(config)  # Should not raise

    def test_invalid_agent(self):
        """Invalid agent raises ValueError."""
        config = {"agent": {"default": "invalid"}}
        with pytest.raises(ValueError, match="Invalid agent 'invalid'"):
            validate_config(config)

    def test_valid_reference_max_lines(self):
        """Valid reference_max_lines."""
        config = {"validation": {"reference_max_lines": 1000}}
        validate_config(config)  # Should not raise

    def test_invalid_reference_max_lines_negative(self):
        """Negative reference_max_lines raises ValueError."""
        config = {"validation": {"reference_max_lines": -1}}
        with pytest.raises(ValueError, match="must be a positive integer"):
            validate_config(config)

    def test_invalid_reference_max_lines_zero(self):
        """Zero reference_max_lines raises ValueError."""
        config = {"validation": {"reference_max_lines": 0}}
        with pytest.raises(ValueError, match="must be a positive integer"):
            validate_config(config)

    def test_invalid_reference_max_lines_string(self):
        """String reference_max_lines raises ValueError."""
        config = {"validation": {"reference_max_lines": "500"}}
        with pytest.raises(ValueError, match="must be a positive integer"):
            validate_config(config)

    def test_invalid_strict_not_bool(self):
        """Non-boolean strict raises ValueError."""
        config = {"validation": {"strict": "true"}}
        with pytest.raises(ValueError, match="must be a boolean"):
            validate_config(config)

    def test_invalid_default_targets_not_list(self):
        """Non-list default_targets raises ValueError."""
        config = {"adapter": {"default_targets": "cursor"}}
        with pytest.raises(ValueError, match="must be a list"):
            validate_config(config)


class TestConfigLoadSave:
    """Test config loading and saving."""

    def test_load_nonexistent_returns_defaults(self):
        """Loading nonexistent config returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = load_config(config_path)
            assert config["agent"]["default"] is None
            assert config["validation"]["reference_max_lines"] == 500

    def test_save_and_load_agent(self):
        """Save agent config and load it back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = get_default_config()
            config["agent"]["default"] = "codex"
            save_config(config, config_path)

            loaded = load_config(config_path)
            assert loaded["agent"]["default"] == "codex"

    def test_save_and_load_validation(self):
        """Save validation config and load it back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = get_default_config()
            config["validation"]["reference_max_lines"] = 1000
            config["validation"]["strict"] = True
            save_config(config, config_path)

            loaded = load_config(config_path)
            assert loaded["validation"]["reference_max_lines"] == 1000
            assert loaded["validation"]["strict"] is True

    def test_save_invalid_config_raises(self):
        """Saving invalid config raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = get_default_config()
            config["agent"]["default"] = "invalid"
            with pytest.raises(ValueError, match="Invalid agent"):
                save_config(config, config_path)

    def test_partial_config_merges_with_defaults(self):
        """Partial config file merges with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            # Save only agent config
            with open(config_path, "w") as f:
                f.write('[agent]\ndefault = "claude"\n')

            loaded = load_config(config_path)
            # Agent should be loaded
            assert loaded["agent"]["default"] == "claude"
            # Defaults should be present
            assert loaded["validation"]["reference_max_lines"] == 500
            assert loaded["adapter"]["default_targets"] == ["cursor", "windsurf"]

    def test_load_preserves_extra_fields(self):
        """Loading config preserves fields not in defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            with open(config_path, "w") as f:
                f.write('[agent]\ndefault = "codex"\ncustom_field = "value"\n')

            loaded = load_config(config_path)
            assert loaded["agent"]["default"] == "codex"
            assert loaded["agent"].get("custom_field") == "value"


class TestValidAgentsConstant:
    """Test VALID_AGENTS constant."""

    def test_valid_agents_contains_codex(self):
        """VALID_AGENTS includes codex."""
        assert "codex" in VALID_AGENTS

    def test_valid_agents_contains_copilot(self):
        """VALID_AGENTS includes copilot."""
        assert "copilot" in VALID_AGENTS

    def test_valid_agents_contains_claude(self):
        """VALID_AGENTS includes claude."""
        assert "claude" in VALID_AGENTS

    def test_valid_agents_contains_opencode(self):
        """VALID_AGENTS includes opencode."""
        assert "opencode" in VALID_AGENTS

    def test_valid_agents_count(self):
        """VALID_AGENTS has exactly 4 agents."""
        assert len(VALID_AGENTS) == 4


class TestConfigProfiles:
    """Test policy profile configuration support."""

    def test_default_config_has_oasr_section(self):
        """Default config includes oasr section."""
        config = get_default_config()
        assert "oasr" in config
        assert "default_profile" in config["oasr"]

    def test_default_profile_is_safe(self):
        """Default execution profile is 'safe'."""
        config = get_default_config()
        assert config["oasr"]["default_profile"] == "safe"

    def test_default_config_has_profiles_section(self):
        """Default config includes profiles section."""
        config = get_default_config()
        assert "profiles" in config
        assert isinstance(config["profiles"], dict)

    def test_safe_profile_exists_by_default(self):
        """Safe profile is defined in defaults."""
        config = get_default_config()
        assert "safe" in config["profiles"]
        safe = config["profiles"]["safe"]
        assert safe["deny_shell"] is True
        assert safe["network"] is False
        assert safe["allow_env"] is False

    def test_load_user_defined_profile(self):
        """Load user-defined custom profile from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            with open(config_path, "w") as f:
                f.write("""
[oasr]
default_profile = "dev"

[profiles.dev]
network = true
allow_env = true
deny_shell = false
allowed_commands = ["bash", "curl", "git"]
""")

            loaded = load_config(config_path)
            assert loaded["oasr"]["default_profile"] == "dev"
            assert "dev" in loaded["profiles"]
            assert loaded["profiles"]["dev"]["network"] is True
            assert loaded["profiles"]["dev"]["allow_env"] is True
            assert loaded["profiles"]["dev"]["deny_shell"] is False

    def test_user_profiles_merge_with_defaults(self):
        """User profiles are added alongside default profiles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            with open(config_path, "w") as f:
                f.write("""
[profiles.custom]
network = true
""")

            loaded = load_config(config_path)
            # Safe profile should still exist
            assert "safe" in loaded["profiles"]
            # Custom profile should be added
            assert "custom" in loaded["profiles"]

    def test_validate_invalid_default_profile(self):
        """Invalid default_profile type raises ValueError."""
        config = {"oasr": {"default_profile": 123}}
        with pytest.raises(ValueError, match="must be a string"):
            validate_config(config)

    def test_validate_invalid_profiles_not_dict(self):
        """Invalid profiles structure raises ValueError."""
        config = {"profiles": "not a dict"}
        with pytest.raises(ValueError, match="must be a table"):
            validate_config(config)

    def test_validate_invalid_profile_data_not_dict(self):
        """Invalid profile data raises ValueError."""
        config = {"profiles": {"custom": "not a dict"}}
        with pytest.raises(ValueError, match="must be a table"):
            validate_config(config)

    def test_validate_profile_fields(self):
        """Validate profile field types."""
        # Test invalid fs_read_roots
        config = {"profiles": {"custom": {"fs_read_roots": "not a list"}}}
        with pytest.raises(ValueError, match="fs_read_roots must be a list"):
            validate_config(config)

        # Test invalid deny_shell
        config = {"profiles": {"custom": {"deny_shell": "not a bool"}}}
        with pytest.raises(ValueError, match="deny_shell must be a boolean"):
            validate_config(config)

        # Test invalid network
        config = {"profiles": {"custom": {"network": "not a bool"}}}
        with pytest.raises(ValueError, match="network must be a boolean"):
            validate_config(config)

    def test_save_and_load_profiles(self):
        """Save config with profiles and load it back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config = get_default_config()
            config["oasr"]["default_profile"] = "dev"
            config["profiles"]["dev"] = {
                "network": True,
                "allow_env": True,
                "deny_shell": False,
            }
            save_config(config, config_path)

            loaded = load_config(config_path)
            assert loaded["oasr"]["default_profile"] == "dev"
            assert loaded["profiles"]["dev"]["network"] is True
