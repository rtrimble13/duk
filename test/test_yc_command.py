"""
Unit tests for yc command.
"""

import json
import os
import tempfile
from datetime import date
from unittest import mock

import pandas as pd
from click.testing import CliRunner

from duk.cli import main


class TestYcCommand:
    """Test cases for yc command functionality."""

    def test_yc_help(self):
        """Test yc command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["yc", "--help"])

        assert result.exit_code == 0
        assert "Request yield curve data" in result.output
        assert "--zero-rates" in result.output
        assert "--tenors" in result.output
        assert "--key-rates" in result.output
        assert "--interval" in result.output

    def test_yc_missing_api_key(self):
        """Test yc command without API key configured."""
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

            result = runner.invoke(main, ["--config", config_path, "yc"], env=env)

            assert result.exit_code == 1
            assert "FMP API key not configured" in result.output

    def test_yc_basic_usage(self):
        """Test basic yc command usage."""
        # Create mock DataFrame with multi-date format (date index, tenor columns)
        mock_df = pd.DataFrame(
            {
                "month1": [4.35, 4.40],
                "year1": [4.68, 4.72],
                "year10": [3.79, 3.82],
            },
            index=pd.to_datetime(["2023-06-01", "2023-06-02"]).date,
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc"])

                assert result.exit_code == 0
                assert "month1" in result.output
                assert "year1" in result.output
                assert "year10" in result.output

    def test_yc_with_start_and_end_date(self):
        """Test yc command with start and end dates."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
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
                        "yc",
                        "-s",
                        "2023-06-01",
                        "-e",
                        "2023-06-30",
                    ],
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["start_date"] == "2023-06-01"
                assert call_kwargs["end_date"] == "2023-06-30"

    def test_yc_with_limit(self):
        """Test yc command with limit."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "yc", "-n", "10"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["limit"] == 10

    def test_yc_with_zero_rates_flag(self):
        """Test yc command with --zero-rates flag."""
        # Single date format with zero_rate column
        mock_df = pd.DataFrame(
            {
                "years": [0.083, 1.0, 10.0],
                "date": [date(2023, 7, 1), date(2024, 6, 1), date(2033, 6, 1)],
                "zero_rate": [4.35, 4.68, 3.79],
            },
            index=["month1", "year1", "year10"],
        )
        mock_df.index.name = "tenor"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc", "-z"])

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["zero_rates"] is True

    def test_yc_with_tenors_option(self):
        """Test yc command with --tenors option."""
        mock_df = pd.DataFrame(
            {
                "month6": [4.50],
                "year1": [4.68],
                "year10": [3.79],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "yc", "--tenors", "month6, year10"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["tenors"] == ("month6", "year10")

    def test_yc_with_key_rates_flag(self):
        """Test yc command with --key-rates flag."""
        mock_df = pd.DataFrame(
            {
                "year1": [4.68],
                "year5": [4.10],
                "year10": [3.79],
                "year20": [4.00],
                "year30": [3.90],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "yc", "--key-rates"]
                )

                assert result.exit_code == 0
                # Should pass tenors for year1 to year30 range
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["tenors"] == ("year1", "year30")

    def test_yc_tenors_and_key_rates_mutually_exclusive(self):
        """Test that --tenors and --key-rates cannot be used together."""
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
                    "yc",
                    "--tenors",
                    "month6, year10",
                    "--key-rates",
                ],
            )

            assert result.exit_code == 1
            assert "Cannot use both --tenors and --key-rates" in result.output

    def test_yc_with_interval(self):
        """Test yc command with --interval option."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "month6": [4.50],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "yc", "-i", "quarter"]
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["interval"] == "quarter"

    def test_yc_quiet_mode(self):
        """Test yc command with --quiet flag."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc", "-q"])

                assert result.exit_code == 0
                # Output should not contain data
                assert "month1" not in result.output
                assert "year1" not in result.output

    def test_yc_output_to_file(self):
        """Test yc command with --output to write to file."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35, 4.40],
                "year1": [4.68, 4.72],
            },
            index=[date(2023, 6, 1), date(2023, 6, 2)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                output_file = os.path.join(tmpdir, "output.csv")
                result = runner.invoke(
                    main, ["--config", config_path, "yc", "-o", output_file]
                )

                assert result.exit_code == 0
                assert os.path.exists(output_file)
                assert f"Data written to {output_file}" in result.output

                # Verify file contents
                with open(output_file, "r") as f:
                    contents = f.read()
                    assert "month1" in contents
                    assert "year1" in contents

    def test_yc_output_to_directory(self):
        """Test yc command with --output pointing to directory."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
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
                        "yc",
                        "-s",
                        "2023-06-01",
                        "-e",
                        "2023-06-30",
                        "-o",
                        output_dir,
                    ],
                )

                assert result.exit_code == 0
                expected_file = os.path.join(output_dir, "yc_2023-06-01_2023-06-30.csv")
                assert os.path.exists(expected_file)

    def test_yc_empty_data(self):
        """Test yc command when no data is returned."""
        mock_df = pd.DataFrame()

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc"])

                assert result.exit_code == 0
                assert "No yield curve data found" in result.output

    def test_yc_api_error(self):
        """Test yc command when API raises an error."""
        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.side_effect = Exception("API connection error")

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc"])

                assert result.exit_code == 1
                assert "Failed to fetch yield curve" in result.output

    def test_yc_verbose_mode(self):
        """Test yc command with --verbose flag."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc", "-v"])

                assert result.exit_code == 0

    def test_yc_with_api_key_from_environment(self):
        """Test yc command with API key from environment variable."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            env = {"FMP_API_KEY": "env_test_key"}

            result = runner.invoke(main, ["yc"], env=env)

            assert result.exit_code == 0
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["api_key"] == "env_test_key"

    def test_yc_csv_output_format(self):
        """Test yc command with --csv flag for CSV output."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35, 4.40],
                "year1": [4.68, 4.72],
            },
            index=[date(2023, 6, 1), date(2023, 6, 2)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc", "--csv"])

                assert result.exit_code == 0
                # Check for CSV format in output
                assert "month1" in result.output
                assert "year1" in result.output
                assert "4.35" in result.output

    def test_yc_json_output_format(self):
        """Test yc command with --json flag for JSON output."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35, 4.40],
                "year1": [4.68, 4.72],
            },
            index=[date(2023, 6, 1), date(2023, 6, 2)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc", "--json"])

                assert result.exit_code == 0
                # Check for JSON format in output
                assert "[" in result.output
                assert "{" in result.output
                assert "month1" in result.output
                assert "year1" in result.output

    def test_yc_csv_and_json_mutually_exclusive(self):
        """Test that --csv and --json cannot be used together."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')

            result = runner.invoke(
                main, ["--config", config_path, "yc", "--csv", "--json"]
            )

            assert result.exit_code == 1
            assert "Only one of --csv or --json can be specified" in result.output

    def test_yc_json_output_to_file(self):
        """Test yc command with --json and --output to write JSON to file."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35, 4.40],
                "year1": [4.68, 4.72],
            },
            index=[date(2023, 6, 1), date(2023, 6, 2)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
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
                        "yc",
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
                    data = json.load(f)
                    assert isinstance(data, list)
                    assert len(data) == 2
                    assert "month1" in data[0]
                    assert "year1" in data[0]

    def test_yc_json_output_to_directory(self):
        """Test yc command with --json writing to directory."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
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
                        "yc",
                        "--json",
                        "-s",
                        "2023-06-01",
                        "-e",
                        "2023-06-30",
                        "-o",
                        output_dir,
                    ],
                )

                assert result.exit_code == 0
                expected_file = os.path.join(
                    output_dir, "yc_2023-06-01_2023-06-30.json"
                )
                assert os.path.exists(expected_file)

    def test_yc_default_csv_output(self):
        """Test that CSV is the default output format."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(main, ["--config", config_path, "yc"])

                assert result.exit_code == 0
                # Default should be CSV format (comma-separated)
                assert "," in result.output
                # Should not be JSON
                assert "[{" not in result.output

    def test_yc_invalid_tenors_format(self):
        """Test yc command with invalid tenors format."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test.toml")
            with open(config_path, "w") as f:
                f.write("[api]\n")
                f.write('fmp_key = "test_key"\n')

            # Test with only one tenor value
            result = runner.invoke(
                main, ["--config", config_path, "yc", "--tenors", "month6"]
            )

            assert result.exit_code == 1
            assert "Invalid tenors format" in result.output

    def test_yc_key_rates_single_date_format(self):
        """Test yc command with --key-rates using single-date format."""
        # Single date format with tenor index
        mock_df = pd.DataFrame(
            {
                "years": [1.0, 5.0, 10.0, 20.0, 30.0],
                "date": [
                    date(2024, 6, 1),
                    date(2028, 6, 1),
                    date(2033, 6, 1),
                    date(2043, 6, 1),
                    date(2053, 6, 1),
                ],
                "par_rate": [4.68, 4.10, 3.79, 4.00, 3.90],
            },
            index=["year1", "year5", "year10", "year20", "year30"],
        )
        mock_df.index.name = "tenor"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
            mock_get.return_value = mock_df

            runner = CliRunner()
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = os.path.join(tmpdir, "test.toml")
                with open(config_path, "w") as f:
                    f.write("[api]\n")
                    f.write('fmp_key = "test_key"\n')

                result = runner.invoke(
                    main, ["--config", config_path, "yc", "--key-rates"]
                )

                assert result.exit_code == 0
                assert "year1" in result.output
                assert "year5" in result.output
                assert "year10" in result.output
                assert "year20" in result.output
                assert "year30" in result.output

    def test_yc_all_interval_choices(self):
        """Test that all interval choices are valid."""
        mock_df = pd.DataFrame(
            {
                "month1": [4.35],
                "year1": [4.68],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        valid_intervals = ["day", "week", "month", "quarter", "semi-annual", "annual"]

        for interval in valid_intervals:
            with mock.patch("duk.cli.get_yield_curve") as mock_get:
                mock_get.return_value = mock_df

                runner = CliRunner()
                with tempfile.TemporaryDirectory() as tmpdir:
                    config_path = os.path.join(tmpdir, "test.toml")
                    with open(config_path, "w") as f:
                        f.write("[api]\n")
                        f.write('fmp_key = "test_key"\n')

                    result = runner.invoke(
                        main, ["--config", config_path, "yc", "-i", interval]
                    )

                    assert result.exit_code == 0, f"Failed for interval: {interval}"
                    call_kwargs = mock_get.call_args[1]
                    assert call_kwargs["interval"] == interval

    def test_yc_combined_options(self):
        """Test yc command with multiple options combined."""
        mock_df = pd.DataFrame(
            {
                "month6": [4.50],
                "year1": [4.68],
                "year5": [4.10],
            },
            index=[date(2023, 6, 1)],
        )
        mock_df.index.name = "date"

        with mock.patch("duk.cli.get_yield_curve") as mock_get:
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
                        "yc",
                        "-s",
                        "2023-06-01",
                        "-e",
                        "2023-06-30",
                        "-z",
                        "--tenors",
                        "month6, year5",
                        "-i",
                        "quarter",
                    ],
                )

                assert result.exit_code == 0
                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args[1]
                assert call_kwargs["start_date"] == "2023-06-01"
                assert call_kwargs["end_date"] == "2023-06-30"
                assert call_kwargs["zero_rates"] is True
                assert call_kwargs["tenors"] == ("month6", "year5")
                assert call_kwargs["interval"] == "quarter"
