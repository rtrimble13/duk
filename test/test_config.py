"""Tests for config module."""

import os
import tempfile

from duk.config import DukConfig, get_config


class TestDukConfig:
    """Tests for DukConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        # Use a non-existent path to force default config
        config = DukConfig(config_path="/nonexistent/path/dukrc")

        assert config.get_log_level() == "INFO"
        assert config.get_console_logging() is True
        assert config.get_default_limit() == 5
        assert config.get_output_dir() == "./var"

    def test_config_from_file(self):
        """Test loading configuration from file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("[api]\n")
            f.write('fmp_api_key = "test_key_123"\n')
            f.write("\n")
            f.write("[logging]\n")
            f.write('log_level = "DEBUG"\n')
            f.write('console_logging = "false"\n')
            f.write("\n")
            f.write("[output]\n")
            f.write('default_limit = "10"\n')
            config_path = f.name

        try:
            config = DukConfig(config_path=config_path)

            assert config.get_fmp_api_key() == "test_key_123"
            assert config.get_log_level() == "DEBUG"
            assert config.get_console_logging() is False
            assert config.get_default_limit() == 10
        finally:
            os.unlink(config_path)

    def test_get_method(self):
        """Test generic get method."""
        config = DukConfig(config_path="/nonexistent/path/dukrc")

        # Test with fallback
        value = config.get("nonexistent", "key", "fallback_value")
        assert value == "fallback_value"

    def test_get_fmp_api_key_from_env(self):
        """Test getting FMP API key from environment."""
        # Set environment variable
        os.environ["FMP_API_KEY"] = "env_test_key"

        try:
            config = DukConfig(config_path="/nonexistent/path/dukrc")
            api_key = config.get_fmp_api_key()

            # Should get from environment
            assert api_key == "env_test_key"
        finally:
            # Clean up
            if "FMP_API_KEY" in os.environ:
                del os.environ["FMP_API_KEY"]

    def test_get_log_file(self):
        """Test getting log file path."""
        config = DukConfig(config_path="/nonexistent/path/dukrc")
        log_file = config.get_log_file()

        # Should return a path
        assert log_file
        assert isinstance(log_file, str)
        assert "duk.log" in log_file


class TestGetConfig:
    """Tests for get_config function."""

    def test_singleton_behavior(self):
        """Test that get_config returns the same instance."""
        # Reset global config
        import duk.config

        duk.config._global_config = None

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2
