"""
Unit tests for the SQLite cache functionality.
"""

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from duk.cache import CacheManager


class TestCacheManager:
    """Test cases for CacheManager class."""

    def setup_method(self):
        """Set up test fixtures with temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = self.temp_dir.name
        self.cache_manager = CacheManager(cache_dir=self.cache_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_init_creates_database(self):
        """Test that initialization creates the database file and tables."""
        db_path = Path(self.cache_dir) / "duk_cache.db"
        assert db_path.exists()

        # Check that tables exist
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert "treasury_cache" in tables
            assert "price_history_cache" in tables

    def test_treasury_cache_roundtrip(self):
        """Test storing and retrieving treasury data."""
        sample_data = [
            {
                "record_date": "2023-12-01",
                "1_mo": "5.50",
                "3_mo": "5.35",
                "6_mo": "5.15",
                "1_yr": "4.95",
                "2_yr": "4.85",
            }
        ]

        # Store data
        self.cache_manager.store_treasury_data(sample_data, "2023-12-01", "2023-12-01")

        # Retrieve data
        retrieved_data = self.cache_manager.get_treasury_data(
            "2023-12-01", "2023-12-01"
        )

        assert retrieved_data is not None
        assert len(retrieved_data) == 1
        assert retrieved_data[0]["record_date"] == "2023-12-01"
        assert retrieved_data[0]["1_yr"] == "4.95"

    def test_treasury_cache_miss(self):
        """Test cache miss for treasury data."""
        result = self.cache_manager.get_treasury_data("2023-01-01", "2023-01-01")
        assert result is None

    def test_price_cache_roundtrip(self):
        """Test storing and retrieving price data."""
        sample_data = [
            {
                "date": "2023-12-01",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000,
            }
        ]

        # Store data
        self.cache_manager.store_price_data(
            "AAPL", sample_data, "price", "2023-12-01", "2023-12-01"
        )

        # Retrieve data
        retrieved_data = self.cache_manager.get_price_data(
            "AAPL", "price", "2023-12-01", "2023-12-01"
        )

        assert retrieved_data is not None
        assert len(retrieved_data) == 1
        assert retrieved_data[0]["date"] == "2023-12-01"
        assert retrieved_data[0]["close"] == 103.0

    def test_price_cache_different_data_types(self):
        """Test caching different data types (price, dividend, split)."""
        price_data = [{"date": "2023-12-01", "close": 100.0}]
        dividend_data = [{"date": "2023-12-01", "dividend": 0.5}]
        split_data = [{"date": "2023-12-01", "ratio": "2:1"}]

        # Store different data types
        self.cache_manager.store_price_data(
            "AAPL", price_data, "price", "2023-12-01", "2023-12-01"
        )
        self.cache_manager.store_price_data(
            "AAPL", dividend_data, "dividend", "2023-12-01", "2023-12-01"
        )
        self.cache_manager.store_price_data(
            "AAPL", split_data, "split", "2023-12-01", "2023-12-01"
        )

        # Retrieve different data types
        retrieved_price = self.cache_manager.get_price_data(
            "AAPL", "price", "2023-12-01", "2023-12-01"
        )
        retrieved_dividend = self.cache_manager.get_price_data(
            "AAPL", "dividend", "2023-12-01", "2023-12-01"
        )
        retrieved_split = self.cache_manager.get_price_data(
            "AAPL", "split", "2023-12-01", "2023-12-01"
        )

        assert retrieved_price is not None and retrieved_price[0]["close"] == 100.0
        assert (
            retrieved_dividend is not None and retrieved_dividend[0]["dividend"] == 0.5
        )
        assert retrieved_split is not None and retrieved_split[0]["ratio"] == "2:1"

    def test_cache_key_generation(self):
        """Test that different parameters generate different cache keys."""
        # Store data with different parameters
        sample_data = [{"test": "data"}]

        self.cache_manager.store_treasury_data(sample_data, "2023-12-01", "2023-12-01")
        self.cache_manager.store_treasury_data(sample_data, "2023-12-02", "2023-12-02")

        # These should be different cache entries
        data1 = self.cache_manager.get_treasury_data("2023-12-01", "2023-12-01")
        data2 = self.cache_manager.get_treasury_data("2023-12-02", "2023-12-02")
        data3 = self.cache_manager.get_treasury_data("2023-12-03", "2023-12-03")

        assert data1 is not None
        assert data2 is not None
        assert data3 is None  # Not stored

    def test_get_cache_stats(self):
        """Test cache statistics functionality."""
        # Initially empty
        stats = self.cache_manager.get_cache_stats()
        assert stats["treasury_entries"] == 0
        assert stats["price_history_entries"] == 0

        # Add some data
        sample_data = [{"test": "data"}]
        self.cache_manager.store_treasury_data(sample_data, "2023-12-01", "2023-12-01")
        self.cache_manager.store_price_data(
            "AAPL", sample_data, "price", "2023-12-01", "2023-12-01"
        )

        # Check updated stats
        stats = self.cache_manager.get_cache_stats()
        assert stats["treasury_entries"] == 1
        assert stats["price_history_entries"] == 1
        assert stats["cache_size_bytes"] > 0

    def test_cache_with_invalid_data(self):
        """Test cache handles invalid data gracefully."""
        # Try to store None data - should not raise exception
        self.cache_manager.store_treasury_data(None, "2023-12-01", "2023-12-01")

        # Cache should still be functional
        stats = self.cache_manager.get_cache_stats()
        assert isinstance(stats, dict)

    def test_default_cache_directory_creation(self):
        """Test that default cache directory is created correctly."""
        # Test with var directory not existing (package install mode)
        original_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as temp_root:
                os.chdir(temp_root)
                # Ensure var doesn't exist
                if Path("var").exists():
                    import shutil

                    shutil.rmtree("var")

                # This should use ~/var/duk/ path
                cache_manager = CacheManager()
                expected_path = Path.home() / "var" / "duk" / "duk_cache.db"
                assert cache_manager.db_path.name == "duk_cache.db"
        finally:
            os.chdir(original_cwd)

    @patch("duk.cache.logger")
    def test_error_handling_in_cache_operations(self, mock_logger):
        """Test error handling in cache operations."""
        # Corrupt the database file to trigger errors
        with open(self.cache_manager.db_path, "w") as f:
            f.write("corrupted data")

        # These operations should not raise exceptions, but log errors
        result = self.cache_manager.get_treasury_data("2023-12-01", "2023-12-01")
        assert result is None

        # Store operation should also handle errors gracefully
        self.cache_manager.store_treasury_data(
            [{"test": "data"}], "2023-12-01", "2023-12-01"
        )

        # Verify error was logged
        assert mock_logger.error.called
