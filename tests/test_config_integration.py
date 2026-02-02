"""Integration tests for environment variable configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from config import load_config


class TestConfigIntegration:
    """Integration tests for config loading with environment variables."""

    def test_load_config_with_env_agent(self):
        """Test load_config respects OASR_AGENT environment variable."""
        with patch.dict(os.environ, {"OASR_AGENT": "copilot"}, clear=True):
            config = load_config()
            assert config["agent"]["default"] == "copilot"

    def test_load_config_with_env_profile(self):
        """Test load_config respects OASR_PROFILE environment variable."""
        with patch.dict(os.environ, {"OASR_PROFILE": "dev"}, clear=True):
            config = load_config()
            assert config["oasr"]["default_profile"] == "dev"

    def test_load_config_env_overrides_file(self):
        """Test environment variables override config file values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[agent]\ndefault = "codex"\n')
            config_path = Path(f.name)

        try:
            with patch.dict(os.environ, {"OASR_AGENT": "copilot"}, clear=True):
                config = load_config(config_path=config_path)
                assert config["agent"]["default"] == "copilot"
        finally:
            config_path.unlink()

    def test_load_config_cli_overrides_env(self):
        """Test CLI overrides take precedence over environment variables."""
        with patch.dict(os.environ, {"OASR_AGENT": "copilot"}, clear=True):
            cli_overrides = {"agent": {"default": "claude"}}
            config = load_config(cli_overrides=cli_overrides)
            assert config["agent"]["default"] == "claude"

    def test_load_config_precedence_full_chain(self):
        """Test full precedence chain: cli > env > file > default."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[agent]\ndefault = "codex"\n')
            config_path = Path(f.name)

        try:
            # File has codex, env has copilot, cli has claude
            with patch.dict(os.environ, {"OASR_AGENT": "copilot"}, clear=True):
                # Without CLI override, env should win
                config = load_config(config_path=config_path)
                assert config["agent"]["default"] == "copilot"

                # With CLI override, CLI should win
                cli_overrides = {"agent": {"default": "claude"}}
                config = load_config(
                    config_path=config_path, cli_overrides=cli_overrides
                )
                assert config["agent"]["default"] == "claude"
        finally:
            config_path.unlink()

    def test_load_config_mixed_sources(self):
        """Test loading config from multiple sources simultaneously."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[agent]\ndefault = "codex"\n')
            f.write('[validation]\nstrict = false\n')
            config_path = Path(f.name)

        try:
            with patch.dict(
                os.environ,
                {"OASR_VALIDATION_STRICT": "true", "OASR_PROFILE": "dev"},
                clear=True,
            ):
                config = load_config(config_path=config_path)
                # agent from file
                assert config["agent"]["default"] == "codex"
                # validation.strict from env (overrides file)
                assert config["validation"]["strict"] is True
                # profile from env
                assert config["oasr"]["default_profile"] == "dev"
        finally:
            config_path.unlink()

    def test_load_config_no_env_uses_file(self):
        """Test config file is used when no environment variables set."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[agent]\ndefault = "claude"\n')
            config_path = Path(f.name)

        try:
            with patch.dict(os.environ, {}, clear=True):
                config = load_config(config_path=config_path)
                assert config["agent"]["default"] == "claude"
        finally:
            config_path.unlink()

    def test_load_config_no_file_uses_env(self):
        """Test environment variables work without config file."""
        # Use non-existent path
        config_path = Path("/tmp/nonexistent_oasr_config.toml")
        assert not config_path.exists()

        with patch.dict(os.environ, {"OASR_AGENT": "opencode"}, clear=True):
            config = load_config(config_path=config_path)
            assert config["agent"]["default"] == "opencode"

    def test_load_config_multiple_env_vars(self):
        """Test multiple environment variables at once."""
        with patch.dict(
            os.environ,
            {
                "OASR_AGENT": "codex",
                "OASR_PROFILE": "dev",
                "OASR_VALIDATION_STRICT": "true",
                "OASR_VALIDATION_MAX_LINES": "1000",
                "OASR_ADAPTER_TARGETS": "cursor,windsurf",
            },
            clear=True,
        ):
            config = load_config()
            assert config["agent"]["default"] == "codex"
            assert config["oasr"]["default_profile"] == "dev"
            assert config["validation"]["strict"] is True
            assert config["validation"]["reference_max_lines"] == 1000
            assert config["adapter"]["default_targets"] == ["cursor", "windsurf"]

    def test_load_config_env_only_overrides_specified(self):
        """Test env vars only override specified keys, not entire sections."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[validation]\n')
            f.write('strict = false\n')
            f.write('reference_max_lines = 500\n')
            config_path = Path(f.name)

        try:
            with patch.dict(
                os.environ, {"OASR_VALIDATION_STRICT": "true"}, clear=True
            ):
                config = load_config(config_path=config_path)
                # strict overridden by env
                assert config["validation"]["strict"] is True
                # reference_max_lines from file
                assert config["validation"]["reference_max_lines"] == 500
        finally:
            config_path.unlink()
