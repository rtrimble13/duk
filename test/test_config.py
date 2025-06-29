"""
Tests for the configuration management system.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from duk.config import (
    ConfigurationManager,
    get_config_manager,
    get_api_key,
    validate_required_keys,
)


class TestConfigurationManager:
    """Test the ConfigurationManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_manager = ConfigurationManager()

    def test_init(self):
        """Test ConfigurationManager initialization."""
        assert self.config_manager.config_data == {}
        assert self.config_manager._loaded_files == []

    def test_get_config_file_paths(self):
        """Test that configuration file paths are returned in correct priority order."""
        paths = self.config_manager._get_config_file_paths()

        assert len(paths) == 3
        assert paths[0] == Path("/usr/local/etc/tb.rc")
        assert paths[1] == Path.home() / ".tbrc"
        assert str(paths[2]).endswith("etc/tb.rc")

    def test_load_environment_variables(self):
        """Test loading API keys from environment variables."""
        # Mock config file paths to empty list so no files are loaded
        with patch.object(
            self.config_manager, "_get_config_file_paths", return_value=[]
        ):
            with patch.dict(os.environ, {"FMP_API_KEY": "test_fmp_key"}):
                self.config_manager.load_configuration()

        assert (
            self.config_manager.config_data["api_keys"]["fmp_api_key"] == "test_fmp_key"
        )

    def test_load_environment_variables_missing(self):
        """Test loading when environment variables are not set."""
        # Mock config file paths to empty list so no files are loaded
        with patch.object(
            self.config_manager, "_get_config_file_paths", return_value=[]
        ):
            with patch.dict(os.environ, {}, clear=True):
                self.config_manager.load_configuration()

        assert (
            self.config_manager.config_data.get("api_keys", {}).get("fmp_api_key")
            is None
        )

    def test_get_api_key_existing(self):
        """Test getting an existing API key."""
        self.config_manager.config_data = {"api_keys": {"test_key": "test_value"}}

        assert self.config_manager.get_api_key("test_key") == "test_value"

    def test_get_api_key_missing(self):
        """Test getting a non-existent API key."""
        assert self.config_manager.get_api_key("nonexistent_key") is None

    def test_get_api_key_no_api_keys_section(self):
        """Test getting API key when api_keys section doesn't exist."""
        self.config_manager.config_data = {}
        assert self.config_manager.get_api_key("test_key") is None

    def test_validate_required_keys_success(self):
        """Test validation when all required keys are present."""
        self.config_manager.config_data = {
            "api_keys": {"key1": "value1", "key2": "value2"}
        }

        assert self.config_manager.validate_required_keys(["key1", "key2"]) is True

    def test_validate_required_keys_missing(self):
        """Test validation when some required keys are missing."""
        self.config_manager.config_data = {"api_keys": {"key1": "value1"}}

        assert self.config_manager.validate_required_keys(["key1", "key2"]) is False

    def test_validate_required_keys_empty_config(self):
        """Test validation with empty configuration."""
        assert self.config_manager.validate_required_keys(["key1"]) is False

    def test_get_loaded_files(self):
        """Test getting list of loaded configuration files."""
        self.config_manager._loaded_files = ["/path/to/config1", "/path/to/config2"]

        loaded_files = self.config_manager.get_loaded_files()
        assert loaded_files == ["/path/to/config1", "/path/to/config2"]

        # Ensure it returns a copy, not the original list
        loaded_files.append("/path/to/config3")
        assert len(self.config_manager._loaded_files) == 2


