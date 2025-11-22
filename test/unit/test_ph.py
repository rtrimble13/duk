"""
Unit tests for price history (ph) module
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from duk.api.ph import get_price_history


class TestGetPriceHistory:
    """Test cases for get_price_history function"""

    def test_get_price_history_validates_symbol(self):
        """Test that empty symbol raises ValueError"""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            get_price_history("", "test_api_key")

    def test_get_price_history_validates_api_key(self):
        """Test that empty api_key raises ValueError"""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            get_price_history("IBM", "")

    def test_get_price_history_converts_symbol_to_uppercase(self):
        """Test that symbol is converted to uppercase"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "historical": [
                {"date": "2023-01-01", "close": 100.0, "volume": 1000},
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response) as mock_get:
            get_price_history("ibm", "test_api_key")
            # Check that URL contains uppercase symbol
            call_args = mock_get.call_args
            assert "IBM" in call_args[0][0]

    def test_get_price_history_returns_dataframe(self):
        """Test that function returns a pandas DataFrame"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "historical": [
                {"date": "2023-01-01", "close": 100.0, "volume": 1000},
                {"date": "2023-01-02", "close": 101.0, "volume": 1100},
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            result = get_price_history("IBM", "test_api_key")
            assert isinstance(result, pd.DataFrame)

    def test_get_price_history_sorts_by_date_ascending(self):
        """Test that results are sorted by date in ascending order"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "historical": [
                {"date": "2023-01-03", "close": 102.0, "volume": 1200},
                {"date": "2023-01-01", "close": 100.0, "volume": 1000},
                {"date": "2023-01-02", "close": 101.0, "volume": 1100},
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            result = get_price_history("IBM", "test_api_key")
            dates = result["date"].tolist()
            assert dates == ["2023-01-01", "2023-01-02", "2023-01-03"]

    def test_get_price_history_applies_limit(self):
        """Test that limit parameter limits number of results"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "historical": [
                {"date": "2023-01-01", "close": 100.0, "volume": 1000},
                {"date": "2023-01-02", "close": 101.0, "volume": 1100},
                {"date": "2023-01-03", "close": 102.0, "volume": 1200},
                {"date": "2023-01-04", "close": 103.0, "volume": 1300},
                {"date": "2023-01-05", "close": 104.0, "volume": 1400},
                {"date": "2023-01-06", "close": 105.0, "volume": 1500},
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            result = get_price_history("IBM", "test_api_key", limit=3)
            assert len(result) == 3
            # Should return the 3 most recent (last 3 after sorting)
            dates = result["date"].tolist()
            assert dates == ["2023-01-04", "2023-01-05", "2023-01-06"]

    def test_get_price_history_includes_date_parameters(self):
        """Test that from_date and to_date are included in request"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "historical": [
                {"date": "2023-01-01", "close": 100.0, "volume": 1000},
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response) as mock_get:
            get_price_history(
                "IBM",
                "test_api_key",
                from_date="2023-01-01",
                to_date="2023-01-31",
            )
            # Check that params include from and to
            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["from"] == "2023-01-01"
            assert params["to"] == "2023-01-31"

    def test_get_price_history_handles_api_error(self):
        """Test that API errors are properly raised"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException(
            "API Error"
        )

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(requests.RequestException):
                get_price_history("IBM", "test_api_key")

    def test_get_price_history_handles_missing_historical_data(self):
        """Test that missing historical data raises ValueError"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(ValueError, match="No historical data found"):
                get_price_history("IBM", "test_api_key")

    def test_get_price_history_handles_empty_historical_data(self):
        """Test that empty historical data returns empty DataFrame"""
        mock_response = Mock()
        mock_response.json.return_value = {"historical": []}
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            result = get_price_history("IBM", "test_api_key")
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_price_history_default_limit_is_5(self):
        """Test that default limit is 5"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "historical": [
                {"date": f"2023-01-{i:02d}", "close": 100.0 + i, "volume": 1000}
                for i in range(1, 11)
            ]
        }
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            result = get_price_history("IBM", "test_api_key")
            assert len(result) == 5
