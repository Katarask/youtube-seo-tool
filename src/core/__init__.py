"""Core analysis modules."""

from .autocomplete import AutocompleteScraper, scrape_autocomplete
from .youtube_api import YouTubeAPI, get_youtube_api
from .trends import TrendsAPI, get_youtube_trends, PYTRENDS_AVAILABLE
from .analyzer import KeywordAnalyzer, analyze_keyword, find_opportunities
from .apify_scraper import ApifyScraper, ScrapedVideo, APIFY_AVAILABLE
from .gemini_analyzer import GeminiAnalyzer, GEMINI_AVAILABLE
from .claude_analyzer import ClaudeAnalyzer, CommentSentiment, TitleSuggestion, VideoDecision, CLAUDE_AVAILABLE
from .video_validator import VideoValidator, VideoValidationResult, validate_video_idea, AI_PROVIDER

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
    # Apify Scraper
    "ApifyScraper",
    "ScrapedVideo",
    "APIFY_AVAILABLE",
    # AI Analyzers
    "GeminiAnalyzer",
    "GEMINI_AVAILABLE",
    "ClaudeAnalyzer",
    "CLAUDE_AVAILABLE",
    "CommentSentiment",
    "TitleSuggestion",
    "VideoDecision",
    # Video Validator
    "VideoValidator",
    "VideoValidationResult",
    "validate_video_idea",
    "AI_PROVIDER",
]
