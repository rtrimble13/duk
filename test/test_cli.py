"""Tests for CLI module using Click."""

import pandas as pd
import pytest
from click.testing import CliRunner

from duk.cli import cli, main


class TestCliGroup:
    """Tests for main CLI group."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "CLI tool for downloading market and financial data" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "duk" in result.output


class TestPhCommand:
    """Tests for ph command."""

    def test_ph_help(self):
        """Test ph command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["ph", "--help"])
        assert result.exit_code == 0
        assert "Download security price history" in result.output

    def test_ph_successful_execution(self, mocker):
        """Test successful execution of ph command."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "close": [100.0, 101.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(cli, ["ph", "IBM"])
        assert result.exit_code == 0
        assert "2024-01-01" in result.output
        assert "100.0" in result.output

    def test_ph_with_limit(self, mocker):
        """Test ph command with limit option."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mock_get = mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(cli, ["ph", "IBM", "--limit", "10"])
        assert result.exit_code == 0

        # Verify that limit was passed
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["limit"] == 10

    def test_ph_with_date_range(self, mocker):
        """Test ph command with date range."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-15"]),
                "close": [103.0],
            }
        )

        mock_get = mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(
            cli,
            [
                "ph",
                "IBM",
                "--from-date",
                "2024-01-01",
                "--to-date",
                "2024-01-31",
            ],
        )
        assert result.exit_code == 0

        # Verify that date range was passed
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["from_date"] == "2024-01-01"
        assert call_kwargs["to_date"] == "2024-01-31"

    def test_ph_with_fields(self, mocker):
        """Test ph command with custom fields."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
                "volume": [1000000],
            }
        )

        mock_get = mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(
            cli, ["ph", "IBM", "--fields", "date", "--fields", "close"]
        )
        assert result.exit_code == 0

        # Verify that fields were passed
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["fields"] == ["date", "close"]

    def test_ph_csv_output_format(self, mocker):
        """Test ph command with CSV output format."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(cli, ["ph", "IBM", "--output-format", "csv"])
        assert result.exit_code == 0
        assert "date,close" in result.output or "date" in result.output

    def test_ph_json_output_format(self, mocker):
        """Test ph command with JSON output format."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(cli, ["ph", "IBM", "--output-format", "json"])
        assert result.exit_code == 0
        assert '"date"' in result.output or '"close"' in result.output

    def test_ph_empty_data(self, mocker):
        """Test ph command with empty data."""
        runner = CliRunner()
        mock_df = pd.DataFrame()

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(cli, ["ph", "INVALID"])
        assert result.exit_code == 1
        assert "No data found" in result.output

    def test_ph_value_error(self, mocker):
        """Test ph command with ValueError."""
        runner = CliRunner()

        mocker.patch(
            "duk.ph.get_price_history",
            side_effect=ValueError("Invalid symbol"),
        )
        result = runner.invoke(cli, ["ph", ""])
        assert result.exit_code == 1
        assert "Error:" in result.output

    def test_ph_unexpected_error(self, mocker):
        """Test ph command with unexpected error."""
        runner = CliRunner()

        mocker.patch(
            "duk.ph.get_price_history",
            side_effect=Exception("Unexpected error"),
        )
        result = runner.invoke(cli, ["ph", "IBM"])
        assert result.exit_code == 1
        assert "Unexpected error:" in result.output

    def test_ph_with_file_output_default_dir(self, mocker, tmp_path):
        """Test ph command with -o flag using default directory."""
        # Reset the global config to avoid caching issues
        import duk.config

        duk.config._global_config = None

        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)

        # Create a temporary config file with custom output dir
        config_file = tmp_path / "test_dukrc"
        config_file.write_text(
            f"""
[api]
fmp_api_key = "test_key"

[output]
output_dir = "{tmp_path}"
"""
        )

        result = runner.invoke(cli, ["--config", str(config_file), "ph", "IBM", "-o"])

        # Reset global config after test
        duk.config._global_config = None

        assert result.exit_code == 0
        assert "Output written to:" in result.output
        assert "IBM_table.txt" in result.output

        # Verify file was created
        output_file = tmp_path / "IBM_table.txt"
        assert output_file.exists()

    def test_ph_with_file_output_custom_path(self, mocker, tmp_path):
        """Test ph command with -o flag and custom path."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)

        custom_dir = tmp_path / "custom_output"
        result = runner.invoke(cli, ["ph", "IBM", "-o", str(custom_dir)])

        assert result.exit_code == 0
        assert "Output written to:" in result.output

        # Verify file was created in custom directory
        output_file = custom_dir / "IBM_table.txt"
        assert output_file.exists()

    def test_ph_with_file_output_csv_format(self, mocker, tmp_path):
        """Test ph command with file output in CSV format."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)

        result = runner.invoke(
            cli,
            ["ph", "IBM", "-o", str(tmp_path), "--output-format", "csv"],
        )

        assert result.exit_code == 0
        assert "IBM_csv.csv" in result.output

        # Verify CSV file was created
        output_file = tmp_path / "IBM_csv.csv"
        assert output_file.exists()

        # Verify it's valid CSV
        content = output_file.read_text()
        assert "date,close" in content or "date" in content

    def test_ph_without_file_output(self, mocker):
        """Test ph command without -o flag outputs to stdout only."""
        runner = CliRunner()
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("duk.ph.get_price_history", return_value=mock_df)
        result = runner.invoke(cli, ["ph", "IBM"])

        assert result.exit_code == 0
        assert "Output written to:" not in result.output
        assert "2024-01-01" in result.output


class TestMain:
    """Tests for main function."""

    def test_main_execution(self, mocker):
        """Test main function execution."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [100.0],
            }
        )

        mocker.patch("sys.argv", ["duk", "ph", "IBM"])
        mocker.patch("duk.ph.get_price_history", return_value=mock_df)

        # main() calls sys.exit() on success, so we need to catch it
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Click's CliRunner doesn't use exit codes the same way
        # so we just verify it doesn't raise other exceptions
        assert exc_info.value.code in [0, None]
