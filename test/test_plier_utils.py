"""
Tests for plier_utils module.
"""

import pandas as pd
import pytest

from duk.plier_utils import (
    cut_rows,
    grab_columns,
    join_datasets,
    parse_column_spec,
    strip_columns,
)


class TestParseColumnSpec:
    """Tests for parse_column_spec function."""

    def test_parse_column_names(self):
        """Test parsing column names."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110], "volume": [1000, 1100]})
        result = parse_column_spec("close,volume", df)
        assert result == ["close", "volume"]

    def test_parse_positive_indices(self):
        """Test parsing positive column indices."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110], "volume": [1000, 1100]})
        result = parse_column_spec("1,2", df)
        assert result == ["close", "volume"]

    def test_parse_negative_indices(self):
        """Test parsing negative column indices."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110], "volume": [1000, 1100]})
        result = parse_column_spec("-1,-2", df)
        assert result == ["volume", "close"]

    def test_parse_mixed_spec(self):
        """Test parsing mixed column names and indices."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110], "volume": [1000, 1100]})
        result = parse_column_spec("date,1,-1", df)
        assert result == ["date", "close", "volume"]

    def test_parse_invalid_column_name(self):
        """Test parsing invalid column name."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110]})
        with pytest.raises(ValueError, match="Column 'invalid' not found"):
            parse_column_spec("invalid", df)

    def test_parse_invalid_index(self):
        """Test parsing out of range index."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110]})
        with pytest.raises(ValueError, match="out of range"):
            parse_column_spec("10", df)

    def test_parse_negative_index_out_of_range(self):
        """Test parsing negative index out of range."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110]})
        with pytest.raises(ValueError, match="out of range"):
            parse_column_spec("-10", df)

    def test_parse_empty_spec(self):
        """Test parsing empty specification."""
        df = pd.DataFrame({"date": [1, 2], "close": [100, 110]})
        result = parse_column_spec("", df)
        assert result == []


class TestGrabColumns:
    """Tests for grab_columns function."""

    def test_grab_by_column_names(self):
        """Test grabbing columns by name."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = grab_columns(df, "close,volume")
        assert list(result.columns) == ["date", "close", "volume"]
        assert len(result) == 2

    def test_grab_by_positive_indices(self):
        """Test grabbing columns by positive indices."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = grab_columns(df, "2,3")
        assert list(result.columns) == ["date", "close", "volume"]

    def test_grab_by_negative_indices(self):
        """Test grabbing columns by negative indices."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = grab_columns(df, "-2,-1")
        assert list(result.columns) == ["date", "close", "volume"]

    def test_grab_without_date_column(self):
        """Test grabbing columns when no date column exists."""
        df = pd.DataFrame(
            {
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = grab_columns(df, "close,volume")
        assert list(result.columns) == ["close", "volume"]

    def test_grab_including_date_in_spec(self):
        """Test grabbing columns when date is in the spec."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
            }
        )
        result = grab_columns(df, "date,close")
        assert list(result.columns) == ["date", "close"]


class TestStripColumns:
    """Tests for strip_columns function."""

    def test_strip_by_column_names(self):
        """Test stripping columns by name."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = strip_columns(df, "open,volume")
        assert list(result.columns) == ["date", "close"]
        assert len(result) == 2

    def test_strip_by_positive_indices(self):
        """Test stripping columns by positive indices."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = strip_columns(df, "1,3")
        assert list(result.columns) == ["date", "close"]

    def test_strip_by_negative_indices(self):
        """Test stripping columns by negative indices."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [100.0, 105.0],
                "close": [102.0, 107.0],
                "volume": [1000, 1100],
            }
        )
        result = strip_columns(df, "-3,-1")
        assert list(result.columns) == ["date", "close"]


class TestJoinDatasets:
    """Tests for join_datasets function."""

    def test_join_two_datasets(self):
        """Test joining two datasets."""
        df1 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        df2 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "volume": [1000, 1100],
            }
        )
        result = join_datasets([df1, df2])
        assert list(result.columns) == ["date", "close", "volume"]
        assert len(result) == 2

    def test_join_three_datasets(self):
        """Test joining three datasets."""
        df1 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        df2 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "volume": [1000, 1100],
            }
        )
        df3 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "open": [99.0, 104.0],
            }
        )
        result = join_datasets([df1, df2, df3])
        assert "date" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns
        assert "open" in result.columns
        assert len(result) == 2

    def test_join_with_missing_dates(self):
        """Test joining datasets with missing dates (outer join)."""
        df1 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        df2 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-03", "2023-01-04"]),
                "volume": [1100, 1200],
            }
        )
        result = join_datasets([df1, df2])
        assert len(result) == 3  # Should have all 3 dates

    def test_join_sorts_by_date(self):
        """Test that join result is sorted by date."""
        df1 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-03", "2023-01-02"]),
                "close": [105.0, 100.0],
            }
        )
        df2 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "volume": [1000, 1100],
            }
        )
        result = join_datasets([df1, df2])
        assert result["date"].tolist() == [
            pd.Timestamp("2023-01-02"),
            pd.Timestamp("2023-01-03"),
        ]

    def test_join_with_duplicate_columns(self):
        """Test joining datasets with duplicate column names."""
        df1 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "price": [100.0, 105.0],
            }
        )
        df2 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "price": [99.0, 104.0],
            }
        )
        result = join_datasets([df1, df2])
        assert "price" in result.columns
        assert "price_1" in result.columns

    def test_join_too_few_datasets(self):
        """Test join with too few datasets."""
        df1 = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        with pytest.raises(ValueError, match="At least 2 datasets are required"):
            join_datasets([df1])

    def test_join_missing_date_column(self):
        """Test join when date column is missing."""
        df1 = pd.DataFrame(
            {
                "close": [100.0, 105.0],
            }
        )
        df2 = pd.DataFrame(
            {
                "volume": [1000, 1100],
            }
        )
        with pytest.raises(ValueError, match="Date column not found"):
            join_datasets([df1, df2])


class TestCutRows:
    """Tests for cut_rows function."""

    def test_cut_positive_rows(self):
        """Test cutting rows from the start."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                ),
                "close": [100.0, 105.0, 103.0, 108.0],
            }
        )
        result = cut_rows(df, 2)
        assert len(result) == 2
        assert result["close"].tolist() == [103.0, 108.0]

    def test_cut_negative_rows(self):
        """Test cutting rows from the end."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
                ),
                "close": [100.0, 105.0, 103.0, 108.0],
            }
        )
        result = cut_rows(df, -2)
        assert len(result) == 2
        assert result["close"].tolist() == [100.0, 105.0]

    def test_cut_single_row_positive(self):
        """Test cutting single row from start."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        result = cut_rows(df, 1)
        assert len(result) == 1
        assert result["close"].iloc[0] == 105.0

    def test_cut_single_row_negative(self):
        """Test cutting single row from end."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        result = cut_rows(df, -1)
        assert len(result) == 1
        assert result["close"].iloc[0] == 100.0

    def test_cut_too_many_rows(self):
        """Test cutting more rows than available."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        with pytest.raises(ValueError, match="Cannot cut"):
            cut_rows(df, 5)

    def test_cut_all_rows(self):
        """Test cutting all rows."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-02", "2023-01-03"]),
                "close": [100.0, 105.0],
            }
        )
        with pytest.raises(ValueError, match="Cannot cut"):
            cut_rows(df, 2)
