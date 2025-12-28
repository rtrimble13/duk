"""
Unit tests for ph command.
"""

import os
import tempfile
from unittest import mock

import pandas as pd
from click.testing import CliRunner

from duk.cli import main


class TestPhCommand:
    """Test cases for ph command functionality."""

    def test_ph_help(self):
        """Test ph command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["ph", "--help"])

        assert result.exit_code == 0
        assert "Request price history for a symbol" in result.output
        assert "SYMBOL" in result.output

    def test_ph_missing_api_key(self):
        """Test ph command without API key configured."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")
            with open(config_path, "w") as f:
                f.write("[general]\n")
                f.write('log_level = "info"\n')

            # Ensure no API key in environment
            env = os.environ.copy()
            if "FMP_API_KEY" in env:
                del env["FMP_API_KEY"]

            result = runner.invoke(
                main, ["--config", config_path, "ph", "AAPL"], env=env
            )

            assert result.exit_code == 1
            assert "FMP API key not configured" in result.output

    def test_ph_basic_usage(self):
        """Test basic ph command usage."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [149.0, 150.0],
                "high": [151.0, 155.0],
                "low": [148.0, 149.0],
                "close": [150.0, 154.0],
                "volume": [900000, 1000000],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "ph", "AAPL"])

                assert result.exit_code == 0
                assert "date" in result.output
                assert "open" in result.output
                assert "high" in result.output
                assert "low" in result.output
                assert "close" in result.output
                assert "volume" in result.output

    def test_ph_with_start_and_end_date(self):
        """Test ph command with start and end dates."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        config_path,
                        "ph",
                        "AAPL",
                        "-s",
                        "2023-01-01",
                        "-e",
                        "2023-12-31",
                    ],
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["start_date"] == "2023-01-01"
                assert call_kwargs["end_date"] == "2023-12-31"

    def test_ph_with_limit(self):
        """Test ph command with limit."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "-n", "10"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["limit"] == 10

    def test_ph_with_frequency(self):
        """Test ph command with frequency option."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-09"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "-f", "week"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["frequency"] == "week"

    def test_ph_with_ohlc_filter(self):
        """Test ph command with --ohlc filter."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "open": [149.0],
                "high": [151.0],
                "low": [148.0],
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--ohlc"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["fields"] == ["open", "high", "low", "close"]

    def test_ph_with_hlc_filter(self):
        """Test ph command with --hlc filter."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "high": [151.0],
                "low": [148.0],
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--hlc"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["fields"] == ["high", "low", "close"]

    def test_ph_with_close_filter(self):
        """Test ph command with --close filter."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--close"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["fields"] == ["close"]

    def test_ph_with_hlcv_filter(self):
        """Test ph command with --hlcv filter."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "high": [151.0],
                "low": [148.0],
                "close": [150.0],
                "volume": [900000],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--hlcv"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["fields"] == ["high", "low", "close", "volume"]

    def test_ph_with_cv_filter(self):
        """Test ph command with --cv filter."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
                "volume": [900000],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--cv"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["fields"] == ["close", "volume"]

    def test_ph_multiple_field_filters_error(self):
        """Test that using multiple field filters raises an error."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ph", "AAPL", "--ohlc", "--hlc"]
            )

            assert result.exit_code == 1
            assert "Only one" in result.output

    def test_ph_quiet_mode(self):
        """Test ph command with --quiet flag."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "-q"]
                )

                assert result.exit_code == 0
                # Output should not contain data
                assert "Date" not in result.output
                assert "Close" not in result.output

    def test_ph_output_to_file(self):
        """Test ph command with --output to write to file."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                output_file = os.path.join(tmpdir, "output.csv")
                result = runner.invoke(
                    main,
                    ["--config", config_path, "ph", "AAPL", "-o", output_file],
                )

                assert result.exit_code == 0
                assert os.path.exists(output_file)
                assert f"Data written to {output_file}" in result.output

                # Verify file contents
                with open(output_file, "r") as f:
                    contents = f.read()
                    assert "date" in contents
                    assert "close" in contents
                    assert "2023-01-02" in contents
                    assert "2023-01-03" in contents

    def test_ph_output_to_directory(self):
        """Test ph command with --output pointing to directory."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                output_dir = os.path.join(tmpdir, "output_dir")
                os.makedirs(output_dir)

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        config_path,
                        "ph",
                        "AAPL",
                        "-s",
                        "2023-01-01",
                        "-e",
                        "2023-12-31",
                        "-o",
                        output_dir,
                    ],
                )

                assert result.exit_code == 0
                expected_file = os.path.join(
                    output_dir, "AAPL_2023-01-01_2023-12-31.csv"
                )
                assert os.path.exists(expected_file)

    def test_ph_case_insensitive_symbol(self):
        """Test that symbol is case-insensitive."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "ph", "aapl"])

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["symbol"] == "AAPL"

    def test_ph_empty_data(self):
        """Test ph command when no data is returned."""
        mock_df = pd.DataFrame()

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "ph", "INVALID"])

                assert result.exit_code == 0
                assert "No data found" in result.output

    def test_ph_api_error(self):
        """Test ph command when API raises an error."""
        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.side_effect = Exception("API connection error")

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "ph", "AAPL"])

                assert result.exit_code == 1
                assert "Failed to fetch price history" in result.output

    def test_ph_verbose_mode(self):
        """Test ph command with --verbose flag."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "-v"]
                )

                assert result.exit_code == 0
                # Verbose mode should include debug logging
                # This depends on logging configuration but should not fail

    def test_ph_with_api_key_from_environment(self):
        """Test ph command with API key from environment variable."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            env = {"FMP_API_KEY": "env_test_key"}

            result = runner.invoke(main, ["ph", "AAPL"], env=env)

            assert result.exit_code == 0
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["api_key"] == "env_test_key"

    def test_ph_csv_output_format(self):
        """Test ph command with --csv flag for CSV output."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--csv"]
                )

                assert result.exit_code == 0
                # Check for CSV format in output
                assert "date" in result.output
                assert "close" in result.output
                assert "2023-01-02" in result.output
                assert "2023-01-03" in result.output

    def test_ph_json_output_format(self):
        """Test ph command with --json flag for JSON output."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--json"]
                )

                assert result.exit_code == 0
                # Check for JSON format in output
                assert "[" in result.output
                assert "{" in result.output
                assert "date" in result.output
                assert "close" in result.output

    def test_ph_csv_and_json_mutually_exclusive(self):
        """Test that --csv and --json cannot be used together."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')

            result = runner.invoke(
                main, ["--config", config_path, "ph", "AAPL", "--csv", "--json"]
            )

            assert result.exit_code == 1
            assert "Only one of --csv or --json can be specified" in result.output

    def test_ph_json_output_to_file(self):
        """Test ph command with --json and --output to write JSON to file."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [150.0, 154.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                output_file = os.path.join(tmpdir, "output.json")
                result = runner.invoke(
                    main,
                    [
                        "--config",
                        config_path,
                        "ph",
                        "AAPL",
                        "--json",
                        "-o",
                        output_file,
                    ],
                )

                assert result.exit_code == 0
                assert os.path.exists(output_file)
                assert f"Data written to {output_file}" in result.output

                # Verify file contents
                with open(output_file, "r") as f:
                    import json

                    data = json.load(f)
                    assert isinstance(data, list)
                    assert len(data) == 2
                    assert "date" in data[0]
                    assert "close" in data[0]

    def test_ph_json_output_to_directory(self):
        """Test ph command with --json writing to directory."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                output_dir = os.path.join(tmpdir, "output_dir")
                os.makedirs(output_dir)

                result = runner.invoke(
                    main,
                    [
                        "--config",
                        config_path,
                        "ph",
                        "AAPL",
                        "--json",
                        "-s",
                        "2023-01-01",
                        "-e",
                        "2023-12-31",
                        "-o",
                        output_dir,
                    ],
                )

                assert result.exit_code == 0
                expected_file = os.path.join(
                    output_dir, "AAPL_2023-01-01_2023-12-31.json"
                )
                assert os.path.exists(expected_file)

    def test_ph_default_csv_output(self):
        """Test that CSV is the default output format."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "ph", "AAPL"])

                assert result.exit_code == 0
                # Default should be CSV format
                assert "date,close" in result.output
                assert "2023-01-02" in result.output

    def test_ph_with_adj_flag(self):
        """Test ph command with --adj flag for adjusted price history."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [149.0, 150.0],
                "high": [151.0, 155.0],
                "low": [148.0, 149.0],
                "close": [150.0, 154.0],
                "volume": [900000, 1000000],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--adj"]
                )

                assert result.exit_code == 0
                # Verify get_price_history was called with adjusted=True
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["adjusted"] is True

    def test_ph_without_adj_flag(self):
        """Test ph command without --adj flag defaults to non-adjusted prices."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02"]),
                "close": [150.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "ph", "AAPL"])

                assert result.exit_code == 0
                # Verify get_price_history was called with adjusted=False (default)
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["adjusted"] is False

    def test_ph_summary_flag(self):
        """Test ph command with --summary flag."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                "close": [100.0, 110.0, 105.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--summary"]
                )

                assert result.exit_code == 0
                # Output should contain summary statistics
                assert "SUMMARY STATISTICS" in result.output
                assert "Number of observations:" in result.output
                assert "Date range:" in result.output
                assert "close:" in result.output
                assert "Min:" in result.output
                assert "Max:" in result.output
                assert "Mean:" in result.output
                assert "Median:" in result.output
                # Should not contain raw data
                assert "date,close" not in result.output

    def test_ph_summary_with_quiet(self):
        """Test ph command with --summary and --quiet flags."""
        mock_df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                "close": [100.0, 110.0],
            }
        )
        mock_df = mock_df.set_index("date")

        with mock.patch("duk.cli.get_price_history") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "ph", "AAPL", "--summary", "-q"]
                )

                assert result.exit_code == 0
                # Output should not contain summary statistics when quiet flag is set
                assert "SUMMARY STATISTICS" not in result.output
                assert "Number of observations:" not in result.output
