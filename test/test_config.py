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

    def test_config_template_exists(self):
        """Test that the config template file exists in etc/dukrc."""
        # Get the repository root (parent of src/)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(repo_root, "etc", "dukrc")
        assert os.path.exists(
            template_path
        ), f"Config template not found at {template_path}"
        assert os.path.isfile(
            template_path
        ), f"Config template is not a file: {template_path}"

    def test_user_dukrc_exists(self):
        """Test that ~/.dukrc exists (if user has set it up)."""
        user_config_path = os.path.expanduser("~/.dukrc")
        # This test checks if the user config file exists
        # Note: This may not exist in CI/test environments, which is okay
        if os.path.exists(user_config_path):
            # If it exists, verify it's a file
            assert os.path.isfile(
                user_config_path
            ), f"~/.dukrc exists but is not a file: {user_config_path}"
            # Verify it can be loaded as a config
            config = DukConfig(user_config_path)
            # fmt: off
            assert config.is_loaded() is True, "~/.dukrc exists but failed to load"  # noqa: E501
            # fmt: on
        # If file doesn't exist, test passes (user hasn't set up config yet)

    def test_fmp_key_from_environment_variable(self):
        """Test that FMP_API_KEY environment variable takes precedence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a config file with a key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "config_file_key"\n')

            # Set environment variable
            os.environ["FMP_API_KEY"] = "env_var_key"
            try:
                config = DukConfig(config_path)
                # Environment variable should take precedence
                assert config.fmp_key == "env_var_key"
            finally:
                # Clean up environment variable
                del os.environ["FMP_API_KEY"]

    def test_fmp_key_from_config_when_no_env_var(self):
        """Test config file used when environment variable not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a config file with a key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "config_file_key"\n')

            # Ensure environment variable is not set
            if "FMP_API_KEY" in os.environ:
                del os.environ["FMP_API_KEY"]

            config = DukConfig(config_path)
            # Config file should be used
            assert config.fmp_key == "config_file_key"

    def test_fmp_key_empty_when_no_env_var_and_no_config(self):
        """Test fmp_key returns empty when neither source has value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.conf")

            # Ensure environment variable is not set
            if "FMP_API_KEY" in os.environ:
                del os.environ["FMP_API_KEY"]

            config = DukConfig(config_path)
            # Should return empty string
            assert config.fmp_key == ""

    def test_fmp_key_from_env_var_when_config_missing(self):
        """Test environment variable works when config missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.conf")

            # Set environment variable
            os.environ["FMP_API_KEY"] = "env_only_key"
            try:
                config = DukConfig(config_path)
                # Environment variable should be used
                assert config.fmp_key == "env_only_key"
                assert config.is_loaded() is False
            finally:
                # Clean up environment variable
                del os.environ["FMP_API_KEY"]

    def test_fmp_key_empty_env_var_falls_back_to_config(self):
        """Test empty environment variable falls back to config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a config file with a key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "config_file_key"\n')

            # Set environment variable to empty string
            os.environ["FMP_API_KEY"] = ""
            try:
                config = DukConfig(config_path)
                # Empty env var should be ignored, config file used
                assert config.fmp_key == "config_file_key"
            finally:
                # Clean up environment variable
                del os.environ["FMP_API_KEY"]

    def test_fmp_key_whitespace_env_var_falls_back_to_config(self):
        """Test whitespace-only env variable falls back to config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a config file with a key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "config_file_key"\n')

            # Set environment variable to whitespace-only string
            os.environ["FMP_API_KEY"] = "   "
            try:
                config = DukConfig(config_path)
                # Whitespace-only should be ignored, config file used
                assert config.fmp_key == "config_file_key"
            finally:
                # Clean up environment variable
                del os.environ["FMP_API_KEY"]
