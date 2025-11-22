"""
Unit tests for logging configuration module.
"""

import logging
import os
import tempfile

from duk.logging_config import get_logger, setup_logging


class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_setup_logging_default_params(self):
        """Test setup_logging with default parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            assert logger is not None
            assert logger.name == "duk"
            assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self):
        """Test setup_logging with debug level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_level="debug", log_dir=tmpdir)

            assert logger.level == logging.DEBUG

    def test_setup_logging_creates_log_file(self):
        """Test that setup_logging creates log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            logger = setup_logging(log_dir=log_dir, log_file="test.log")

            # Check that log directory was created
            assert os.path.exists(log_dir)

            # Check that log file was created
            log_file_path = os.path.join(log_dir, "test.log")
            # Write a log message to ensure file is created
            logger.info("Test message")
            assert os.path.exists(log_file_path)

    def test_setup_logging_without_console(self):
        """Test setup_logging without console output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir, console_output=False)

            # Should only have file handler
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_logging_with_console(self):
        """Test setup_logging with console output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir, console_output=True)

            # Should have both file and console handlers
            assert len(logger.handlers) == 2
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "FileHandler" in handler_types
            assert "StreamHandler" in handler_types

    def test_get_logger_default(self):
        """Test get_logger with default name."""
        logger = get_logger()
        assert logger.name == "duk"

    def test_get_logger_with_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("test_module")
        assert logger.name == "duk.test_module"

    def test_logging_levels(self):
        """Test different logging levels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test each level
            levels = ["debug", "info", "warning", "error", "critical"]
            for level in levels:
                logger = setup_logging(log_level=level, log_dir=tmpdir)
                expected_level = getattr(logging, level.upper())
                assert logger.level == expected_level
