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


class TestLSCommandScreening:
    """Test cases for ls command screening functionality."""

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_by_sector(self, mock_api):
        """Test ls command with --sector=value for screening."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "sector": "Technology"},
            {
                "symbol": "MSFT",
                "companyName": "Microsoft Corporation",
                "sector": "Technology",
            },
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
                main, ["--config", config_path, "ls", "--sector=Technology"]
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            assert "MSFT" in result.output
            # Verify screener_api was called with correct sector
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["sector"] == "Technology"

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_by_multiple_sectors(self, mock_api):
        """Test ls command with --sector with multiple values."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "sector": "Technology"},
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
                main, ["--config", config_path, "ls", "--sector=Technology,Healthcare"]
            )

            assert result.exit_code == 0
            # Should call screener_api twice (once per sector)
            assert mock_api.call_count == 2

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_by_industry(self, mock_api):
        """Test ls command with --industry=value for screening."""
        # Mock API response
        mock_api.return_value = [
            {
                "symbol": "MSFT",
                "companyName": "Microsoft Corporation",
                "industry": "Software",
            },
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
                main, ["--config", config_path, "ls", "--industry=Software"]
            )

            assert result.exit_code == 0
            assert "MSFT" in result.output
            # Verify screener_api was called with correct industry
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["industry"] == "Software"

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_with_price_greater_than(self, mock_api):
        """Test ls command with --price=>value syntax."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "price": 150.0},
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
                main, ["--config", config_path, "ls", "--price=>100"]
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            # Verify screener_api was called with priceMoreThan
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["priceMoreThan"] == 100.0

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_with_price_less_than(self, mock_api):
        """Test ls command with --price=<value syntax."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "XYZ", "companyName": "XYZ Corp", "price": 10.0},
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

            result = runner.invoke(main, ["--config", config_path, "ls", "--price=<50"])

            assert result.exit_code == 0
            assert "XYZ" in result.output
            # Verify screener_api was called with priceLowerThan
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["priceLowerThan"] == 50.0

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_with_market_cap(self, mock_api):
        """Test ls command with --market-cap filter."""
        # Mock API response
        mock_api.return_value = [
            {"symbol": "AAPL", "companyName": "Apple Inc.", "marketCap": 2000000000000},
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
                main, ["--config", config_path, "ls", "--market-cap=>1000000000000"]
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            # Verify screener_api was called with marketCapMoreThan
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["marketCapMoreThan"] == 1000000000000.0

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_combined_filters(self, mock_api):
        """Test ls command with multiple screening filters."""
        # Mock API response
        mock_api.return_value = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "sector": "Technology",
                "price": 150.0,
            },
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
                main,
                [
                    "--config",
                    config_path,
                    "ls",
                    "--sector=Technology",
                    "--price=>100",
                    "--market-cap=>1000000000",
                ],
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            # Verify screener_api was called with all filters
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["sector"] == "Technology"
            assert call_kwargs["priceMoreThan"] == 100.0
            assert call_kwargs["marketCapMoreThan"] == 1000000000.0

    @mock.patch("duk.cli.sector_list_api")
    def test_ls_sectors_flag_still_works(self, mock_api):
        """Test that --sectors without value still lists sectors."""
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
    def test_ls_industries_flag_still_works(self, mock_api):
        """Test that --industries without value still lists industries."""
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

    def test_ls_invalid_price_format(self):
        """Test that invalid price format is rejected."""
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

            result = runner.invoke(main, ["--config", config_path, "ls", "--price=100"])

            assert result.exit_code == 1
            assert "must start with > or <" in result.output

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_with_price_range(self, mock_api):
        """Test ls command with price range using multiple --price options."""
        # Mock API response
        mock_api.return_value = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "price": 75.0,
            },
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
                main, ["--config", config_path, "ls", "--price=>50", "--price=<100"]
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            # Verify screener_api was called with both bounds
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["priceMoreThan"] == 50.0
            assert call_kwargs["priceLowerThan"] == 100.0

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_with_market_cap_range(self, mock_api):
        """Test ls command with market cap range."""
        # Mock API response
        mock_api.return_value = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "marketCap": 1500000000000,
            },
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
                main,
                [
                    "--config",
                    config_path,
                    "ls",
                    "--market-cap=>1000000000000",
                    "--market-cap=<2000000000000",
                ],
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            # Verify screener_api was called with both bounds
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["marketCapMoreThan"] == 1000000000000.0
            assert call_kwargs["marketCapLowerThan"] == 2000000000000.0

    @mock.patch("duk.fmp_api.screener_api")
    def test_ls_screen_with_combined_ranges(self, mock_api):
        """Test ls command with multiple parameter ranges."""
        # Mock API response
        mock_api.return_value = [
            {
                "symbol": "AAPL",
                "companyName": "Apple Inc.",
                "sector": "Technology",
                "price": 75.0,
                "volume": 60000000,
            },
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
                main,
                [
                    "--config",
                    config_path,
                    "ls",
                    "--sector=Technology",
                    "--price=>50",
                    "--price=<100",
                    "--volume=>50000000",
                    "--volume=<100000000",
                ],
            )

            assert result.exit_code == 0
            assert "AAPL" in result.output
            # Verify screener_api was called with all filters
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args[1]
            assert call_kwargs["sector"] == "Technology"
            assert call_kwargs["priceMoreThan"] == 50.0
            assert call_kwargs["priceLowerThan"] == 100.0
            assert call_kwargs["volumeMoreThan"] == 50000000
            assert call_kwargs["volumeLowerThan"] == 100000000

    def test_ls_screen_duplicate_greater_than_error(self):
        """Test that duplicate > operators for same parameter cause error."""
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
                main, ["--config", config_path, "ls", "--price=>50", "--price=>100"]
            )

            assert result.exit_code == 1
            assert "Cannot specify multiple '>' values" in result.output

    def test_ls_screen_duplicate_less_than_error(self):
        """Test that duplicate < operators for same parameter cause error."""
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
                main, ["--config", config_path, "ls", "--price=<50", "--price=<100"]
            )

            assert result.exit_code == 1
            assert "Cannot specify multiple '<' values" in result.output

    def test_ls_summary_flag(self):
        """Test ls command with --summary flag shows only count."""
        mock_data = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
        ]

        with mock.patch("duk.cli.actively_trading_list_api") as mock_api:
            mock_api.return_value = mock_data

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")

                # Create a test config file with API key
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ls", "--summary"]
                )

                assert result.exit_code == 0
                # Should only show count, not full summary statistics
                assert "Number of results: 3" in result.output
                # Should NOT show full statistics
                assert "SUMMARY STATISTICS" not in result.output
                assert "Min:" not in result.output
                assert "Max:" not in result.output

    def test_ls_summary_with_quiet(self):
        """Test ls command with --summary and --quiet flags."""
        mock_data = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
        ]

        with mock.patch("duk.cli.actively_trading_list_api") as mock_api:
            mock_api.return_value = mock_data

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")

                # Create a test config file with API key
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ls", "--summary", "-q"]
                )

                assert result.exit_code == 0
                # Should not show count when quiet flag is set
                assert "Number of results:" not in result.output
