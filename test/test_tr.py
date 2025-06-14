"""
Unit tests for the treasury rate subprogram.
"""

import json
import pytest
from unittest.mock import Mock, patch
import pandas as pd

from duk.commands.tr import TreasuryRateDownloader, format_data_for_pandas


class TestTreasuryRateDownloader:
    """Test cases for TreasuryRateDownloader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.downloader = TreasuryRateDownloader()

        # Sample treasury data for testing
        self.sample_data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "2_mo": "5.40",
                "3_mo": "5.35",
                "4_mo": "5.25",
                "6_mo": "5.15",
                "1_yr": "4.95",
                "2_yr": "4.85",
                "3_yr": "4.75",
                "5_yr": "4.65",
                "7_yr": "4.55",
                "10_yr": "4.45",
                "20_yr": "4.35",
                "30_yr": "4.25",
            },
            {
                "record_date": "2023-11-30",
                "1_mo": "5.52",
                "2_mo": "5.42",
                "3_mo": "5.37",
                "4_mo": "5.27",
                "6_mo": "5.17",
                "1_yr": "4.97",
                "2_yr": "4.87",
                "3_yr": "4.77",
                "5_yr": "4.67",
                "7_yr": "4.57",
                "10_yr": "4.47",
                "20_yr": "4.37",
                "30_yr": "4.27",
            },
        ]

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_get_latest_date_success(self, mock_request):
        """Test successful retrieval of latest date."""
        mock_request.return_value = {"data": [{"record_date": "2023-12-01"}]}

        result = self.downloader.get_latest_date()
        assert result == "2023-12-01"

        # Verify correct API call
        mock_request.assert_called_once_with(
            {"sort": "-record_date", "page[size]": "1"}
        )

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

        # Verify the filter parameter
        expected_params = {"sort": "record_date", "filter": "record_date:eq:2023-12-01"}
        mock_request.assert_called_once_with(expected_params)

    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_download_data_date_range(self, mock_request):
        """Test downloading data for a date range."""
        mock_request.return_value = {"data": self.sample_data}

        result = self.downloader.download_data(
            start_date="2023-11-30", end_date="2023-12-01"
        )
        assert result == self.sample_data

        # Verify the filter parameter
        expected_params = {
            "sort": "record_date",
            "filter": "record_date:gte:2023-11-30,record_date:lte:2023-12-01",
        }
        mock_request.assert_called_once_with(expected_params)

    @patch("duk.commands.tr.TreasuryRateDownloader.get_latest_date")
    @patch("duk.commands.tr.TreasuryRateDownloader._make_request")
    def test_download_data_with_days(self, mock_request, mock_latest):
        """Test downloading data with days parameter."""
        mock_latest.return_value = "2023-12-01"
        mock_request.return_value = {"data": self.sample_data}

        result = self.downloader.download_data(days=2)
        assert result == self.sample_data

        # Verify the date range calculation
        expected_params = {
            "sort": "record_date",
            "filter": "record_date:gte:2023-11-30,record_date:lte:2023-12-01",
        }
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

        mock_get.assert_called_once_with(
            self.downloader.BASE_URL, params={"test": "param"}, timeout=30
        )

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
                "1_mo": "5.50",
                "2_mo": "5.40",
                "1_yr": "4.95",
                "10_yr": "4.45",
            }
        ]

        result = format_data_for_pandas(data)

        # Check DataFrame structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "record_date" in result.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result["record_date"])
        assert pd.api.types.is_numeric_dtype(result["1_mo"])
        assert pd.api.types.is_numeric_dtype(result["10_yr"])

        # Check values
        assert result.iloc[0]["record_date"] == pd.Timestamp("2023-12-01")
        assert result.iloc[0]["1_mo"] == 5.50
        assert result.iloc[0]["10_yr"] == 4.45

    def test_format_data_with_nulls(self):
        """Test formatting data with null values."""
        data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "2_mo": None,
                "1_yr": "",
                "10_yr": "4.45",
            }
        ]

        result = format_data_for_pandas(data)

        # Check that nulls are handled properly
        assert result.iloc[0]["1_mo"] == 5.50
        assert pd.isna(result.iloc[0]["2_mo"])
        assert pd.isna(result.iloc[0]["1_yr"])
        assert result.iloc[0]["10_yr"] == 4.45


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    data = {
        "record_date": [pd.Timestamp("2023-12-01"), pd.Timestamp("2023-11-30")],
        "1_mo": [5.50, 5.52],
        "1_yr": [4.95, 4.97],
        "10_yr": [4.45, 4.47],
    }
    return pd.DataFrame(data)


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
        assert list(saved_df.columns) == ["record_date", "1_mo", "1_yr", "10_yr"]

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
        assert data[0]["1_mo"] == 5.50
