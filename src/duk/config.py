"""
Configuration management for duk.

This module handles loading and managing configuration from ~/.dukrc file
using the configistate library.
"""

import os
from pathlib import Path

from configistate import Config


class DukConfig:
    """Configuration manager for duk application."""

    def __init__(self, config_path=None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to config file. Defaults to ~/.dukrc
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.dukrc")

        self.config_path = config_path
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            self.config = Config(self.config_path)
        else:
            # Use default configuration if config file doesn't exist
            self.config = self._get_default_config()

    def _get_default_config(self):
        """Get default configuration."""
        default_config = Config()

        # API defaults
        default_config.config = {
            "api": {"fmp_api_key": os.getenv("FMP_API_KEY", "")},
            "logging": {
                "log_level": "INFO",
                "log_file": str(Path.home() / ".local" / "share" / "duk" / "duk.log"),
                "console_logging": "true",
            },
            "output": {"output_dir": "./var", "default_limit": "5"},
        }

        return default_config

    def get(self, section, key, fallback=None):
        """
        Get configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key not found

        Returns:
            Configuration value or fallback
        """
        try:
            return self.config.get(f"{section}.{key}", fallback)
        except Exception:
            return fallback

    def get_fmp_api_key(self):
        """Get FMP API key."""
        return self.get("api", "fmp_api_key", os.getenv("FMP_API_KEY", ""))

    def get_log_level(self):
        """Get log level."""
        return self.get("logging", "log_level", "INFO")

    def get_log_file(self):
        """Get log file path."""
        log_dir = Path.home() / ".local" / "share" / "duk"
        default_log = str(log_dir / "duk.log")
        return self.get("logging", "log_file", default_log)

    def get_console_logging(self):
        """Get console logging flag."""
        value = self.get("logging", "console_logging", "true")
        return value.lower() in ("true", "yes", "1", "on")

    def get_output_dir(self):
        """Get output directory."""
        return self.get("output", "output_dir", "./var")

    def get_default_limit(self):
        """Get default limit for records."""
        try:
            return int(self.get("output", "default_limit", "5"))
        except ValueError:
            return 5


# Global config instance
_global_config = None


def get_config(config_path=None):
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        DukConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = DukConfig(config_path)
    return _global_config
