"""
Tests for rates_utils module.
"""

import pandas as pd

from duk.rates_utils import treasury_rates2df


class TestTreasuryRates2df:
    """Tests for treasury_rates2df function."""

    def test_basic_conversion(self):
        """Test basic conversion of treasury rates to DataFrame."""
        par_yields = [
            {
                "date": "2023-01-03",
                "month1": 4.35,
                "month2": 4.42,
                "month3": 4.45,
                "year1": 4.68,
                "year5": 3.94,
                "year10": 3.79,
                "year30": 3.88,
            },
            {
                "date": "2023-01-02",
                "month1": 4.30,
                "month2": 4.40,
                "month3": 4.43,
                "year1": 4.65,
                "year5": 3.90,
                "year10": 3.75,
                "year30": 3.85,
            },
        ]

        result = treasury_rates2df(par_yields)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.index.name == "date"

    def test_date_is_converted_to_date_object(self):
        """Test that date field is converted to date object."""
        from datetime import date

        par_yields = [
            {"date": "2023-01-03", "month1": 4.35},
            {"date": "2023-01-02", "month1": 4.30},
        ]

        result = treasury_rates2df(par_yields)

        # Check that index values are date objects
        assert result.index[0] == date(2023, 1, 2)
        assert result.index[1] == date(2023, 1, 3)

    def test_dataframe_indexed_on_date(self):
        """Test that DataFrame is indexed on date."""
        par_yields = [
            {"date": "2023-01-03", "year10": 3.79},
            {"date": "2023-01-02", "year10": 3.75},
        ]

        result = treasury_rates2df(par_yields)

        assert result.index.name == "date"
        assert "date" not in result.columns

    def test_dataframe_sorted_ascending(self):
        """Test that DataFrame is sorted by date in ascending order."""
        par_yields = [
            {"date": "2023-01-05", "year10": 3.80},
            {"date": "2023-01-02", "year10": 3.75},
            {"date": "2023-01-04", "year10": 3.78},
            {"date": "2023-01-03", "year10": 3.76},
        ]

        result = treasury_rates2df(par_yields)

        # Verify ascending order
        dates = list(result.index)
        assert dates == sorted(dates)

    def test_empty_input_returns_empty_dataframe(self):
        """Test that empty input returns empty DataFrame."""
        result = treasury_rates2df([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_rate_values_preserved(self):
        """Test that rate values are correctly preserved."""
        par_yields = [
            {
                "date": "2023-01-03",
                "month1": 4.35,
                "year10": 3.79,
                "year30": 3.88,
            },
        ]

        result = treasury_rates2df(par_yields)

        assert result.loc[result.index[0], "month1"] == 4.35
        assert result.loc[result.index[0], "year10"] == 3.79
        assert result.loc[result.index[0], "year30"] == 3.88

    def test_all_rate_columns_present(self):
        """Test that all rate columns from input are present in output."""
        par_yields = [
            {
                "date": "2023-01-03",
                "month1": 4.35,
                "month2": 4.42,
                "month3": 4.45,
                "year1": 4.68,
                "year5": 3.94,
                "year10": 3.79,
                "year30": 3.88,
            },
        ]

        result = treasury_rates2df(par_yields)

        expected_columns = [
            "month1",
            "month2",
            "month3",
            "year1",
            "year5",
            "year10",
            "year30",
        ]
        for col in expected_columns:
            assert col in result.columns

    def test_single_record_input(self):
        """Test conversion with single record input."""
        par_yields = [
            {"date": "2023-01-03", "month1": 4.35, "year10": 3.79},
        ]

        result = treasury_rates2df(par_yields)

        assert len(result) == 1
        assert result.index.name == "date"

    def test_missing_date_column(self):
        """Test handling of input without date column."""
        par_yields = [
            {"month1": 4.35, "year10": 3.79},
            {"month1": 4.30, "year10": 3.75},
        ]

        result = treasury_rates2df(par_yields)

        # Should return DataFrame without date index
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_none_values_in_rates(self):
        """Test handling of None values in rate fields."""
        par_yields = [
            {"date": "2023-01-03", "month1": 4.35, "year10": None},
            {"date": "2023-01-02", "month1": None, "year10": 3.75},
        ]

        result = treasury_rates2df(par_yields)

        assert len(result) == 2
        assert pd.isna(result.loc[result.index[1], "year10"])
        assert pd.isna(result.loc[result.index[0], "month1"])
