"""
Test cases for the ph (price history) command and aggregate_by_frequency function.
"""

import pytest
import pandas as pd
import numpy as np
from click.testing import CliRunner

from duk.commands.ph import aggregate_by_frequency
from duk.main import main


class TestAggregateByFrequency:
    """Test cases for aggregate_by_frequency function."""

    def setup_method(self):
        """Set up test data."""
        # Create sample data with daily frequency
        dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
        self.sample_data = pd.DataFrame(
            {
                "price": range(len(dates)),
                "volume": [i * 100 for i in range(len(dates))],
            },
            index=dates,
        )

    def test_frequency_mapping(self):
        """Test that frequency mapping uses Python 3.8 compatible strings."""
        from duk.commands.ph import aggregate_by_frequency
        import inspect

        # Get the source code of the function to check frequency mapping
        source = inspect.getsource(aggregate_by_frequency)

        # Check that the function uses Python 3.8 compatible frequency strings
        assert '"monthly": "M"' in source
        assert '"semiannual": "6M"' in source
        assert '"weekly": "W"' in source
        assert '"quarterly": "Q"' in source
        assert '"annual": "A"' in source

        # Ensure it does NOT use Python 3.8 incompatible strings
        assert '"monthly": "ME"' not in source
        assert '"semiannual": "6ME"' not in source

    def test_aggregate_monthly(self):
        """Test monthly aggregation."""
        result = aggregate_by_frequency(self.sample_data, "monthly")

        # Should have 12 months of data
        assert len(result) == 12

        # Check first and last entries
        assert result.index[0].month == 1  # January
        assert result.index[-1].month == 12  # December

        # Verify aggregation logic (should be last value of each month)
        jan_data = self.sample_data[self.sample_data.index.month == 1]
        assert result.iloc[0]["price"] == jan_data.iloc[-1]["price"]

    def test_aggregate_semiannual(self):
        """Test semiannual aggregation."""
        result = aggregate_by_frequency(self.sample_data, "semiannual")

        # Should have 3 entries (Jan 31, Jul 31, Jan 31 next year) due to how 6M works
        assert len(result) == 3

        # Check dates - should be end of January, July, and January next year
        assert result.index[0].month == 1
        assert result.index[1].month == 7
        assert result.index[2].month == 1

    def test_aggregate_quarterly(self):
        """Test quarterly aggregation."""
        result = aggregate_by_frequency(self.sample_data, "quarterly")

        # Should have 4 quarters
        assert len(result) == 4

        # Check that we get end of quarters
        quarters = [idx.month for idx in result.index]
        expected_quarters = [3, 6, 9, 12]  # End of Q1, Q2, Q3, Q4
        assert quarters == expected_quarters

    def test_aggregate_weekly(self):
        """Test weekly aggregation."""
        result = aggregate_by_frequency(self.sample_data, "weekly")

        # Should have approximately 52-53 weeks
        assert 52 <= len(result) <= 54

    def test_aggregate_annual(self):
        """Test annual aggregation."""
        result = aggregate_by_frequency(self.sample_data, "annual")

        # Should have 1 entry for the year
        assert len(result) == 1

        # Should be end of year
        assert result.index[0].month == 12

    def test_invalid_frequency(self):
        """Test handling of invalid frequency."""
        with pytest.raises(ValueError, match="Unsupported frequency"):
            aggregate_by_frequency(self.sample_data, "invalid")

    def test_data_with_date_column(self):
        """Test handling data with date column instead of datetime index."""
        data_with_date_col = self.sample_data.reset_index()
        data_with_date_col = data_with_date_col.rename(columns={"index": "date"})

        result = aggregate_by_frequency(data_with_date_col, "monthly")
        assert len(result) == 12
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_data_with_record_date_column(self):
        """Test handling data with record_date column."""
        data_with_record_date = self.sample_data.reset_index()
        data_with_record_date = data_with_record_date.rename(
            columns={"index": "record_date"}
        )

        result = aggregate_by_frequency(data_with_record_date, "monthly")
        assert len(result) == 12
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_data_without_datetime_index_or_column(self):
        """Test error handling for data without proper date information."""
        bad_data = pd.DataFrame({"price": [1, 2, 3], "volume": [100, 200, 300]})

        with pytest.raises(ValueError, match="Data must have datetime index"):
            aggregate_by_frequency(bad_data, "monthly")

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        empty_data = pd.DataFrame(columns=["price", "volume"])
        empty_data.index = pd.DatetimeIndex([])

        result = aggregate_by_frequency(empty_data, "monthly")
        assert len(result) == 0

    def test_data_with_nans(self):
        """Test handling of data with NaN values."""
        data_with_nans = self.sample_data.copy()
        data_with_nans.iloc[::10, :] = np.nan  # Set every 10th row to NaN

        result = aggregate_by_frequency(data_with_nans, "monthly")

        # Should still have monthly data, with NaN rows filtered out
        assert len(result) > 0
        assert len(result) <= 12


class TestPhCommand:
    """Test cases for the ph CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_ph_help(self):
        """Test ph command help."""
        result = self.runner.invoke(main, ["ph", "--help"])
        assert result.exit_code == 0
        assert "Aggregate price history data by frequency" in result.output
        assert "frequency" in result.output
        assert "monthly" in result.output
        assert "semiannual" in result.output

    def test_ph_basic_usage(self):
        """Test basic ph command usage with sample data."""
        result = self.runner.invoke(main, ["ph", "--frequency", "monthly"])

        assert result.exit_code == 0
        assert "No input file provided" in result.output
        assert "price,volume" in result.output

        # Should have monthly data points
        lines = result.output.strip().split("\n")
        data_lines = [line for line in lines if line.startswith("2023-")]
        assert len(data_lines) == 12  # 12 months

    def test_ph_semiannual_frequency(self):
        """Test ph command with semiannual frequency."""
        result = self.runner.invoke(main, ["ph", "--frequency", "semiannual"])

        assert result.exit_code == 0

        # Should have semiannual data points (3 due to year boundary)
        lines = result.output.strip().split("\n")
        data_lines = [
            line
            for line in lines
            if line.startswith("2023-") or line.startswith("2024-")
        ]
        assert len(data_lines) == 3  # 3 semiannual periods

    def test_ph_quarterly_frequency(self):
        """Test ph command with quarterly frequency."""
        result = self.runner.invoke(main, ["ph", "--frequency", "quarterly"])

        assert result.exit_code == 0

        # Should have quarterly data points
        lines = result.output.strip().split("\n")
        data_lines = [line for line in lines if line.startswith("2023-")]
        assert len(data_lines) == 4  # 4 quarters

    def test_ph_json_output(self):
        """Test ph command with JSON output format."""
        result = self.runner.invoke(
            main, ["ph", "--frequency", "monthly", "--output-format", "json"]
        )

        assert result.exit_code == 0
        assert "{" in result.output  # Should be JSON format
        assert '"price"' in result.output
        assert '"volume"' in result.output

    def test_ph_invalid_frequency(self):
        """Test ph command with invalid frequency."""
        result = self.runner.invoke(main, ["ph", "--frequency", "invalid"])

        # Should fail due to invalid choice
        assert result.exit_code != 0

    def test_ph_nonexistent_input_file(self):
        """Test ph command with non-existent input file."""
        result = self.runner.invoke(main, ["ph", "--input-file", "nonexistent.csv"])

        # Should fail due to non-existent file
        assert result.exit_code != 0