class TestConfigurationFileLoading:
    """Test configuration file loading functionality."""

    def test_load_config_file_success(self):
        """Test successful loading of a TOML configuration file."""
        config_manager = ConfigurationManager()

        toml_content = """
[api_keys]
test_key = "test_value"
another_key = "another_value"

[settings]
log_level = "DEBUG"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()

            try:
                config_manager._load_config_file(Path(f.name))

                assert (
                    config_manager.config_data["api_keys"]["test_key"] == "test_value"
                )
                assert (
                    config_manager.config_data["api_keys"]["another_key"]
                    == "another_value"
                )
                assert config_manager.config_data["settings"]["log_level"] == "DEBUG"
                assert f.name in config_manager._loaded_files

            finally:
                os.unlink(f.name)

    def test_load_config_file_not_exists(self):
        """Test loading a configuration file that doesn't exist."""
        config_manager = ConfigurationManager()
        non_existent_file = Path("/nonexistent/path/config.toml")

        # Should not raise an exception
        config_manager._load_config_file(non_existent_file)
        assert config_manager.config_data == {}
        assert len(config_manager._loaded_files) == 0

    def test_load_configuration_priority_order(self):
        """Test that configuration files are loaded in correct priority order."""
        config_manager = ConfigurationManager()

        # Mock the _get_config_file_paths to return our test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files with different content
            system_config = Path(temp_dir) / "system.toml"
            user_config = Path(temp_dir) / "user.toml"
            project_config = Path(temp_dir) / "project.toml"

            # System config (lowest priority)
            system_config.write_text(
                """
[api_keys]
test_key = "system_value"
system_only_key = "system_only"
"""
            )

            # User config (medium priority) - should override system
            user_config.write_text(
                """
[api_keys]
test_key = "user_value"
user_only_key = "user_only"
"""
            )

            # Project config (highest priority) - should override both
            project_config.write_text(
                """
[api_keys]
test_key = "project_value"
project_only_key = "project_only"
"""
            )

            # Mock the paths method to return our test files
            test_paths = [system_config, user_config, project_config]
            with patch.object(
                config_manager, "_get_config_file_paths", return_value=test_paths
            ):
                with patch.dict(
                    os.environ, {}, clear=True
                ):  # Clear environment vars for this test
                    config_manager.load_configuration()

            # Check that project config (highest priority) won
            assert config_manager.config_data["api_keys"]["test_key"] == "project_value"

            # Check that all unique keys are present
            assert (
                config_manager.config_data["api_keys"]["system_only_key"]
                == "system_only"
            )
            assert (
                config_manager.config_data["api_keys"]["user_only_key"] == "user_only"
            )
            assert (
                config_manager.config_data["api_keys"]["project_only_key"]
                == "project_only"
            )


class TestGlobalFunctions:
    """Test global configuration functions."""

    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns the same instance."""
        # Reset the global config manager
        import duk.config

        duk.config._config_manager = None

        manager1 = get_config_manager()
        manager2 = get_config_manager()

        assert manager1 is manager2

    @patch("duk.config.get_config_manager")
    def test_get_api_key_convenience_function(self, mock_get_config_manager):
        """Test the get_api_key convenience function."""
        mock_manager = mock_get_config_manager.return_value
        mock_manager.get_api_key.return_value = "test_value"

        result = get_api_key("test_key")

        mock_manager.get_api_key.assert_called_once_with("test_key")
        assert result == "test_value"

    @patch("duk.config.get_config_manager")
    def test_validate_required_keys_convenience_function(self, mock_get_config_manager):
        """Test the validate_required_keys convenience function."""
        mock_manager = mock_get_config_manager.return_value
        mock_manager.validate_required_keys.return_value = True

        result = validate_required_keys(["key1", "key2"])

        mock_manager.validate_required_keys.assert_called_once_with(["key1", "key2"])
        assert result is True


class TestBackwardCompatibility:
    """Test backward compatibility with existing API key mechanisms."""

    def test_environment_variable_integration(self):
        """Test that environment variables work with the new system."""
        config_manager = ConfigurationManager()

        # Mock config file paths to empty list so no files are loaded
        with patch.object(
            config_manager, "_get_config_file_paths", return_value=[]
        ):
            with patch.dict(os.environ, {"FMP_API_KEY": "env_test_key"}):
                config_manager.load_configuration()

        assert config_manager.get_api_key("fmp_api_key") == "env_test_key"

    def test_file_overrides_environment(self):
        """Test that configuration file values override environment variables."""
        config_manager = ConfigurationManager()

        # Set environment variable
        with patch.dict(os.environ, {"FMP_API_KEY": "env_key"}):
            # Create a temporary config file that should override the env var
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".toml", delete=False
            ) as f:
                f.write(
                    """
[api_keys]
fmp_api_key = "file_key"
"""
                )
                f.flush()

                try:
                    # Mock the config file paths to include our test file
                    with patch.object(
                        config_manager,
                        "_get_config_file_paths",
                        return_value=[Path(f.name)],
                    ):
                        config_manager.load_configuration()

                    # File should override environment
                    assert config_manager.get_api_key("fmp_api_key") == "file_key"

                finally:
                    os.unlink(f.name)
