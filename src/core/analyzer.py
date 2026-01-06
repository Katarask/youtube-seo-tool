"""Main analyzer that combines all data sources for keyword analysis."""

from typing import Optional
from datetime import datetime

from ..data.models import (
    KeywordAnalysis,
    KeywordSuggestion,
    TrendData,
    DemandMetrics,
    SupplyMetrics,
    VideoInfo,
)
from ..data.cache import cache
from .autocomplete import AutocompleteScraper
from .youtube_api import YouTubeAPI
from .trends import TrendsAPI, PYTRENDS_AVAILABLE
from ..utils.config import config
from ..utils.logger import logger
from ..utils.validators import validate_keyword, validate_keywords, ValidationError
from ..constants import (
    TREND_DEFAULT_INTEREST,
    MAX_SUGGESTIONS_TO_ANALYZE,
)


class KeywordAnalyzer:
    """
    Main analyzer that combines autocomplete, YouTube API, and Google Trends
    to provide comprehensive keyword analysis with Gap Score.
    """
    
    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        language: str = "en",
        region: str = "us"
    ):
        self.language = language
        self.region = region
        
        # Initialize components
        self.autocomplete = AutocompleteScraper(language=language, region=region)
        
        api_key = youtube_api_key or config.youtube_api_key
        if api_key:
            self.youtube = YouTubeAPI(api_key)
        else:
            self.youtube = None
            logger.warning("No YouTube API key. Some features will be limited.")

        if PYTRENDS_AVAILABLE:
            self.trends = TrendsAPI()
        else:
            self.trends = None
            logger.warning("pytrends not available. Trend data will use defaults.")
    
    def analyze_keyword(
        self,
        keyword: str,
        include_suggestions: bool = True,
        expand_suggestions: bool = False,
        use_cache: bool = True
    ) -> KeywordAnalysis:
        """
        Perform comprehensive analysis on a keyword.

        Args:
            keyword: The keyword to analyze
            include_suggestions: Whether to fetch autocomplete suggestions
            expand_suggestions: Whether to do prefix/suffix expansion
            use_cache: Whether to use cached results

        Returns:
            KeywordAnalysis object with all metrics

        Raises:
            ValidationError: If keyword is invalid
        """
        # Validate and sanitize keyword
        keyword = validate_keyword(keyword)
        logger.debug(f"Analyzing keyword: {keyword}")

        analysis = KeywordAnalysis(keyword=keyword)
        
        # 1. Get autocomplete suggestions
        if include_suggestions:
            if expand_suggestions:
                analysis.suggestions = self.autocomplete.expand_suggestions(
                    keyword, use_cache=use_cache
                )
            else:
                analysis.suggestions = self.autocomplete.get_suggestions(
                    keyword, use_cache=use_cache
                )
        
        # 2. Get Google Trends data
        if self.trends:
            analysis.trend_data = self.trends.get_trend_data(
                keyword, use_cache=use_cache
            )
        else:
            # Default trend data if pytrends not available
            analysis.trend_data = TrendData(
                keyword=keyword,
                average_interest=TREND_DEFAULT_INTEREST,
                trend_direction=0,
            )

        trend_index = analysis.trend_data.average_interest if analysis.trend_data else TREND_DEFAULT_INTEREST
        
        # 3. Get YouTube demand data
        if self.youtube:
            analysis.demand, analysis.top_videos = self.youtube.analyze_keyword_demand(
                keyword,
                trend_index=trend_index,
                use_cache=use_cache
            )
            
            # 4. Get YouTube supply data
            analysis.supply = self.youtube.analyze_keyword_supply(
                keyword, use_cache=use_cache
            )
        else:
            # Minimal data without API
            analysis.demand = DemandMetrics(
                trend_index=trend_index,
                avg_views_top_10=0,
                total_views_top_10=0,
                avg_engagement_rate=0,
            )
            analysis.supply = SupplyMetrics(
                videos_last_30_days=0,
                videos_last_7_days=0,
                avg_channel_subscribers=0,
                small_channels_in_top_10=0,
                avg_video_age_days=0,
            )

        logger.debug(f"Analysis complete for '{keyword}': gap_score={analysis.gap_score:.2f}")
        return analysis
    
    def analyze_keywords(
        self,
        keywords: list[str],
        include_suggestions: bool = False,
        use_cache: bool = True,
        progress_callback=None
    ) -> list[KeywordAnalysis]:
        """
        Analyze multiple keywords.

        Args:
            keywords: List of keywords to analyze
            include_suggestions: Whether to fetch suggestions (slower)
            use_cache: Whether to use cached results
            progress_callback: Optional callback function(current, total, keyword)

        Returns:
            List of KeywordAnalysis objects

        Raises:
            ValidationError: If any keyword is invalid
        """
        # Validate all keywords upfront
        keywords = validate_keywords(keywords)
        logger.info(f"Analyzing {len(keywords)} keywords")

        results = []
        total = len(keywords)
        
        for i, keyword in enumerate(keywords):
            if progress_callback:
                progress_callback(i + 1, total, keyword)
            
            analysis = self.analyze_keyword(
                keyword,
                include_suggestions=include_suggestions,
                use_cache=use_cache
            )
            results.append(analysis)
        
        return results
    
    def find_opportunities(
        self,
        seed_keyword: str,
        min_gap_score: float = 5.0,
        max_results: int = 20,
        use_cache: bool = True
    ) -> list[KeywordAnalysis]:
        """
        Find keyword opportunities starting from a seed keyword.
        
        1. Expands seed keyword with autocomplete
        2. Analyzes each suggestion
        3. Filters by gap score
        4. Returns sorted by opportunity
        
        Args:
            seed_keyword: Starting keyword
            min_gap_score: Minimum gap score to include
            max_results: Maximum results to return
            use_cache: Whether to use cached results
            
        Returns:
            List of KeywordAnalysis sorted by gap score
        """
        # Get expanded suggestions
        suggestions = self.autocomplete.expand_suggestions(
            seed_keyword,
            prefixes=True,
            suffixes=True,
            use_cache=use_cache
        )
        
        # Limit to avoid quota exhaustion
        keywords_to_analyze = [seed_keyword] + [s.keyword for s in suggestions[:MAX_SUGGESTIONS_TO_ANALYZE]]
        
        # Analyze all keywords
        results = self.analyze_keywords(
            keywords_to_analyze,
            include_suggestions=False,
            use_cache=use_cache
        )
        
        # Filter by minimum gap score
        filtered = [r for r in results if r.gap_score >= min_gap_score]
        
        # Sort by gap score (highest first)
        filtered.sort(key=lambda x: x.gap_score, reverse=True)
        
        return filtered[:max_results]
    
    def compare_keywords(
        self,
        keywords: list[str],
        use_cache: bool = True
    ) -> list[KeywordAnalysis]:
        """
        Compare multiple keywords side by side.
        
        Args:
            keywords: List of keywords to compare
            use_cache: Whether to use cached results
            
        Returns:
            List of KeywordAnalysis sorted by gap score
        """
        results = self.analyze_keywords(keywords, use_cache=use_cache)
        results.sort(key=lambda x: x.gap_score, reverse=True)
        return results
    
    @property
    def quota_used(self) -> int:
        """Get YouTube API quota used this session."""
        if self.youtube:
            return self.youtube.quota_used
        return 0


# Convenience function
def analyze_keyword(keyword: str, **kwargs) -> KeywordAnalysis:
    """
    Convenience function for quick keyword analysis.
    
    Args:
        keyword: The keyword to analyze
        **kwargs: Additional arguments for KeywordAnalyzer.analyze_keyword
        
    Returns:
        KeywordAnalysis object
    """
    analyzer = KeywordAnalyzer()
    return analyzer.analyze_keyword(keyword, **kwargs)


def find_opportunities(seed_keyword: str, **kwargs) -> list[KeywordAnalysis]:
    """
    Convenience function to find keyword opportunities.
    
    Args:
        seed_keyword: Starting keyword
        **kwargs: Additional arguments
        
    Returns:
        List of opportunities sorted by gap score
    """
    analyzer = KeywordAnalyzer()
    return analyzer.find_opportunities(seed_keyword, **kwargs)
