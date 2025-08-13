"""
SQLite caching layer for duk data downloads.
"""

import json
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import os

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages SQLite cache for API data."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache manager.

        Args:
            cache_dir: Directory to store cache database. Defaults to var/ directory.
        """
        if cache_dir is None:
            # Default cache directory logic based on issue requirements
            if Path("var").exists():
                # Local repository mode
                cache_dir = "var"
            else:
                # Package install mode - use ~/var/duk/
                cache_dir = os.path.expanduser("~/var/duk")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "duk_cache.db"
        self._init_database()

    def _init_database(self):
        """Initialize the cache database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Treasury rates cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS treasury_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Price history cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS price_history_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    ticker TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    data_type TEXT NOT NULL,  -- 'price', 'dividend', 'split'
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # List data cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS list_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    list_type TEXT NOT NULL,  -- list type: index, sector, etc.
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_treasury_cache_key
                ON treasury_cache(cache_key)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_treasury_dates
                ON treasury_cache(start_date, end_date)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_price_cache_key
                ON price_history_cache(cache_key)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_price_ticker_dates
                ON price_history_cache(ticker, start_date, end_date, data_type)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_list_cache_key
                ON list_cache(cache_key)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_list_type
                ON list_cache(list_type)
            """
            )

            conn.commit()
            logger.debug(f"Cache database initialized at {self.db_path}")

    def _generate_cache_key(self, **kwargs) -> str:
        """Generate a consistent cache key from parameters."""
        # Sort parameters for consistent key generation
        key_data = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_treasury_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get treasury data from cache if available."""
        cache_key = self._generate_cache_key(
            start_date=start_date, end_date=end_date, days=days, data_type="treasury"
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT data FROM treasury_cache
                    WHERE cache_key = ?
                """,
                    (cache_key,),
                )

                result = cursor.fetchone()
                if result:
                    # Update access time
                    cursor.execute(
                        """
                        UPDATE treasury_cache
                        SET accessed_at = CURRENT_TIMESTAMP
                        WHERE cache_key = ?
                    """,
                        (cache_key,),
                    )
                    conn.commit()

                    data = json.loads(result[0])
                    logger.debug(f"Cache hit for treasury data: {cache_key}")
                    return data

                logger.debug(f"Cache miss for treasury data: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Error reading from treasury cache: {e}")
            return None

    def store_treasury_data(
        self,
        data: List[Dict[str, Any]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ):
        """Store treasury data in cache."""
        cache_key = self._generate_cache_key(
            start_date=start_date, end_date=end_date, days=days, data_type="treasury"
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO treasury_cache
                    (cache_key, start_date, end_date, data, created_at, accessed_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    (cache_key, start_date, end_date, json.dumps(data)),
                )
                conn.commit()
                logger.debug(f"Stored treasury data in cache: {cache_key}")

        except Exception as e:
            logger.error(f"Error storing treasury data in cache: {e}")

    def get_price_data(
        self,
        ticker: str,
        data_type: str = "price",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get price data from cache if available."""
        cache_key = self._generate_cache_key(
            ticker=ticker.upper(),
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT data FROM price_history_cache
                    WHERE cache_key = ?
                """,
                    (cache_key,),
                )

                result = cursor.fetchone()
                if result:
                    # Update access time
                    cursor.execute(
                        """
                        UPDATE price_history_cache
                        SET accessed_at = CURRENT_TIMESTAMP
                        WHERE cache_key = ?
                    """,
                        (cache_key,),
                    )
                    conn.commit()

                    data = json.loads(result[0])
                    logger.debug(
                        f"Cache hit for {ticker} {data_type} data: {cache_key}"
                    )
                    return data

                logger.debug(f"Cache miss for {ticker} {data_type} data: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Error reading from price cache: {e}")
            return None

    def store_price_data(
        self,
        ticker: str,
        data: List[Dict[str, Any]],
        data_type: str = "price",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
    ):
        """Store price data in cache."""
        cache_key = self._generate_cache_key(
            ticker=ticker.upper(),
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO price_history_cache
                    (cache_key, ticker, start_date, end_date, data_type, data,
                     created_at, accessed_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    (
                        cache_key,
                        ticker.upper(),
                        start_date,
                        end_date,
                        data_type,
                        json.dumps(data),
                    ),
                )
                conn.commit()
                logger.debug(f"Stored {ticker} {data_type} data in cache: {cache_key}")

        except Exception as e:
            logger.error(f"Error storing {ticker} {data_type} data in cache: {e}")

    def clear_cache(self, older_than_days: int = 30):
        """Clear cache entries older than specified days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = (
                    datetime.now() - timedelta(days=older_than_days)
                ).isoformat()

                cursor.execute(
                    """
                    DELETE FROM treasury_cache
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                cursor.execute(
                    """
                    DELETE FROM price_history_cache
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                conn.commit()
                logger.info(f"Cleared cache entries older than {older_than_days} days")

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_list_data(self, list_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get list data from cache if available."""
        try:
            cache_key = self._generate_cache_key(list_type=list_type)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT data FROM list_cache
                    WHERE cache_key = ?
                """,
                    (cache_key,),
                )

                result = cursor.fetchone()
                if result:
                    # Update accessed_at
                    cursor.execute(
                        """
                        UPDATE list_cache
                        SET accessed_at = CURRENT_TIMESTAMP
                        WHERE cache_key = ?
                    """,
                        (cache_key,),
                    )
                    conn.commit()

                    data = json.loads(result[0])
                    logger.debug(f"Cache hit for list data: {list_type}")
                    return data

                logger.debug(f"Cache miss for list data: {list_type}")
                return None

        except Exception as e:
            logger.error(f"Error reading from list cache: {e}")
            return None

    def store_list_data(self, list_type: str, data: List[Dict[str, Any]]):
        """Store list data in cache."""
        try:
            cache_key = self._generate_cache_key(list_type=list_type)
            data_json = json.dumps(data)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO list_cache
                    (cache_key, list_type, data, created_at, accessed_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    (cache_key, list_type, data_json),
                )

                conn.commit()
                logger.debug(f"Stored list data in cache: {list_type}")

        except Exception as e:
            logger.error(f"Error storing list data in cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM treasury_cache")
                treasury_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM price_history_cache")
                price_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM list_cache")
                list_count = cursor.fetchone()[0]

                return {
                    "treasury_entries": treasury_count,
                    "price_history_entries": price_count,
                    "list_entries": list_count,
                    "cache_file": str(self.db_path),
                    "cache_size_bytes": (
                        self.db_path.stat().st_size if self.db_path.exists() else 0
                    ),
                }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
