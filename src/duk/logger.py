"""
Logging configuration for duk.

This module sets up logging to both file and console based on configuration.
"""

import logging
from pathlib import Path

from duk.config import get_config


def setup_logging(config=None):
    """
    Setup logging configuration.

    Args:
        config: Optional DukConfig instance. If None, uses global config.

    Returns:
        Logger instance
    """
    if config is None:
        config = get_config()

    # Get configuration
    log_level = getattr(logging, config.get_log_level().upper(), logging.INFO)
    log_file = config.get_log_file()
    console_logging = config.get_console_logging()

    # Create log directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger("duk")
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (if enabled)
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logger.info("Logging initialized")
    return logger


def get_logger(name=None):
    """
    Get a logger instance.

    Args:
        name: Optional logger name. If None, returns root duk logger.

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"duk.{name}")
    return logging.getLogger("duk")
