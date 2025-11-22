"""
Unit tests for config module
"""

import os
import tempfile

from duk.config import Config


class TestConfig:
    """Test cases for Config class"""

    def test_config_loads_defaults(self):
        """Test that default configuration is loaded"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.get_fmp_api_key() == ""
            assert config.get_output_dir() == "./var"
            assert config.get_log_dir() == "./var/logs"
            assert config.get_log_level() == "INFO"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_config_loads_user_config(self):
        """Test that user configuration is loaded from file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("[api]\n")
            f.write('fmp_api_key = "test_key_123"\n')
            f.write("[output]\n")
            f.write('output_dir = "/tmp/output"\n')
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.get_fmp_api_key() == "test_key_123"
            assert config.get_output_dir() == "/tmp/output"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_config_handles_missing_file(self):
        """Test that config handles missing file gracefully"""
        config_path = "/tmp/nonexistent_config_file_12345.rc"
        config = Config(config_path)  # noqa: F841
        # Should use defaults
        assert config.get_output_dir() == "./var"

    def test_get_fallback_value(self):
        """Test that fallback values work"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            config_path = f.name

        try:
            config = Config(config_path)
            value = config.get("nonexistent", "key", "fallback_value")
            assert value == "fallback_value"
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_should_log_to_file(self):
        """Test log_to_file boolean parsing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("[logging]\n")
            f.write("log_to_file = true\n")
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.should_log_to_file() is True
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_should_log_to_stdout(self):
        """Test log_to_stdout boolean parsing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("[logging]\n")
            f.write("log_to_stdout = false\n")
            config_path = f.name

        try:
            config = Config(config_path)
            assert config.should_log_to_stdout() is False
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)
