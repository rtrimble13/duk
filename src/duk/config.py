"""
Configuration management for duk
"""

import logging
import os

from configistate import Config as ConfigiState

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "api": {"fmp_api_key": ""},
    "output": {"output_dir": "./var"},
    "logging": {
        "log_dir": "./var/logs",
        "log_level": "INFO",
        "log_to_file": True,
        "log_to_stdout": True,
    },
}


class Config:
    """Configuration manager for duk"""

    def __init__(self, config_path=None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to config file (default: ~/.dukrc)
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.dukrc")

        self.config_path = config_path
        self.config = ConfigiState()

        # Set default configuration
        for section, values in DEFAULT_CONFIG.items():
            for key, value in values.items():
                self.config.set(f"{section}.{key}", value)

        # Load user configuration if it exists
        if os.path.exists(config_path):
            try:
                self.config.load(config_path)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        else:
            logger.info(f"Config file not found at {config_path}, using defaults")

    def get(self, section, key, fallback=None):
        """
        Get configuration value

        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key not found

        Returns:
            Configuration value
        """
        config_key = f"{section}.{key}"
        return self.config.get(config_key, fallback)

    def get_fmp_api_key(self):
        """Get FMP API key"""
        return self.get("api", "fmp_api_key", "")

    def get_output_dir(self):
        """Get output directory"""
        return self.get("output", "output_dir", "./var")

    def get_log_dir(self):
        """Get log directory"""
        return self.get("logging", "log_dir", "./var/logs")

    def get_log_level(self):
        """Get log level"""
        return self.get("logging", "log_level", "INFO")

    def should_log_to_file(self):
        """Check if logging to file is enabled"""
        value = self.get("logging", "log_to_file", True)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "yes", "1")

    def should_log_to_stdout(self):
        """Check if logging to stdout is enabled"""
        value = self.get("logging", "log_to_stdout", True)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "yes", "1")


# Global config instance
_config = None


def get_config(config_path=None):
    """
    Get global configuration instance

    Args:
        config_path: Path to config file (default: ~/.dukrc)

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
