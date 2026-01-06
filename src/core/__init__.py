"""Core analysis modules."""

from .autocomplete import AutocompleteScraper, scrape_autocomplete
from .youtube_api import YouTubeAPI, get_youtube_api
from .trends import TrendsAPI, get_youtube_trends, PYTRENDS_AVAILABLE
from .analyzer import KeywordAnalyzer, analyze_keyword, find_opportunities

__all__ = [
    "AutocompleteScraper",
    "scrape_autocomplete",
    "YouTubeAPI",
    "get_youtube_api",
    "TrendsAPI",
    "get_youtube_trends",
    "PYTRENDS_AVAILABLE",
    "KeywordAnalyzer",
    "analyze_keyword",
    "find_opportunities",
]
