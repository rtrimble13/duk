"""
List utilities for processing sector and industry list data.

This module provides functions for processing sector and industry
list data retrieved from APIs.
"""

import hashlib
import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def _process_list_data(
    data: List[Dict[str, Any]],
    field_name: str,
    id_col: str,
    hash_col: str,
    name_col: str,
) -> pd.DataFrame:
    """
    Generic function to process list data with sorting and hash generation.

    Args:
        data: List of dictionaries containing the data
        field_name: Name of the field in input data (e.g., 'sector', 'industry')
        id_col: Name for the ID column in output (e.g., 'sector_id')
        hash_col: Name for the hash column in output (e.g., 'sector_hash')
        name_col: Name for the name column in output (e.g., 'sector_name')

    Returns:
        pandas DataFrame with three columns: id, hash, and name
    """
    if not data:
        logger.warning(f"Empty {field_name} data input, returning empty DataFrame")
        return pd.DataFrame(columns=[id_col, hash_col, name_col])

    logger.debug(f"Processing {len(data)} {field_name} records")

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(data)

    # Check if field exists
    if field_name not in df.columns:
        logger.warning(f"No '{field_name}' column found in data")
        return pd.DataFrame(columns=[id_col, hash_col, name_col])

    # Extract names and sort alphabetically
    names = df[field_name].tolist()
    names_sorted = sorted(names)

    # Create new DataFrame with processed data
    processed_data = []
    for idx, name in enumerate(names_sorted, start=1):
        # Generate SHA256 hash and take first 5 characters
        name_hash = hashlib.sha256(name.encode()).hexdigest()[:5]

        processed_data.append(
            {
                id_col: idx,
                hash_col: name_hash,
                name_col: name,
            }
        )

    result_df = pd.DataFrame(processed_data)
    logger.info(f"Processed {len(result_df)} {field_name} records")

    return result_df


def process_sectors(sector_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process sector list API data into a structured DataFrame.

    Takes the output of sector_list_api and converts it into a DataFrame
    with sector_id, sector_hash, and sector_name columns. Sectors are
    sorted alphabetically before assigning IDs.

    Args:
        sector_data: List of dictionaries containing sector information,
            as returned by sector_list_api. Each dictionary should
            contain a 'sector' field.

    Returns:
        pandas DataFrame with columns:
        - sector_id (int): Sequential ID starting from 1, assigned after
          alphabetical sorting
        - sector_hash (str): First 5 characters of SHA256 hash of sector name
        - sector_name (str): Name of the sector

    Example:
        >>> from duk.fmp_api import sector_list_api
        >>> sectors = sector_list_api("your_api_key")
        >>> df = process_sectors(sectors)
        >>> print(df.head())
    """
    return _process_list_data(
        data=sector_data,
        field_name="sector",
        id_col="sector_id",
        hash_col="sector_hash",
        name_col="sector_name",
    )


def process_industries(industry_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process industry list API data into a structured DataFrame.

    Takes the output of industry_list_api and converts it into a DataFrame
    with industry_id, industry_hash, and industry_name columns. Industries
    are sorted alphabetically before assigning IDs.

    Args:
        industry_data: List of dictionaries containing industry information,
            as returned by industry_list_api. Each dictionary should
            contain an 'industry' field.

    Returns:
        pandas DataFrame with columns:
        - industry_id (int): Sequential ID starting from 1, assigned after
          alphabetical sorting
        - industry_hash (str): First 5 characters of SHA256 hash of industry name
        - industry_name (str): Name of the industry

    Example:
        >>> from duk.fmp_api import industry_list_api
        >>> industries = industry_list_api("your_api_key")
        >>> df = process_industries(industries)
        >>> print(df.head())
    """
    return _process_list_data(
        data=industry_data,
        field_name="industry",
        id_col="industry_id",
        hash_col="industry_hash",
        name_col="industry_name",
    )
