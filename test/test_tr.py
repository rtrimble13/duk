"""
Unit tests for the treasury rate subprogram.
"""

import json
import pytest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np

from duk.commands.tr import (
    TreasuryRateDownloader,
    format_data_for_pandas,
    maturity_to_years,
    get_interpolation_maturities,
    interpolate_yield_curve,
    bootstrap_spot_rates,
)


class TestTreasuryRateDownloader:
    """Test cases for TreasuryRateDownloader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.downloader = TreasuryRateDownloader()

        # Sample treasury data for testing
        self.sample_data = [
            {
                "record_date": "2023-12-01",
                "month1": "5.50",
                "month2": "5.40",
                "month3": "5.35",
                "month4": "5.25",
                "month6": "5.15",
                "year1": "4.95",
                "year2": "4.85",
                "year3": "4.75",
                "year5": "4.65",
                "year7": "4.55",
                "year10": "4.45",
                "year20": "4.35",
                "year30": "4.25",
            },
            {
                "record_date": "2023-11-30",
                "month1": "5.52",
                "month2": "5.42",
                "month3": "5.37",
                "month4": "5.27",
                "month6": "5.17",
                "year1": "4.97",
                "year2": "4.87",
                "year3": "4.77",
                "year5": "4.67",
                "year7": "4.57",
                "year10": "4.47",
                "year20": "4.37",
                "year30": "4.27",
            },
        ]

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_get_latest_date_success(self, mock_request):
        """Test successful retrieval of latest date."""
        mock_request.return_value = {"data": [{"record_date": "2023-12-01"}]}

        result = self.downloader.get_latest_date()
        assert result == "2023-12-01"

        # Verify correct API call
        # Should request only one record via FMP API
        mock_request.assert_called_once_with({"limit": 1})

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_get_latest_date_failure(self, mock_request):
        """Test handling of API failure when getting latest date."""
        mock_request.return_value = None

        result = self.downloader.get_latest_date()
        assert result is None

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_download_data_latest_only(self, mock_request):
        """Test downloading latest data only."""
        # Mock the get_latest_date call first
        mock_request.side_effect = [
            {"data": [{"record_date": "2023-12-01"}]},  # get_latest_date call
            {"data": self.sample_data[:1]},  # download_data call
        ]

        result = self.downloader.download_data()
        assert result == self.sample_data[:1]
        assert len(result) == 1
        assert result[0]["record_date"] == "2023-12-01"

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_download_data_specific_date(self, mock_request):
        """Test downloading data for a specific date."""
        mock_request.return_value = {"data": self.sample_data[:1]}

        result = self.downloader.download_data(start_date="2023-12-01")
        assert result == self.sample_data[:1]

        # Verify the date range parameters for FMP API
        expected_params = {"from": "2023-12-01", "to": "2023-12-01"}
        mock_request.assert_called_once_with(expected_params)

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_download_data_date_range(self, mock_request):
        """Test downloading data for a date range."""
        mock_request.return_value = {"data": self.sample_data}

        result = self.downloader.download_data(
            start_date="2023-11-30", end_date="2023-12-01"
        )
        assert result == self.sample_data

        # Verify the date range parameters for FMP API
        expected_params = {"from": "2023-11-30", "to": "2023-12-01"}
        mock_request.assert_called_once_with(expected_params)

    @patch("duk.commands.tr.TreasuryRateDownloader.get_latest_date")
    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_download_data_with_days(self, mock_request, mock_latest):
        """Test downloading data with days parameter."""
        mock_latest.return_value = "2023-12-01"
        mock_request.return_value = {"data": self.sample_data}

        result = self.downloader.download_data(days=2)
        assert result == self.sample_data

        # Verify the date range parameters for FMP API
        expected_params = {"from": "2023-11-30", "to": "2023-12-01"}
        mock_request.assert_called_once_with(expected_params)

    @patch("requests.Session.get")
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.downloader._make_request({"test": "param"})
        assert result == {"data": []}
        # Verify that the API key is included in the request parameters
        called_args, called_kwargs = mock_get.call_args
        assert called_args[0] == self.downloader.BASE_URL
        params = called_kwargs.get("params", {})
        assert params.get("test") == "param"
        assert "apikey" in params
        assert called_kwargs.get("timeout") == 30

    @patch("requests.Session.get")
    def test_make_request_failure(self, mock_get):
        """Test handling of API request failure."""
        mock_get.side_effect = Exception("Network error")

        result = self.downloader._make_request({"test": "param"})
        assert result is None


class TestFormatDataForPandas:
    """Test cases for format_data_for_pandas function."""

    def test_format_empty_data(self):
        """Test formatting empty data."""
        result = format_data_for_pandas([])
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_format_sample_data(self):
        """Test formatting sample treasury data."""
        data = [
            {
                "record_date": "2023-12-01",
                "month1": "5.50",
                "month2": "5.40",
                "year1": "4.95",
                "year10": "4.45",
            }
        ]

        result = format_data_for_pandas(data)

        # Check DataFrame structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "record_date" in result.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result["record_date"])
        assert pd.api.types.is_numeric_dtype(result["month1"])
        assert pd.api.types.is_numeric_dtype(result["year10"])

        # Check values
        assert result.iloc[0]["record_date"] == pd.Timestamp("2023-12-01")
        assert result.iloc[0]["month1"] == 5.50
        assert result.iloc[0]["year10"] == 4.45

    def test_format_data_with_nulls(self):
        """Test formatting data with null values."""
        data = [
            {
                "record_date": "2023-12-01",
                "month1": "5.50",
                "month2": None,
                "year1": "",
                "year10": "4.45",
            }
        ]

        result = format_data_for_pandas(data)

        # Check that nulls are handled properly
        assert result.iloc[0]["month1"] == 5.50
        assert pd.isna(result.iloc[0]["month2"])
        assert pd.isna(result.iloc[0]["year1"])
        assert result.iloc[0]["year10"] == 4.45


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    data = {
        "record_date": [pd.Timestamp("2023-12-01"), pd.Timestamp("2023-11-30")],
        "month1": [5.50, 5.52],
        "year1": [4.95, 4.97],
        "year10": [4.45, 4.47],
    }
    return pd.DataFrame(data)


class TestBootstrapSpotRates:
    """Test cases for bootstrap spot rates functionality."""

    def test_bootstrap_spot_rates_basic(self):
        """Test basic bootstrap spot rate calculation."""
        # Simple test case with known par rates
        maturities = np.array([0.5, 1.0, 2.0, 5.0])
        par_rates = np.array([4.0, 4.2, 4.5, 5.0])

        spot_rates = bootstrap_spot_rates(maturities, par_rates)

        # Basic checks
        assert len(spot_rates) == len(par_rates)
        # First spot rate should be approximately equal to first par rate
        # (within rounding)
        assert abs(spot_rates[0] - par_rates[0]) < 1e-10
        assert all(spot_rates > 0)  # All spot rates should be positive

        # Spot rates should be close to par rates for realistic data
        assert all(np.abs(spot_rates - par_rates) < 2.0)

    def test_bootstrap_spot_rates_single_maturity(self):
        """Test bootstrap with single maturity."""
        maturities = np.array([1.0])
        par_rates = np.array([4.5])

        spot_rates = bootstrap_spot_rates(maturities, par_rates)

        assert len(spot_rates) == 1
        assert abs(spot_rates[0] - par_rates[0]) < 1e-10

    def test_bootstrap_spot_rates_empty_input(self):
        """Test bootstrap with empty input."""
        maturities = np.array([])
        par_rates = np.array([])

        spot_rates = bootstrap_spot_rates(maturities, par_rates)

        assert len(spot_rates) == 0

    def test_bootstrap_spot_rates_mismatched_lengths(self):
        """Test bootstrap with mismatched input lengths."""
        maturities = np.array([1.0, 2.0])
        par_rates = np.array([4.0])

        with pytest.raises(ValueError, match="must have the same length"):
            bootstrap_spot_rates(maturities, par_rates)

    def test_bootstrap_spot_rates_unsorted_input(self):
        """Test bootstrap with unsorted maturities."""
        # Input maturities out of order
        maturities = np.array([2.0, 0.5, 5.0, 1.0])
        par_rates = np.array([4.5, 4.0, 5.0, 4.2])

        spot_rates = bootstrap_spot_rates(maturities, par_rates)

        # Should return results in original order
        assert len(spot_rates) == len(par_rates)
        assert all(spot_rates > 0)

    def test_interpolate_yield_curve_with_bootstrap(self):
        """Test interpolation with bootstrap spot rates enabled."""
        # Create sample data
        data = {
            "record_date": pd.Timestamp("2023-12-01"),
            "month1": 5.50,
            "month3": 5.35,
            "month6": 5.15,
            "year1": 4.95,
            "year2": 4.85,
            "year5": 4.65,
            "year10": 4.45,
            "year30": 4.25,
        }
        df_row = pd.Series(data)

        # Test interpolation with bootstrap enabled
        result = interpolate_yield_curve(
            df_row, "semiannual", bootstrap_spot_rates_flag=True
        )

        # Check result structure
        assert isinstance(result, pd.DataFrame)
        expected_columns = [
            "calendar_date",
            "maturity_years",
            "interpolated_rate",
            "interpolated_spot_rate",
        ]
        assert list(result.columns) == expected_columns
        assert len(result) > 0

        # Check that spot rates are calculated
        assert "interpolated_spot_rate" in result.columns
        assert all(result["interpolated_spot_rate"] > 0)
        assert all(pd.notna(result["interpolated_spot_rate"]))

        # Spot rates should be close to par rates
        rate_diff = np.abs(
            result["interpolated_rate"] - result["interpolated_spot_rate"]
        )
        assert all(rate_diff < 2.0)  # Should be within reasonable range

    def test_interpolate_yield_curve_bootstrap_failure_fallback(self):
        """Test that interpolation gracefully handles bootstrap calculation failures."""
        # Create data that might cause bootstrap issues (all same rate)
        data = {
            "record_date": pd.Timestamp("2023-12-01"),
            "year1": 4.0,
            "year2": 4.0,
            "year5": 4.0,
        }
        df_row = pd.Series(data)

        # Should not raise an exception even if bootstrap fails
        result = interpolate_yield_curve(
            df_row, "semiannual", bootstrap_spot_rates_flag=True
        )

        # Should still have interpolated rates
        assert isinstance(result, pd.DataFrame)
        assert "interpolated_rate" in result.columns
        assert len(result) > 0

    def test_bootstrap_semiannual_coupons_with_different_intervals(self):
        """Test bootstrap correctly handles semiannual coupons for intervals."""
        # Create sample data with sufficient points for interpolation
        data = {
            "record_date": pd.Timestamp("2023-12-01"),
            "month6": 4.00,
            "year1": 4.20,
            "year2": 4.50,
            "year5": 5.00,
            "year10": 5.25,
        }
        df_row = pd.Series(data)

        # Test bootstrap with semiannual interval (direct calculation)
        result_semiannual = interpolate_yield_curve(
            df_row, "semiannual", bootstrap_spot_rates_flag=True
        )

        # Test bootstrap with quarterly interval (should use two-step process)
        result_quarterly = interpolate_yield_curve(
            df_row, "quarter", bootstrap_spot_rates_flag=True
        )

        # Both should have spot rates
        assert "interpolated_spot_rate" in result_semiannual.columns
        assert "interpolated_spot_rate" in result_quarterly.columns

        # Quarterly should have more data points than semiannual
        assert len(result_quarterly) > len(result_semiannual)

        # Spot rates should be positive and close to par rates
        assert all(result_semiannual["interpolated_spot_rate"] > 0)
        assert all(result_quarterly["interpolated_spot_rate"] > 0)

        # Check that spot rates are reasonable (within 2% of par rates)
        semi_diff = np.abs(
            result_semiannual["interpolated_rate"]
            - result_semiannual["interpolated_spot_rate"]
        )
        quarterly_diff = np.abs(
            result_quarterly["interpolated_rate"]
            - result_quarterly["interpolated_spot_rate"]
        )
        assert all(semi_diff < 2.0)
        assert all(quarterly_diff < 2.0)


class TestSaveData:
    """Test cases for save_data function."""

    def test_save_csv(self, tmp_path, sample_dataframe):
        """Test saving data as CSV."""
        from duk.commands.tr import save_data

        filename = "test_output.csv"
        save_data(sample_dataframe, filename, "csv", str(tmp_path))

        # Check file was created
        filepath = tmp_path / filename
        assert filepath.exists()

        # Check content
        saved_df = pd.read_csv(filepath)
        assert len(saved_df) == 2
        assert list(saved_df.columns) == ["record_date", "month1", "year1", "year10"]

    def test_save_json(self, tmp_path, sample_dataframe):
        """Test saving data as JSON."""
        from duk.commands.tr import save_data

        filename = "test_output.json"
        save_data(sample_dataframe, filename, "json", str(tmp_path))

        # Check file was created
        filepath = tmp_path / filename
        assert filepath.exists()

        # Check content
        with open(filepath) as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["record_date"] == "2023-12-01"
        assert data[0]["month1"] == 5.50


class TestInterpolationFunctions:
    """Test cases for interpolation functions."""

    def test_maturity_to_years(self):
        """Test maturity string conversion to years."""
        assert maturity_to_years("month1") == 1 / 12
        assert maturity_to_years("month6") == 0.5
        assert maturity_to_years("year1") == 1.0
        assert maturity_to_years("year10") == 10.0
        assert maturity_to_years("year30") == 30.0

        with pytest.raises(ValueError):
            maturity_to_years("invalid_format")

    def test_get_interpolation_maturities(self):
        """Test interpolation maturity point generation."""
        # Test semiannual
        semi_maturities = get_interpolation_maturities("semiannual")
        assert len(semi_maturities) == 60  # 0.5 to 30.0 in 0.5 steps
        assert semi_maturities[0] == 0.5
        assert semi_maturities[-1] == 30.0

        # Test quarterly
        quarterly_maturities = get_interpolation_maturities("quarter")
        assert quarterly_maturities[0] == 0.25
        assert quarterly_maturities[1] == 0.5

        # Test invalid interval
        with pytest.raises(ValueError):
            get_interpolation_maturities("invalid")

    def test_interpolate_yield_curve(self):
        """Test cubic spline interpolation of yield curve."""
        # Create sample data
        data = {
            "record_date": pd.Timestamp("2023-12-01"),
            "month1": 5.50,
            "month3": 5.35,
            "month6": 5.15,
            "year1": 4.95,
            "year2": 4.85,
            "year5": 4.65,
            "year10": 4.45,
            "year30": 4.25,
        }
        df_row = pd.Series(data)

        # Test interpolation
        result = interpolate_yield_curve(df_row, "semiannual")

        # Check result structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            "calendar_date",
            "maturity_years",
            "interpolated_rate",
        ]
        assert len(result) > 0

        # Check data types and values
        assert result["calendar_date"].iloc[0] == "2023-12-01"
        assert all(result["maturity_years"] >= 1 / 12)  # Should start from 1 month
        assert all(result["maturity_years"] <= 30.0)  # Should not exceed 30 years

        # Check that interpolated rates are reasonable
        assert all(result["interpolated_rate"] > 0)
        assert all(result["interpolated_rate"] < 10)  # Reasonable rate range

    def test_interpolate_yield_curve_insufficient_data(self):
        """Test interpolation with insufficient data points."""
        # Create sample data with only 2 points (need at least 3 for cubic spline)
        data = {
            "record_date": pd.Timestamp("2023-12-01"),
            "year1": 4.95,
            "year10": 4.45,
        }
        df_row = pd.Series(data)

        # Should return DataFrame with NaN values instead of raising exception
        result = interpolate_yield_curve(df_row, "semiannual")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["calendar_date"].iloc[0] == "2023-12-01"
        assert pd.isna(result["maturity_years"].iloc[0])
        assert pd.isna(result["interpolated_rate"].iloc[0])

    def test_interpolate_yield_curve_with_nans(self):
        """Test interpolation with NaN values in data."""
        # Create sample data with NaN values
        data = {
            "record_date": pd.Timestamp("2023-12-01"),
            "month1": 5.50,
            "month3": np.nan,  # This should be filtered out
            "month6": 5.15,
            "year1": 4.95,
            "year2": np.nan,  # This should be filtered out
            "year5": 4.65,
            "year10": 4.45,
            "year30": 4.25,
        }
        df_row = pd.Series(data)

        # Should still work with valid data points
        result = interpolate_yield_curve(df_row, "semiannual")
        assert len(result) > 0
        assert all(result["interpolated_rate"] > 0)
