"""
Tests for ls_utils module.
"""

import hashlib

import pandas as pd

from duk.ls_utils import process_industries, process_sectors


class TestProcessSectors:
    """Tests for process_sectors function."""

    def test_basic_processing(self):
        """Test basic processing of sector data."""
        sector_data = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
            {"sector": "Financial Services"},
        ]

        result = process_sectors(sector_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ["sector_id", "sector_hash", "sector_name"]

    def test_alphabetical_sorting(self):
        """Test that sectors are sorted alphabetically before assigning IDs."""
        sector_data = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
            {"sector": "Financial Services"},
        ]

        result = process_sectors(sector_data)

        # Check that sectors are in alphabetical order
        assert result["sector_name"].tolist() == [
            "Financial Services",
            "Healthcare",
            "Technology",
        ]

    def test_sector_id_assignment(self):
        """Test that sector IDs are assigned sequentially starting from 1."""
        sector_data = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
            {"sector": "Financial Services"},
        ]

        result = process_sectors(sector_data)

        # Check that IDs start at 1 and are sequential
        assert result["sector_id"].tolist() == [1, 2, 3]

    def test_sector_hash_generation(self):
        """Test that sector hash is first 5 characters of SHA256 hash."""
        sector_data = [
            {"sector": "Technology"},
        ]

        result = process_sectors(sector_data)

        # Calculate expected hash
        expected_hash = hashlib.sha256("Technology".encode("utf-8")).hexdigest()[:5]
        assert result["sector_hash"].iloc[0] == expected_hash

    def test_sector_hash_length(self):
        """Test that sector hash is exactly 5 characters."""
        sector_data = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
        ]

        result = process_sectors(sector_data)

        # Check that all hashes are 5 characters long
        for sector_hash in result["sector_hash"]:
            assert len(sector_hash) == 5

    def test_empty_input(self):
        """Test processing of empty sector data."""
        sector_data = []

        result = process_sectors(sector_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["sector_id", "sector_hash", "sector_name"]

    def test_missing_sector_column(self):
        """Test handling of data without 'sector' column."""
        sector_data = [
            {"name": "Technology"},
            {"name": "Healthcare"},
        ]

        result = process_sectors(sector_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["sector_id", "sector_hash", "sector_name"]

    def test_duplicate_sectors(self):
        """Test processing of duplicate sector names."""
        sector_data = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
            {"sector": "Technology"},
        ]

        result = process_sectors(sector_data)

        # Both Technology entries should be included
        assert len(result) == 3
        # Check that sorting still works correctly
        tech_entries = result[result["sector_name"] == "Technology"]
        assert len(tech_entries) == 2

    def test_data_types(self):
        """Test that output columns have correct data types."""
        sector_data = [
            {"sector": "Technology"},
            {"sector": "Healthcare"},
        ]

        result = process_sectors(sector_data)

        # sector_id should be integer
        assert pd.api.types.is_integer_dtype(result["sector_id"])
        # sector_hash should be string
        assert pd.api.types.is_object_dtype(result["sector_hash"])
        # sector_name should be string
        assert pd.api.types.is_object_dtype(result["sector_name"])


class TestProcessIndustries:
    """Tests for process_industries function."""

    def test_basic_processing(self):
        """Test basic processing of industry data."""
        industry_data = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
            {"industry": "Banking"},
        ]

        result = process_industries(industry_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == [
            "industry_id",
            "industry_hash",
            "industry_name",
        ]

    def test_alphabetical_sorting(self):
        """Test that industries are sorted alphabetically before assigning IDs."""
        industry_data = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
            {"industry": "Banking"},
        ]

        result = process_industries(industry_data)

        # Check that industries are in alphabetical order
        assert result["industry_name"].tolist() == [
            "Banking",
            "Pharmaceuticals",
            "Software",
        ]

    def test_industry_id_assignment(self):
        """Test that industry IDs are assigned sequentially starting from 1."""
        industry_data = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
            {"industry": "Banking"},
        ]

        result = process_industries(industry_data)

        # Check that IDs start at 1 and are sequential
        assert result["industry_id"].tolist() == [1, 2, 3]

    def test_industry_hash_generation(self):
        """Test that industry hash is first 5 characters of SHA256 hash."""
        industry_data = [
            {"industry": "Software"},
        ]

        result = process_industries(industry_data)

        # Calculate expected hash
        expected_hash = hashlib.sha256("Software".encode("utf-8")).hexdigest()[:5]
        assert result["industry_hash"].iloc[0] == expected_hash

    def test_industry_hash_length(self):
        """Test that industry hash is exactly 5 characters."""
        industry_data = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
        ]

        result = process_industries(industry_data)

        # Check that all hashes are 5 characters long
        for industry_hash in result["industry_hash"]:
            assert len(industry_hash) == 5

    def test_empty_input(self):
        """Test processing of empty industry data."""
        industry_data = []

        result = process_industries(industry_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            "industry_id",
            "industry_hash",
            "industry_name",
        ]

    def test_missing_industry_column(self):
        """Test handling of data without 'industry' column."""
        industry_data = [
            {"name": "Software"},
            {"name": "Pharmaceuticals"},
        ]

        result = process_industries(industry_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            "industry_id",
            "industry_hash",
            "industry_name",
        ]

    def test_duplicate_industries(self):
        """Test processing of duplicate industry names."""
        industry_data = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
            {"industry": "Software"},
        ]

        result = process_industries(industry_data)

        # Both Software entries should be included
        assert len(result) == 3
        # Check that sorting still works correctly
        software_entries = result[result["industry_name"] == "Software"]
        assert len(software_entries) == 2

    def test_data_types(self):
        """Test that output columns have correct data types."""
        industry_data = [
            {"industry": "Software"},
            {"industry": "Pharmaceuticals"},
        ]

        result = process_industries(industry_data)

        # industry_id should be integer
        assert pd.api.types.is_integer_dtype(result["industry_id"])
        # industry_hash should be string
        assert pd.api.types.is_object_dtype(result["industry_hash"])
        # industry_name should be string
        assert pd.api.types.is_object_dtype(result["industry_name"])


class TestHashConsistency:
    """Test that hash generation is consistent across both functions."""

    def test_same_hash_for_same_string(self):
        """Test that the same string generates the same hash in both functions."""
        test_name = "Technology"

        sector_data = [{"sector": test_name}]
        industry_data = [{"industry": test_name}]

        sector_result = process_sectors(sector_data)
        industry_result = process_industries(industry_data)

        # The hash should be the same for the same string
        assert (
            sector_result["sector_hash"].iloc[0]
            == industry_result["industry_hash"].iloc[0]
        )
