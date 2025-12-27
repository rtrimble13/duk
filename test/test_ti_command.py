"""
Unit tests for ti command group (technical indicators).
"""

import json
import os
import tempfile

import pandas as pd
from click.testing import CliRunner

from duk.cli import main


class TestTiCommand:
    """Test cases for ti command group."""

    def test_ti_help(self):
        """Test ti command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["ti", "--help"])

        assert result.exit_code == 0
        assert "Technical indicators" in result.output
        assert "sma" in result.output
        assert "ema" in result.output


class TestSmaCommand:
    """Test cases for sma command functionality."""

    def test_sma_help(self):
        """Test sma command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["ti", "sma", "--help"])

        assert result.exit_code == 0
        assert "Simple Moving Average" in result.output
        assert "--input" in result.output
        assert "--column" in result.output
        assert "--window" in result.output

    def test_sma_missing_input(self):
        """Test sma command without input file."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["ti", "sma", "--column", "close", "--window", "10"]
        )

        assert result.exit_code != 0
        assert "input" in result.output.lower() or "missing" in result.output.lower()

    def test_sma_missing_column(self):
        """Test sma command without column parameter."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "sma", "-i", input_file, "--window", "2"]
            )

            assert result.exit_code != 0
            assert (
                "column" in result.output.lower() or "missing" in result.output.lower()
            )

    def test_sma_missing_window(self):
        """Test sma command without window parameter."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["ti", "sma", "-i", input_file, "-c", "close"])

            assert result.exit_code != 0
            assert (
                "window" in result.output.lower() or "missing" in result.output.lower()
            )

    def test_sma_basic_calculation(self):
        """Test basic SMA calculation."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "sma", "-i", input_file, "-c", "close", "-w", "3"]
            )

            assert result.exit_code == 0
            assert "close" in result.output
            assert "close_sma_3" in result.output

    def test_sma_with_output_file_csv(self):
        """Test SMA with output to CSV file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main,
                [
                    "ti",
                    "sma",
                    "-i",
                    input_file,
                    "-c",
                    "close",
                    "-w",
                    "3",
                    "-o",
                    output_file,
                ],
            )

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            # Verify output file contents
            output_df = pd.read_csv(output_file)
            assert "close" in output_df.columns
            assert "close_sma_3" in output_df.columns
            assert len(output_df) == 4

    def test_sma_with_output_file_json(self):
        """Test SMA with output to JSON file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.json")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main,
                [
                    "ti",
                    "sma",
                    "-i",
                    input_file,
                    "-c",
                    "close",
                    "-w",
                    "3",
                    "--json",
                    "-o",
                    output_file,
                ],
            )

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            # Verify output file contents
            with open(output_file) as f:
                output_data = json.load(f)
            assert len(output_data) == 4
            assert "close" in output_data[0]
            assert "close_sma_3" in output_data[0]

    def test_sma_invalid_column(self):
        """Test SMA with non-existent column."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "sma", "-i", input_file, "-c", "price", "-w", "2"]
            )

            assert result.exit_code == 1
            assert "not found" in result.output

    def test_sma_invalid_window_zero(self):
        """Test SMA with window=0."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "sma", "-i", input_file, "-c", "close", "-w", "0"]
            )

            assert result.exit_code == 1
            assert "Window must be greater than 0" in result.output

    def test_sma_non_numeric_column(self):
        """Test SMA with non-numeric column."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "symbol": ["AAPL", "AAPL", "AAPL"],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "sma", "-i", input_file, "-c", "symbol", "-w", "2"]
            )

            assert result.exit_code == 1
            assert "numeric" in result.output.lower()

    def test_sma_with_json_input(self):
        """Test SMA with JSON input file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.json")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_json(input_file, orient="records", date_format="iso")

            result = runner.invoke(
                main, ["ti", "sma", "-i", input_file, "-c", "close", "-w", "3"]
            )

            assert result.exit_code == 0
            assert "close_sma_3" in result.output

    def test_sma_quiet_mode(self):
        """Test SMA with quiet flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main,
                [
                    "ti",
                    "sma",
                    "-i",
                    input_file,
                    "-c",
                    "close",
                    "-w",
                    "2",
                    "-o",
                    output_file,
                    "-q",
                ],
            )

            assert result.exit_code == 0
            # In quiet mode with file output, should only show file confirmation
            assert "Data written to" in result.output
            # Should not contain CSV headers (which would indicate data was printed)
            lines = result.output.strip().split("\n")
            # Filter out log lines (they start with date/timestamp or don't contain commas)
            csv_lines = [
                line for line in lines if "," in line and not line.startswith("20")
            ]
            # Should have no CSV data lines in output
            assert len(csv_lines) == 0


class TestEmaCommand:
    """Test cases for ema command functionality."""

    def test_ema_help(self):
        """Test ema command help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["ti", "ema", "--help"])

        assert result.exit_code == 0
        assert "Exponential Moving Average" in result.output
        assert "--input" in result.output
        assert "--column" in result.output
        assert "--window" in result.output

    def test_ema_missing_input(self):
        """Test ema command without input file."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["ti", "ema", "--column", "close", "--window", "10"]
        )

        assert result.exit_code != 0
        assert "input" in result.output.lower() or "missing" in result.output.lower()

    def test_ema_missing_column(self):
        """Test ema command without column parameter."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "ema", "-i", input_file, "--window", "2"]
            )

            assert result.exit_code != 0
            assert (
                "column" in result.output.lower() or "missing" in result.output.lower()
            )

    def test_ema_missing_window(self):
        """Test ema command without window parameter."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(main, ["ti", "ema", "-i", input_file, "-c", "close"])

            assert result.exit_code != 0
            assert (
                "window" in result.output.lower() or "missing" in result.output.lower()
            )

    def test_ema_basic_calculation(self):
        """Test basic EMA calculation."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "ema", "-i", input_file, "-c", "close", "-w", "3"]
            )

            assert result.exit_code == 0
            assert "close" in result.output
            assert "close_ema_3" in result.output

    def test_ema_with_output_file_csv(self):
        """Test EMA with output to CSV file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main,
                [
                    "ti",
                    "ema",
                    "-i",
                    input_file,
                    "-c",
                    "close",
                    "-w",
                    "3",
                    "-o",
                    output_file,
                ],
            )

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            # Verify output file contents
            output_df = pd.read_csv(output_file)
            assert "close" in output_df.columns
            assert "close_ema_3" in output_df.columns
            assert len(output_df) == 4

    def test_ema_with_output_file_json(self):
        """Test EMA with output to JSON file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.json")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main,
                [
                    "ti",
                    "ema",
                    "-i",
                    input_file,
                    "-c",
                    "close",
                    "-w",
                    "3",
                    "--json",
                    "-o",
                    output_file,
                ],
            )

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            # Verify output file contents
            with open(output_file) as f:
                output_data = json.load(f)
            assert len(output_data) == 4
            assert "close" in output_data[0]
            assert "close_ema_3" in output_data[0]

    def test_ema_invalid_column(self):
        """Test EMA with non-existent column."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "ema", "-i", input_file, "-c", "price", "-w", "2"]
            )

            assert result.exit_code == 1
            assert "not found" in result.output

    def test_ema_invalid_window_zero(self):
        """Test EMA with window=0."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "ema", "-i", input_file, "-c", "close", "-w", "0"]
            )

            assert result.exit_code == 1
            assert "Window must be greater than 0" in result.output

    def test_ema_non_numeric_column(self):
        """Test EMA with non-numeric column."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "symbol": ["AAPL", "AAPL", "AAPL"],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main, ["ti", "ema", "-i", input_file, "-c", "symbol", "-w", "2"]
            )

            assert result.exit_code == 1
            assert "numeric" in result.output.lower()

    def test_ema_with_json_input(self):
        """Test EMA with JSON input file."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.json")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
                    ),
                    "close": [100.0, 105.0, 103.0, 108.0],
                }
            )
            df.to_json(input_file, orient="records", date_format="iso")

            result = runner.invoke(
                main, ["ti", "ema", "-i", input_file, "-c", "close", "-w", "3"]
            )

            assert result.exit_code == 0
            assert "close_ema_3" in result.output

    def test_ema_quiet_mode(self):
        """Test EMA with quiet flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "prices.csv")
            output_file = os.path.join(tmpdir, "output.csv")
            df = pd.DataFrame(
                {
                    "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                    "close": [100.0, 105.0, 103.0],
                }
            )
            df.to_csv(input_file, index=False)

            result = runner.invoke(
                main,
                [
                    "ti",
                    "ema",
                    "-i",
                    input_file,
                    "-c",
                    "close",
                    "-w",
                    "2",
                    "-o",
                    output_file,
                    "-q",
                ],
            )

            assert result.exit_code == 0
            # In quiet mode with file output, should only show file confirmation
            assert "Data written to" in result.output
            # Should not contain CSV headers (which would indicate data was printed)
            lines = result.output.strip().split("\n")
            # Filter out log lines (they start with date/timestamp or don't contain commas)
            csv_lines = [
                line for line in lines if "," in line and not line.startswith("20")
            ]
            # Should have no CSV data lines in output
            assert len(csv_lines) == 0
