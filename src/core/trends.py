"""Google Trends integration for YouTube search trends."""

import time
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from ..data.models import TrendData
from ..data.cache import cache
from ..utils.rate_limiter import rate_limiters
from ..utils.logger import trends_logger as logger
from ..constants import (
    CACHE_TTL_TRENDS,
    TREND_DEFAULT_INTEREST,
)

# Import pytrends with error handling
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logger.warning("pytrends not installed. Google Trends features disabled.")


class TrendsAPI:
    """
    Google Trends API wrapper for YouTube-specific trends.
    
    Uses pytrends (unofficial API) to fetch trend data with
    the gprop='youtube' filter for YouTube Search.
    """
    
    def __init__(
        self,
        language: str = "en-US",
        timezone: int = 360,
        proxy: Optional[str] = None,
        retries: int = 3,
        backoff_factor: float = 0.5
    ):
        if not PYTRENDS_AVAILABLE:
            raise ImportError("pytrends is required. Install with: pip install pytrends")
        
        self.language = language
        self.timezone = timezone
        
        # Initialize pytrends with retry logic
        proxies = [proxy] if proxy else []
        self.pytrends = TrendReq(
            hl=language,
            tz=timezone,
            timeout=(10, 25),
            proxies=proxies,
            retries=retries,
            backoff_factor=backoff_factor,
        )
    
    def get_trend_data(
        self,
        keyword: str,
        timeframe: str = "today 12-m",
        use_cache: bool = True
    ) -> Optional[TrendData]:
        """
        Get YouTube-specific trend data for a keyword.
        
        Args:
            keyword: The keyword to analyze
            timeframe: Time range (e.g., 'today 12-m', 'today 3-m', 'today 5-y')
            use_cache: Whether to use cached results
            
        Returns:
            TrendData object or None if failed
        """
        cache_key = f"{keyword}_{timeframe}"
        
        if use_cache:
            cached = cache.get("trends", cache_key)
            if cached:
                return TrendData(
                    keyword=cached["keyword"],
                    interest_over_time=[
                        (datetime.fromisoformat(d), v) 
                        for d, v in cached["interest_over_time"]
                    ],
                    average_interest=cached["average_interest"],
                    trend_direction=cached["trend_direction"],
                    peak_month=cached.get("peak_month"),
                )
        
        rate_limiters.wait("trends")
        
        try:
            # Build payload for YouTube search
            self.pytrends.build_payload(
                kw_list=[keyword],
                cat=0,  # All categories
                timeframe=timeframe,
                geo="",  # Worldwide
                gprop="youtube"  # YouTube Search specifically!
            )
            
            # Get interest over time
            df = self.pytrends.interest_over_time()
            
            if df.empty:
                return TrendData(
                    keyword=keyword,
                    interest_over_time=[],
                    average_interest=0,
                    trend_direction=0,
                )
            
            # Process data
            interest_data = []
            for date, row in df.iterrows():
                if keyword in row:
                    interest_data.append((date.to_pydatetime(), int(row[keyword])))
            
            if not interest_data:
                return TrendData(
                    keyword=keyword,
                    interest_over_time=[],
                    average_interest=0,
                    trend_direction=0,
                )
            
            # Calculate metrics
            values = [v for _, v in interest_data]
            avg_interest = sum(values) / len(values)
            
            # Calculate trend direction (compare first half vs second half)
            mid = len(values) // 2
            first_half_avg = sum(values[:mid]) / max(1, mid)
            second_half_avg = sum(values[mid:]) / max(1, len(values) - mid)
            
            if first_half_avg > 0:
                trend_direction = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            else:
                trend_direction = 0
            
            # Find peak month
            peak_idx = values.index(max(values))
            peak_date = interest_data[peak_idx][0]
            peak_month = peak_date.strftime("%B %Y")
            
            trend_data = TrendData(
                keyword=keyword,
                interest_over_time=interest_data,
                average_interest=avg_interest,
                trend_direction=trend_direction,
                peak_month=peak_month,
            )
            
            # Cache results
            cache.set("trends", cache_key, {
                "keyword": trend_data.keyword,
                "interest_over_time": [
                    (d.isoformat(), v) for d, v in trend_data.interest_over_time
                ],
                "average_interest": trend_data.average_interest,
                "trend_direction": trend_data.trend_direction,
                "peak_month": trend_data.peak_month,
            }, ttl_hours=CACHE_TTL_TRENDS)

            logger.debug(f"Trends for '{keyword}': avg={trend_data.average_interest:.1f}, dir={trend_data.trend_direction:.1f}%")
            return trend_data

        except Exception as e:
            logger.error(f"Error fetching trends for '{keyword}': {e}")
            # Return a default TrendData instead of None
            return TrendData(
                keyword=keyword,
                interest_over_time=[],
                average_interest=TREND_DEFAULT_INTEREST,
                trend_direction=0,
            )
    
    def compare_keywords(
        self,
        keywords: list[str],
        timeframe: str = "today 12-m",
        use_cache: bool = True
    ) -> dict[str, TrendData]:
        """
        Compare multiple keywords' trends.
        
        Args:
            keywords: List of keywords (max 5)
            timeframe: Time range
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary mapping keyword to TrendData
        """
        # Limit to 5 keywords (Google Trends limit)
        keywords = keywords[:5]
        
        results = {}
        
        # Check cache first
        uncached = []
        for kw in keywords:
            cache_key = f"compare_{kw}_{timeframe}"
            if use_cache:
                cached = cache.get("trends_compare", cache_key)
                if cached:
                    results[kw] = TrendData(
                        keyword=cached["keyword"],
                        interest_over_time=[
                            (datetime.fromisoformat(d), v) 
                            for d, v in cached["interest_over_time"]
                        ],
                        average_interest=cached["average_interest"],
                        trend_direction=cached["trend_direction"],
                        peak_month=cached.get("peak_month"),
                    )
                    continue
            uncached.append(kw)
        
        if not uncached:
            return results
        
        rate_limiters.wait("trends")
        
        try:
            self.pytrends.build_payload(
                kw_list=uncached,
                cat=0,
                timeframe=timeframe,
                geo="",
                gprop="youtube"
            )
            
            df = self.pytrends.interest_over_time()
            
            if df.empty:
                for kw in uncached:
                    results[kw] = TrendData(keyword=kw)
                return results
            
            for kw in uncached:
                if kw not in df.columns:
                    results[kw] = TrendData(keyword=kw)
                    continue
                
                interest_data = []
                for date, row in df.iterrows():
                    interest_data.append((date.to_pydatetime(), int(row[kw])))
                
                values = [v for _, v in interest_data]
                avg_interest = sum(values) / len(values) if values else 0
                
                mid = len(values) // 2 if values else 0
                if mid > 0:
                    first_half = sum(values[:mid]) / mid
                    second_half = sum(values[mid:]) / max(1, len(values) - mid)
                    trend_direction = ((second_half - first_half) / max(1, first_half)) * 100
                else:
                    trend_direction = 0
                
                peak_month = None
                if values:
                    peak_idx = values.index(max(values))
                    peak_month = interest_data[peak_idx][0].strftime("%B %Y")
                
                trend_data = TrendData(
                    keyword=kw,
                    interest_over_time=interest_data,
                    average_interest=avg_interest,
                    trend_direction=trend_direction,
                    peak_month=peak_month,
                )
                
                results[kw] = trend_data
                
                # Cache individual result
                cache.set("trends_compare", f"compare_{kw}_{timeframe}", {
                    "keyword": trend_data.keyword,
                    "interest_over_time": [
                        (d.isoformat(), v) for d, v in trend_data.interest_over_time
                    ],
                    "average_interest": trend_data.average_interest,
                    "trend_direction": trend_data.trend_direction,
                    "peak_month": trend_data.peak_month,
                }, ttl_hours=CACHE_TTL_TRENDS)

            return results

        except Exception as e:
            logger.error(f"Error comparing keywords: {e}")
            for kw in uncached:
                results[kw] = TrendData(keyword=kw, average_interest=TREND_DEFAULT_INTEREST)
            return results
    
    def get_related_queries(
        self,
        keyword: str,
        use_cache: bool = True
    ) -> dict[str, list[dict]]:
        """
        Get related queries for a keyword.
        
        Returns both 'top' and 'rising' related queries.
        
        Args:
            keyword: The keyword to analyze
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with 'top' and 'rising' lists
        """
        cache_key = f"related_{keyword}"
        
        if use_cache:
            cached = cache.get("trends_related", cache_key)
            if cached:
                return cached
        
        rate_limiters.wait("trends")
        
        try:
            self.pytrends.build_payload(
                kw_list=[keyword],
                cat=0,
                timeframe="today 12-m",
                geo="",
                gprop="youtube"
            )
            
            related = self.pytrends.related_queries()
            
            result = {"top": [], "rising": []}
            
            if keyword in related:
                kw_data = related[keyword]
                
                if kw_data.get("top") is not None and not kw_data["top"].empty:
                    result["top"] = kw_data["top"].to_dict("records")
                
                if kw_data.get("rising") is not None and not kw_data["rising"].empty:
                    result["rising"] = kw_data["rising"].to_dict("records")
            
            cache.set("trends_related", cache_key, result, ttl_hours=CACHE_TTL_TRENDS)
            return result

        except Exception as e:
            logger.error(f"Error getting related queries for '{keyword}': {e}")
            return {"top": [], "rising": []}


# Convenience function
def get_youtube_trends(
    keyword: str,
    timeframe: str = "today 12-m"
) -> Optional[TrendData]:
    """
    Convenience function to get YouTube trend data.
    
    Args:
        keyword: The keyword to analyze
        timeframe: Time range
        
    Returns:
        TrendData object or None
    """
    if not PYTRENDS_AVAILABLE:
        return TrendData(keyword=keyword, average_interest=TREND_DEFAULT_INTEREST)
    
    api = TrendsAPI()
    return api.get_trend_data(keyword, timeframe)
