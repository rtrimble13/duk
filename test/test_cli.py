"""
Unit tests for CLI module.
"""

import os
import tempfile
from unittest.mock import patch

import pandas as pd
from click.testing import CliRunner

from duk.cli import main


class TestCLI:
    """Test cases for CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert (
            "duk - A CLI tool for downloading markets and financial data"
            in result.output
        )

    def test_cli_with_custom_config(self):
        """Test CLI with custom config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('default_output_dir = "/tmp/output"\n')
                f.write('default_output_type = "json"\n')
                f.write('log_level = "debug"\n')
                f.write('log_dir = "/tmp/logs"\n')

            runner = CliRunner()
            result = runner.invoke(main, ["--config", config_path, "--help"])

            # Should succeed with custom config
            assert result.exit_code == 0

    def test_cli_without_config(self):
        """Test CLI without config file (should use defaults)."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        # Should still work with defaults
        assert result.exit_code == 0

    def test_ph_command_help(self):
        """Test ph command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["ph", "--help"])

        assert result.exit_code == 0
        assert "Download security price history" in result.output
        assert "SYMBOL" in result.output

    def test_ph_command_no_api_key(self):
        """Test ph command without API key."""
        runner = CliRunner()
        result = runner.invoke(main, ["ph", "IBM"])

        # Should fail with error message about missing API key
        assert result.exit_code == 1
        assert "FMP API key not found" in result.output

    def test_ph_command_with_api_key(self):
        """Test ph command with API key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_api_key"\n')

            # Mock the get_price_history function
            with patch("duk.cli.get_price_history") as mock_get:
                # Create mock DataFrame
                mock_df = pd.DataFrame(
                    {
                        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                        "close": [150.0, 151.0],
                        "volume": [1000000, 1100000],
                    }
                )
                mock_get.return_value = mock_df

                runner = CliRunner()
                result = runner.invoke(main, ["--config", config_path, "ph", "IBM"])

                # Should succeed
                assert result.exit_code == 0
                assert "date" in result.output
                assert "close" in result.output

    def test_ph_command_with_options(self):
        """Test ph command with various options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_api_key"\n')

            # Mock the get_price_history function
            with patch("duk.cli.get_price_history") as mock_get:
                # Create mock DataFrame
                mock_df = pd.DataFrame(
                    {
                        "date": pd.to_datetime(["2024-01-01"]),
                        "close": [150.0],
                    }
                )
                mock_get.return_value = mock_df

                runner = CliRunner()
                result = runner.invoke(
                    main,
                    [
                        "--config",
                        config_path,
                        "ph",
                        "IBM",
                        "--limit",
                        "10",
                        "--fields",
                        "date,close",
                        "--output",
                        "json",
                    ],
                )

                # Should succeed
                assert result.exit_code == 0

                # Verify the function was called with correct parameters
                mock_get.assert_called_once()
                call_args = mock_get.call_args
                assert call_args[1]["symbol"] == "IBM"
                assert call_args[1]["limit"] == 10
                assert call_args[1]["fields"] == ["date", "close"]
