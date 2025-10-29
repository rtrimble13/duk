"""
Tests for the configuration management system using configistate.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

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
        # Reset the global config manager for each test
        import duk.config
        duk.config._config_manager = None
        
        self.config_manager = ConfigurationManager()

    def test_init(self):
        """Test ConfigurationManager initialization."""
        assert self.config_manager.config_path == Path.home() / ".dukrc"
        assert self.config_manager._config is None
        assert self.config_manager._loaded is False

    def test_load_configuration_no_file(self):
        """Test loading configuration when file doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            self.config_manager.load_configuration()
            assert self.config_manager._loaded is True
            assert self.config_manager._config is None

    def test_load_configuration_with_file(self):
        """Test loading configuration from existing file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[api_keys]\ntest_key = "test_value"\n')
            temp_path = f.name

        try:
            # Patch the config path to use our temp file
            with patch.object(self.config_manager, 'config_path', Path(temp_path)):
                self.config_manager.load_configuration()
                assert self.config_manager._loaded is True
                assert self.config_manager._config is not None
        finally:
            os.unlink(temp_path)

    def test_get_api_key_from_config(self):
        """Test getting API key from config file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[api_keys]\nfmp_api_key = "test_fmp_key"\n')
            temp_path = f.name

        try:
            with patch.object(self.config_manager, 'config_path', Path(temp_path)):
                key = self.config_manager.get_api_key('fmp_api_key')
                assert key == "test_fmp_key"
        finally:
            os.unlink(temp_path)

    def test_get_api_key_from_environment(self):
        """Test getting API key from environment variable."""
        # Mock config file not existing
        with patch.object(Path, 'exists', return_value=False):
            with patch.dict(os.environ, {'FMP_API_KEY': 'env_test_key'}):
                key = self.config_manager.get_api_key('fmp_api_key')
                assert key == "env_test_key"

    def test_get_api_key_file_reference(self):
        """Test getting API key from file reference using configistate's file:// feature."""
        # Create a secret file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as secret_file:
            secret_file.write("secret_from_file")
            secret_path = secret_file.name

        # Create a config file with file reference
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(f'[api_keys]\nfmp_api_key = "file://{secret_path}"\n')
            temp_path = f.name

        try:
            with patch.object(self.config_manager, 'config_path', Path(temp_path)):
                key = self.config_manager.get_api_key('fmp_api_key')
                assert key == "secret_from_file"
        finally:
            os.unlink(temp_path)
            os.unlink(secret_path)

    def test_get_api_key_missing(self):
        """Test getting a non-existent API key."""
        with patch.object(Path, 'exists', return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                key = self.config_manager.get_api_key('nonexistent_key')
                assert key is None

    def test_get_api_key_config_overrides_env(self):
        """Test that config file values override environment variables."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[api_keys]\nfmp_api_key = "config_key"\n')
            temp_path = f.name

        try:
            with patch.object(self.config_manager, 'config_path', Path(temp_path)):
                with patch.dict(os.environ, {'FMP_API_KEY': 'env_key'}):
                    key = self.config_manager.get_api_key('fmp_api_key')
                    # Config should override environment
                    assert key == "config_key"
        finally:
            os.unlink(temp_path)

    def test_validate_required_keys_success(self):
        """Test validation when all required keys are present."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[api_keys]\nkey1 = "value1"\nkey2 = "value2"\n')
            temp_path = f.name

        try:
            with patch.object(self.config_manager, 'config_path', Path(temp_path)):
                result = self.config_manager.validate_required_keys(['key1', 'key2'])
                assert result is True
        finally:
            os.unlink(temp_path)

    def test_validate_required_keys_missing(self):
        """Test validation when some required keys are missing."""
        with patch.object(Path, 'exists', return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                result = self.config_manager.validate_required_keys(['key1', 'key2'])
                assert result is False

    def test_get_loaded_files_with_config(self):
        """Test getting list of loaded configuration files."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[api_keys]\ntest_key = "test_value"\n')
            temp_path = f.name

        try:
            with patch.object(self.config_manager, 'config_path', Path(temp_path)):
                self.config_manager.load_configuration()
                loaded_files = self.config_manager.get_loaded_files()
                assert len(loaded_files) == 1
                assert loaded_files[0] == temp_path
        finally:
            os.unlink(temp_path)

    def test_get_loaded_files_no_config(self):
        """Test getting loaded files when no config exists."""
        with patch.object(Path, 'exists', return_value=False):
            self.config_manager.load_configuration()
            loaded_files = self.config_manager.get_loaded_files()
            assert loaded_files == []

    def test_load_configuration_idempotent(self):
        """Test that loading configuration multiple times doesn't reload."""
        with patch.object(Path, 'exists', return_value=False):
            self.config_manager.load_configuration()
            assert self.config_manager._loaded is True
            
            # Load again
            self.config_manager.load_configuration()
            # Should still be loaded
            assert self.config_manager._loaded is True


class TestGlobalFunctions:
    """Test global configuration functions."""

    def setup_method(self):
        """Reset global state before each test."""
        import duk.config
        duk.config._config_manager = None

    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns the same instance."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2

    def test_get_api_key_convenience_function(self):
        """Test the get_api_key convenience function."""
        with patch('duk.config.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.get_api_key.return_value = "test_value"
            mock_get_manager.return_value = mock_manager

            result = get_api_key("test_key")
            
            mock_manager.get_api_key.assert_called_once_with("test_key")
            assert result == "test_value"

    def test_validate_required_keys_convenience_function(self):
        """Test the validate_required_keys convenience function."""
        with patch('duk.config.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.validate_required_keys.return_value = True
            mock_get_manager.return_value = mock_manager

            result = validate_required_keys(["key1", "key2"])
            
            mock_manager.validate_required_keys.assert_called_once_with(["key1", "key2"])
            assert result is True


class TestBackwardCompatibility:
    """Test backward compatibility with existing API key mechanisms."""

    def setup_method(self):
        """Reset global state before each test."""
        import duk.config
        duk.config._config_manager = None

    def test_environment_variable_integration(self):
        """Test that environment variables work with the new system."""
        config_manager = ConfigurationManager()
        
        with patch.object(Path, 'exists', return_value=False):
            with patch.dict(os.environ, {'FMP_API_KEY': 'env_test_key'}):
                key = config_manager.get_api_key('fmp_api_key')
                assert key == "env_test_key"

    def test_config_file_location(self):
        """Test that config is read from ~/.dukrc."""
        config_manager = ConfigurationManager()
        assert config_manager.config_path == Path.home() / ".dukrc"


class TestConfigistateIntegration:
    """Test integration with configistate features."""

    def setup_method(self):
        """Reset global state before each test."""
        import duk.config
        duk.config._config_manager = None

    def test_file_reference_support(self):
        """Test that file:// references are automatically handled by configistate."""
        # Create a secret file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as secret_file:
            secret_file.write("my_secret_key")
            secret_path = secret_file.name

        # Create a config file with file:// reference
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(f'[api_keys]\nfmp_api_key = "file://{secret_path}"\n')
            temp_path = f.name

        try:
            config_manager = ConfigurationManager()
            with patch.object(config_manager, 'config_path', Path(temp_path)):
                key = config_manager.get_api_key('fmp_api_key')
                assert key == "my_secret_key"
        finally:
            os.unlink(temp_path)
            os.unlink(secret_path)

    def test_multiple_api_keys(self):
        """Test reading multiple API keys from config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[api_keys]\n')
            f.write('fmp_api_key = "fmp_key"\n')
            f.write('another_key = "another_value"\n')
            temp_path = f.name

        try:
            config_manager = ConfigurationManager()
            with patch.object(config_manager, 'config_path', Path(temp_path)):
                fmp_key = config_manager.get_api_key('fmp_api_key')
                another_key = config_manager.get_api_key('another_key')
                
                assert fmp_key == "fmp_key"
                assert another_key == "another_value"
        finally:
            os.unlink(temp_path)

    def test_config_error_handling(self):
        """Test that invalid TOML is handled gracefully."""
        # Create a file with invalid TOML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('this is not valid TOML [[[')
            temp_path = f.name

        try:
            config_manager = ConfigurationManager()
            with patch.object(config_manager, 'config_path', Path(temp_path)):
                # Should handle the error gracefully
                config_manager.load_configuration()
                # Should fall back to None
                assert config_manager._config is None
        finally:
            os.unlink(temp_path)
