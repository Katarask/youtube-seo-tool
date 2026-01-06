"""SQLite caching for API responses."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
from contextlib import contextmanager

from ..utils.config import config, get_cache_path


class Cache:
    """SQLite-based cache for API responses."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_cache_path()
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    cache_type TEXT DEFAULT 'general'
                )
            """)
            
            # Index for faster expiry checks
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _make_key(self, cache_type: str, identifier: str) -> str:
        """Create a cache key."""
        return f"{cache_type}:{identifier}"
    
    def get(self, cache_type: str, identifier: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            cache_type: Type of cached data (e.g., 'autocomplete', 'video', 'trends')
            identifier: Unique identifier for the data
            
        Returns:
            Cached value or None if not found/expired
        """
        key = self._make_key(cache_type, identifier)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(row["expires_at"])
            if datetime.now() > expires_at:
                # Expired, delete it
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return None
            
            return json.loads(row["value"])
    
    def set(
        self,
        cache_type: str,
        identifier: str,
        value: Any,
        ttl_hours: Optional[int] = None
    ):
        """
        Set a value in cache.
        
        Args:
            cache_type: Type of cached data
            identifier: Unique identifier
            value: Value to cache (must be JSON serializable)
            ttl_hours: Time to live in hours (uses config default if not specified)
        """
        key = self._make_key(cache_type, identifier)
        ttl = ttl_hours or config.cache_ttl_hours
        expires_at = datetime.now() + timedelta(hours=ttl)
        
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, expires_at, cache_type)
                VALUES (?, ?, ?, ?)
                """,
                (key, json.dumps(value), expires_at.isoformat(), cache_type)
            )
            conn.commit()
    
    def delete(self, cache_type: str, identifier: str):
        """Delete a specific cache entry."""
        key = self._make_key(cache_type, identifier)
        
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
    
    def clear_type(self, cache_type: str):
        """Clear all entries of a specific type."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE cache_type = ?", (cache_type,))
            conn.commit()
    
    def clear_expired(self):
        """Remove all expired entries."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache WHERE expires_at < ?", (datetime.now().isoformat(),))
            conn.commit()
    
    def clear_all(self):
        """Clear entire cache."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._get_connection() as conn:
            # Total entries
            total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            
            # By type
            by_type = {}
            cursor = conn.execute(
                "SELECT cache_type, COUNT(*) as count FROM cache GROUP BY cache_type"
            )
            for row in cursor:
                by_type[row["cache_type"]] = row["count"]
            
            # Expired count
            expired = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            ).fetchone()[0]
            
            return {
                "total_entries": total,
                "by_type": by_type,
                "expired_entries": expired,
            }


# Global cache instance
cache = Cache()
