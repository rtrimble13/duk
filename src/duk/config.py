"""
Configuration management for duk CLI tool.

Supports multiple configuration file locations with priority order:
1. /usr/local/etc/tb.rc (system-wide, lowest priority)
2. ~/.tbrc (user-specific, medium priority)
3. duk/etc/tb.rc (project-specific, highest priority)

Configuration files use TOML format for modern standardization.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        tomllib = None

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages configuration loading from multiple sources with priority order."""

    def __init__(self):
        self.config_data: Dict[str, Any] = {}
        self._loaded_files: list = []

    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from all available sources in priority order."""
        config_files = self._get_config_file_paths()

        # Load files in priority order (lowest priority first)
        # so higher priority files can override settings
        for config_file in config_files:
            if config_file.exists():
                self._load_config_file(config_file)

        # Load environment variables last so they don't override file configs
        # This maintains backward compatibility while allowing file
        # configs to take precedence
        env_data = {}
        env_vars = {"FMP_API_KEY": "fmp_api_key"}

        for env_var, config_key in env_vars.items():
            value = os.environ.get(env_var)
            if value:
                if "api_keys" not in env_data:
                    env_data["api_keys"] = {}
                env_data["api_keys"][config_key] = value
                logger.debug(f"Found {config_key} in environment variable {env_var}")

        # Only use environment variables if not already set in config files
        for section, values in env_data.items():
            if section not in self.config_data:
                self.config_data[section] = {}
            for key, value in values.items():
                if key not in self.config_data[section]:
                    self.config_data[section][key] = value
                    logger.debug(f"Using {key} from environment variable")

        return self.config_data

    def _get_config_file_paths(self) -> list[Path]:
        """Get list of potential configuration file paths in priority order."""
        paths = [
            Path("/usr/local/etc/tb.rc"),  # System-wide (lowest priority)
            Path.home() / ".tbrc",  # User-specific (medium priority)
            Path(__file__).parents[2]
            / "etc"
            / "tb.rc",  # Project-specific (highest priority)
        ]
        return paths

    def _load_config_file(self, config_file: Path) -> None:
        """Load configuration from a single TOML file."""
        try:
            if tomllib is None:
                logger.warning(
                    f"TOML support not available. Cannot load {config_file}. "
                    "Install tomli for Python < 3.11 support."
                )
                return

            with open(config_file, "rb") as f:
                file_config = tomllib.load(f)

            # Merge configuration with proper nesting
            for section, values in file_config.items():
                if section not in self.config_data:
                    self.config_data[section] = {}

                if isinstance(values, dict):
                    self.config_data[section].update(values)
                else:
                    self.config_data[section] = values

            self._loaded_files.append(str(config_file))
            logger.debug(f"Loaded configuration from {config_file}")

        except Exception as e:
            logger.warning(f"Failed to load configuration from {config_file}: {e}")

    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key by name from configuration."""
        api_keys = self.config_data.get("api_keys", {})
        return api_keys.get(key_name)

    def validate_required_keys(self, required_keys: list[str]) -> bool:
        """Validate that all required API keys are present."""
        missing_keys = []

        for key_name in required_keys:
            if not self.get_api_key(key_name):
                missing_keys.append(key_name)

        if missing_keys:
            logger.error(f"Missing required API keys: {missing_keys}")
            logger.error("Configure API keys in one of the following locations:")
            for path in self._get_config_file_paths():
                logger.error(f"  - {path}")
            logger.error("Or set environment variables (e.g., FMP_API_KEY)")
            return False

        return True

    def get_loaded_files(self) -> list[str]:
        """Get list of configuration files that were successfully loaded."""
        return self._loaded_files.copy()


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
