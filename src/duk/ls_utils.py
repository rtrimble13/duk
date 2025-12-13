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
    if not sector_data:
        logger.warning("Empty sector_data input, returning empty DataFrame")
        return pd.DataFrame(columns=["sector_id", "sector_hash", "sector_name"])

    logger.debug(f"Processing {len(sector_data)} sector records")

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(sector_data)

    # Check if 'sector' column exists
    if "sector" not in df.columns:
        logger.warning("No 'sector' column found in sector_data")
        return pd.DataFrame(columns=["sector_id", "sector_hash", "sector_name"])

    # Extract sector names and sort alphabetically
    sectors = df["sector"].tolist()
    sectors_sorted = sorted(sectors)

    # Create new DataFrame with processed data
    processed_data = []
    for idx, sector_name in enumerate(sectors_sorted, start=1):
        # Generate SHA256 hash and take first 5 characters
        sector_hash = hashlib.sha256(sector_name.encode()).hexdigest()[:5]

        processed_data.append(
            {
                "sector_id": idx,
                "sector_hash": sector_hash,
                "sector_name": sector_name,
            }
        )

    result_df = pd.DataFrame(processed_data)
    logger.info(f"Processed {len(result_df)} sector records")

    return result_df


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
    if not industry_data:
        logger.warning("Empty industry_data input, returning empty DataFrame")
        return pd.DataFrame(columns=["industry_id", "industry_hash", "industry_name"])

    logger.debug(f"Processing {len(industry_data)} industry records")

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(industry_data)

    # Check if 'industry' column exists
    if "industry" not in df.columns:
        logger.warning("No 'industry' column found in industry_data")
        return pd.DataFrame(columns=["industry_id", "industry_hash", "industry_name"])

    # Extract industry names and sort alphabetically
    industries = df["industry"].tolist()
    industries_sorted = sorted(industries)

    # Create new DataFrame with processed data
    processed_data = []
    for idx, industry_name in enumerate(industries_sorted, start=1):
        # Generate SHA256 hash and take first 5 characters
        industry_hash = hashlib.sha256(industry_name.encode()).hexdigest()[:5]

        processed_data.append(
            {
                "industry_id": idx,
                "industry_hash": industry_hash,
                "industry_name": industry_name,
            }
        )

    result_df = pd.DataFrame(processed_data)
    logger.info(f"Processed {len(result_df)} industry records")

    return result_df
