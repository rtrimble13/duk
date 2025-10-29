"""
Configuration management for duk CLI tool using configistate.

Reads configuration from a single user config file: ~/.dukrc
Configuration files use TOML format.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from configistate import Config

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages configuration loading using configistate."""

    def __init__(self):
        self.config_path = Path.home() / ".dukrc"
        self._config = None
        self._loaded = False

    def load_configuration(self):
        """Load configuration from ~/.dukrc."""
        if self._loaded:
            return

        # Create config file if it doesn't exist
        if not self.config_path.exists():
            logger.debug(f"Config file {self.config_path} does not exist")
            self._config = None
        else:
            try:
                self._config = Config(str(self.config_path))
                logger.debug(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(
                    f"Failed to load configuration from {self.config_path}: {e}"
                )
                self._config = None

        self._loaded = True

    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key by name from configuration.

        First tries to get from config file, then falls back to environment variables.
        Supports file:// references in config values.
        """
        # Ensure config is loaded
        if not self._loaded:
            self.load_configuration()

        # Try config file first
        if self._config:
            try:
                # configistate uses dot notation, e.g., "api_keys.fmp_api_key"
                key_value = self._config.get(f"api_keys.{key_name}")
                if key_value:
                    logger.debug(f"Found {key_name} in config file")
                    return key_value
            except Exception as e:
                logger.debug(f"Could not get {key_name} from config: {e}")

        # Fall back to environment variables
        env_vars = {"FMP_API_KEY": "fmp_api_key"}
        for env_var, config_key in env_vars.items():
            if config_key == key_name:
                value = os.environ.get(env_var)
                if value:
                    logger.debug(f"Found {key_name} in environment variable {env_var}")
                    return value

        return None

    def get(self, key_path: str, default=None):
        """Get a configuration value by key path.

        Args:
            key_path: Dot-separated path to the config value
                (e.g., "settings.log_level")
            default: Default value to return if key is not found

        Returns:
            The configuration value or default if not found
        """
        # Ensure config is loaded
        if not self._loaded:
            self.load_configuration()

        if self._config:
            try:
                value = self._config.get(key_path)
                return value if value is not None else default
            except Exception as e:
                logger.debug(f"Could not get {key_path} from config: {e}")

        return default

    def validate_required_keys(self, required_keys: list[str]) -> bool:
        """Validate that all required API keys are present."""
        missing_keys = []

        for key_name in required_keys:
            if not self.get_api_key(key_name):
                missing_keys.append(key_name)

        if missing_keys:
            logger.error(f"Missing required API keys: {missing_keys}")
            logger.error("Configure API keys in:")
            logger.error(f"  - {self.config_path}")
            logger.error("Or set environment variables (e.g., FMP_API_KEY)")
            return False

        return True

    def get_loaded_files(self) -> list[str]:
        """Get list of configuration files that were successfully loaded."""
        if self._config and self.config_path.exists():
            return [str(self.config_path)]
        return []


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
        _config_manager.load_configuration()
    return _config_manager


def get_api_key(key_name: str) -> Optional[str]:
    """Convenience function to get an API key."""
    return get_config_manager().get_api_key(key_name)


def validate_required_keys(required_keys: list[str]) -> bool:
    """Convenience function to validate required API keys."""
    return get_config_manager().validate_required_keys(required_keys)
