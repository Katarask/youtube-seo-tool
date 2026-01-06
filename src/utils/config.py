"""Configuration management for YouTube SEO Tool."""

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    
    # YouTube API
    youtube_api_key: str = ""
    
    # Notion
    notion_api_key: str = ""
    notion_database_id: str = ""
    
    # Google Trends
    trends_proxy: Optional[str] = None
    
    # Cache
    cache_ttl_hours: int = 24
    cache_db_path: str = "cache.db"
    
    # Rate Limiting
    youtube_requests_per_day: int = 100  # Conservative to stay under 10k quota
    trends_requests_per_minute: int = 10
    
    # Analysis Settings
    top_videos_count: int = 10
    recent_days_supply: int = 30
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            notion_api_key=os.getenv("NOTION_API_KEY", ""),
            notion_database_id=os.getenv("NOTION_DATABASE_ID", ""),
            trends_proxy=os.getenv("TRENDS_PROXY"),
            cache_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.youtube_api_key:
            errors.append("YOUTUBE_API_KEY is required")
        
        return errors
    
    @property
    def has_notion(self) -> bool:
        """Check if Notion integration is configured."""
        return bool(self.notion_api_key)


# Global config instance
config = Config.from_env()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_cache_path() -> Path:
    """Get the cache database path."""
    return get_project_root() / config.cache_db_path
