"""
Unit tests for CLI module.
"""

import os
import tempfile
from unittest import mock

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


class TestLSCommand:
    """Test cases for ls command functionality."""

    def test_ls_help(self):
        """Test ls command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["ls", "--help"])

        assert result.exit_code == 0
        assert "List company and market information" in result.output

    def test_ls_no_api_key(self):
        """Test ls command without API key configured."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file without API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "debug"\n')

            result = runner.invoke(main, ["--config", config_path, "ls"])

            assert result.exit_code == 1
            assert "FMP API key not configured" in result.output

    @mock.patch("duk.cli.actively_trading_list_api")
    def test_ls_default_actively_trading(self, mock_api):
        """Test ls command default behavior (actively trading list)."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(main, ["--config", config_path, "ls"])

            assert result.exit_code == 0
            assert "AAPL" in result.output
            assert "MSFT" in result.output
            mock_api.assert_called_once_with("test_key")

    @mock.patch("duk.cli.sector_list_api")
    def test_ls_sectors(self, mock_api):
        """Test ls command with --sectors option."""
        # Mock API response
        mock_api.return_value = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(main, ["--config", config_path, "ls", "--sectors"])

            assert result.exit_code == 0
            assert "Technology" in result.output
            assert "Healthcare" in result.output
            mock_api.assert_called_once_with("test_key")

    @mock.patch("duk.cli.industry_list_api")
    def test_ls_industries(self, mock_api):
        """Test ls command with --industries option."""
        # Mock API response
        mock_api.return_value = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ls", "--industries"]
            )

            assert result.exit_code == 0
            assert "Software" in result.output
            assert "Pharmaceuticals" in result.output
            mock_api.assert_called_once_with("test_key")

    @mock.patch("duk.cli.actively_trading_list_api")
    def test_ls_limit(self, mock_api):
        """Test ls command with --limit option."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ls", "--limit", "2"]
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            assert "MSFT" in result.output
            # GOOGL should not be present due to limit
            assert "GOOGL" not in result.output

    @mock.patch("duk.cli.actively_trading_list_api")
    def test_ls_json_output(self, mock_api):
        """Test ls command with --json option."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "name": "Apple Inc."},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(main, ["--config", config_path, "ls", "--json"])

            assert result.exit_code == 0
            # Check for JSON format markers
            assert "[{" in result.output or '{"' in result.output

    @mock.patch("duk.cli.actively_trading_list_api")
    def test_ls_quiet(self, mock_api):
        """Test ls command with --quiet option."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "name": "Apple Inc."},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(main, ["--config", config_path, "ls", "--quiet"])

            assert result.exit_code == 0
            # Output should be empty or minimal
            assert "AAPL" not in result.output

    @mock.patch("duk.cli.actively_trading_list_api")
    def test_ls_output_file(self, mock_api):
        """Test ls command with --output option."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "name": "Apple Inc."},
        ]

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")
            output_path = os.path.join(tmpdir, "output.csv")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')
                f.write("\n")
                f.write("[general]\n")
                f.write('log_level = "error"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ls", "--output", output_path]
            )

            assert result.exit_code == 0
            assert os.path.exists(output_path)

            # Read the file and verify contents
            with open(output_path, "r") as f:
                content = f.read()
                assert "AAPL" in content

    def test_ls_mutually_exclusive_options(self):
        """Test that --sectors and --industries cannot be used together."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ls", "--sectors", "--industries"]
            )

            assert result.exit_code == 1
            assert "Only one of --sectors or --industries" in result.output

    def test_ls_mutually_exclusive_formats(self):
        """Test that --csv and --json cannot be used together."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")

            # Create a test config file with API key
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ls", "--csv", "--json"]
            )

            assert result.exit_code == 1
            assert "Only one of --csv or --json" in result.output
