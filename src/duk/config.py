"""
Configuration management for duk.

This module handles loading and accessing configuration from ~/.dukrc
using the configistate library.
"""

import os
from typing import Optional

from configistate import Config


class DukConfig:
    """Configuration manager for duk application."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file. If None, uses ~/.dukrc
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.dukrc")

        self.config_path = config_path
        self._config = None

        # Load configuration if file exists
        if os.path.exists(self.config_path):
            self._config = Config(self.config_path)

    @property
    def fmp_key(self) -> str:
        """
        Get FMP API key from environment variable or config file.

        First checks for FMP_API_KEY environment variable.
        If not set, retrieves from [api] section in config file.
        """
        # Check environment variable first
        env_key = os.environ.get("FMP_API_KEY", "").strip()
        if env_key:
            return env_key

        # Fall back to config file
        if self._config is None:
            return ""
        return self._config.get("api.fmp_key", default="").strip()

    @property
    def default_output_dir(self) -> str:
        """Get default output directory from [general] section."""
        if self._config is None:
            return "var/duk"
        return self._config.get("general.default_output_dir", default="var/duk")

    @property
    def default_output_type(self) -> str:
        """Get default output type from [general] section."""
        if self._config is None:
            return "csv"
        return self._config.get("general.default_output_type", default="csv")

    @property
    def log_level(self) -> str:
        """Get log level from [general] section."""
        if self._config is None:
            return "info"
        return self._config.get("general.log_level", default="info")

    @property
    def log_dir(self) -> str:
        """Get log directory from [general] section."""
        if self._config is None:
            return "var/duk/log"
        return self._config.get("general.log_dir", default="var/duk/log")

    def is_loaded(self) -> bool:
        """Check if configuration file was successfully loaded."""
        return self._config is not None


def get_config(config_path: Optional[str] = None) -> DukConfig:
    """
    Get configuration instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        DukConfig instance
    """
    return DukConfig(config_path)
