"""
Logging configuration for duk
"""

import logging
import os


def setup_logging(config):
    """
    Setup logging configuration

    Args:
        config: Config instance
    """
    # Get log level
    log_level_str = config.get_log_level()
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("duk")
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add file handler if enabled
    if config.should_log_to_file():
        log_dir = config.get_log_dir()
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "duk.log")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add stdout handler if enabled
    if config.should_log_to_stdout():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name=None):
    """
    Get logger instance

    Args:
        name: Logger name (default: duk)

    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger("duk")
    return logging.getLogger(f"duk.{name}")
