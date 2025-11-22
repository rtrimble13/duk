"""
Unit tests for configuration module.
"""

import os
import tempfile

from duk.config import DukConfig, get_config


class TestDukConfig:
    """Test cases for DukConfig class."""

    def test_config_with_nonexistent_file(self):
        """Test configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.conf")
            config = DukConfig(config_path)

            assert config.is_loaded() is False
            assert config.fmp_key == ""
            assert config.default_output_dir == "var/duk"
            assert config.default_output_type == "csv"
            assert config.log_level == "info"
            assert config.log_dir == "var/duk/log"

    def test_config_with_valid_file(self):
        """Test configuration with a valid config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key_123"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('default_output_dir = "/tmp/output"\n')
                f.write('default_output_type = "json"\n')
                f.write('log_level = "debug"\n')
                f.write('log_dir = "/tmp/logs"\n')

            config = DukConfig(config_path)

            assert config.is_loaded() is True
            assert config.fmp_key == "test_key_123"
            assert config.default_output_dir == "/tmp/output"
            assert config.default_output_type == "json"
            assert config.log_level == "debug"
            assert config.log_dir == "/tmp/logs"

    def test_config_with_partial_file(self):
        """Test configuration with partial config file (some values missing)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a partial config file
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "partial_key"\n')

            config = DukConfig(config_path)

            assert config.is_loaded() is True
            assert config.fmp_key == "partial_key"
            # These should use fallback values
            assert config.default_output_dir == "var/duk"
            assert config.default_output_type == "csv"
            assert config.log_level == "info"
            assert config.log_dir == "var/duk/log"

    def test_get_config_function(self):
        """Test the get_config factory function."""
        config = get_config()
        assert isinstance(config, DukConfig)

    def test_config_default_path(self):
        """Test that default path is ~/.dukrc."""
        config = DukConfig()
        expected_path = os.path.expanduser("~/.dukrc")
        assert config.config_path == expected_path
