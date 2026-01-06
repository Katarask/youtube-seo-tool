"""Notion integration for exporting keyword analysis results."""

from datetime import datetime
from typing import Optional
from notion_client import Client
from notion_client.errors import APIResponseError

from ..data.models import KeywordAnalysis, GapScoreRating
from ..utils.config import config


class NotionExporter:
    """
    Export keyword analysis results to Notion.
    
    Creates a database with all metrics and presents results
    as a mini-presentation with charts and insights.
    """
    
    # Database properties schema
    DATABASE_PROPERTIES = {
        "Keyword": {"title": {}},
        "Gap Score": {"number": {"format": "number"}},
        "Rating": {
            "select": {
                "options": [
                    {"name": "🟢 Excellent", "color": "green"},
                    {"name": "🟡 Good", "color": "yellow"},
                    {"name": "🔴 Poor", "color": "red"},
                ]
            }
        },
        "Demand Score": {"number": {"format": "number"}},
        "Supply Score": {"number": {"format": "number"}},
        "Trend Index": {"number": {"format": "number"}},
        "Trend Direction": {"rich_text": {}},
        "Avg Views (Top 10)": {"number": {"format": "number"}},
        "Videos (30 days)": {"number": {"format": "number"}},
        "Avg Channel Size": {"number": {"format": "number"}},
        "Small Channels %": {"number": {"format": "number"}},
        "Avg Video Age (days)": {"number": {"format": "number"}},
        "Suggestions Count": {"number": {"format": "number"}},
        "Analyzed At": {"date": {}},
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.notion_api_key
        if not self.api_key:
            raise ValueError("Notion API key is required. Set NOTION_API_KEY in .env")
        
        self.client = Client(auth=self.api_key)
        self.database_id = config.notion_database_id
    
    def create_database(
        self,
        parent_page_id: str,
        title: str = "YouTube Keyword Research"
    ) -> str:
        """
        Create a new database for keyword research.
        
        Args:
            parent_page_id: The page ID where the database will be created
            title: Database title
            
        Returns:
            The created database ID
        """
        try:
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": title}}],
                properties=self.DATABASE_PROPERTIES,
                icon={"type": "emoji", "emoji": "🎯"},
            )
            
            self.database_id = response["id"]
            print(f"Created Notion database: {self.database_id}")
            return self.database_id
            
        except APIResponseError as e:
            print(f"Error creating database: {e}")
            raise
    
    def _get_rating_text(self, rating: GapScoreRating) -> str:
        """Convert rating enum to display text."""
        if rating == GapScoreRating.EXCELLENT:
            return "🟢 Excellent"
        elif rating == GapScoreRating.GOOD:
            return "🟡 Good"
        return "🔴 Poor"
