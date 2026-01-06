"""YouTube Data API v3 handler for video and channel data."""

from datetime import datetime, timedelta
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..data.models import VideoInfo, DemandMetrics, SupplyMetrics
from ..data.cache import cache
from ..utils.config import config
from ..utils.rate_limiter import rate_limiters


class YouTubeAPI:
    """
    Handler for YouTube Data API v3.
    
    Manages quota efficiently and provides high-level methods
    for keyword research.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.youtube_api_key
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY in .env")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self._quota_used = 0
    
    @property
    def quota_used(self) -> int:
        """Get approximate quota units used this session."""
        return self._quota_used
    
    def _track_quota(self, units: int):
        """Track quota usage."""
        self._quota_used += units
    
    def search_videos(
        self,
        keyword: str,
        max_results: int = 10,
        order: str = "relevance",
        published_after: Optional[datetime] = None,
        published_before: Optional[datetime] = None,
        use_cache: bool = True
    ) -> list[dict]:
        """
        Search for videos by keyword.
        
        Args:
            keyword: Search query
            max_results: Number of results (max 50)
            order: Sort order ('relevance', 'date', 'viewCount', 'rating')
            published_after: Filter by publish date
            published_before: Filter by publish date
            use_cache: Whether to use cached results
            
        Returns:
            List of video data dictionaries
            
        Quota cost: 100 units per call
        """
        cache_key = f"{keyword}_{order}_{max_results}_{published_after}_{published_before}"
        
        if use_cache:
            cached = cache.get("search", cache_key)
            if cached:
                return cached
        
        rate_limiters.wait("youtube")
        
        try:
            request_params = {
                "q": keyword,
                "part": "snippet",
                "type": "video",
                "maxResults": min(max_results, 50),
                "order": order,
            }
            
            if published_after:
                request_params["publishedAfter"] = published_after.isoformat() + "Z"
            if published_before:
                request_params["publishedBefore"] = published_before.isoformat() + "Z"
            
            request = self.youtube.search().list(**request_params)
            response = request.execute()
            
            self._track_quota(100)
            
            videos = []
            for item in response.get("items", []):
                videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "channel_id": item["snippet"]["channelId"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"],
                    "description": item["snippet"].get("description", ""),
                })
            
            if videos:
                cache.set("search", cache_key, videos, ttl_hours=12)
            
            return videos
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
    
    def get_video_details(
        self,
        video_ids: list[str],
        use_cache: bool = True
    ) -> list[VideoInfo]:
        """
        Get detailed information for videos.
        
        Args:
            video_ids: List of video IDs
            use_cache: Whether to use cached results
            
        Returns:
            List of VideoInfo objects
            
        Quota cost: 1 unit per call (can batch up to 50)
        """
        # Check cache first
        results = []
        uncached_ids = []
        
        for vid in video_ids:
            if use_cache:
                cached = cache.get("video", vid)
                if cached:
                    results.append(VideoInfo(**cached))
                    continue
            uncached_ids.append(vid)
        
        if not uncached_ids:
            return results
        
        rate_limiters.wait("youtube")
        
        try:
            # Batch request (up to 50 IDs)
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=",".join(uncached_ids[:50])
            )
            response = request.execute()
            
            self._track_quota(1)
            
            for item in response.get("items", []):
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                
                video_info = VideoInfo(
                    video_id=item["id"],
                    title=snippet.get("title", ""),
                    channel_id=snippet.get("channelId", ""),
                    channel_title=snippet.get("channelTitle", ""),
                    published_at=datetime.fromisoformat(
                        snippet.get("publishedAt", "").replace("Z", "+00:00")
                    ).replace(tzinfo=None),
                    view_count=int(stats.get("viewCount", 0)),
                    like_count=int(stats.get("likeCount", 0)),
                    comment_count=int(stats.get("commentCount", 0)),
                )
                
                results.append(video_info)
                
                # Cache individual video
                cache.set("video", item["id"], {
                    "video_id": video_info.video_id,
                    "title": video_info.title,
                    "channel_id": video_info.channel_id,
                    "channel_title": video_info.channel_title,
                    "published_at": video_info.published_at.isoformat(),
                    "view_count": video_info.view_count,
                    "like_count": video_info.like_count,
                    "comment_count": video_info.comment_count,
                })
            
            return results
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return results
    
    def get_channel_subscribers(
        self,
        channel_ids: list[str],
        use_cache: bool = True
    ) -> dict[str, int]:
        """
        Get subscriber counts for channels.
        
        Args:
            channel_ids: List of channel IDs
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary mapping channel_id to subscriber count
            
        Quota cost: 1 unit per call
        """
        results = {}
        uncached_ids = []
        
        for cid in channel_ids:
            if use_cache:
                cached = cache.get("channel_subs", cid)
                if cached is not None:
                    results[cid] = cached
                    continue
            uncached_ids.append(cid)
        
        if not uncached_ids:
            return results
        
        rate_limiters.wait("youtube")
        
        try:
            # Deduplicate
            unique_ids = list(set(uncached_ids))[:50]
            
            request = self.youtube.channels().list(
                part="statistics",
                id=",".join(unique_ids)
            )
            response = request.execute()
            
            self._track_quota(1)
            
            for item in response.get("items", []):
                channel_id = item["id"]
                subs = int(item.get("statistics", {}).get("subscriberCount", 0))
                results[channel_id] = subs
                cache.set("channel_subs", channel_id, subs, ttl_hours=48)
            
            return results
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return results
    
    def analyze_keyword_supply(
        self,
        keyword: str,
        days: int = 30,
        use_cache: bool = True
    ) -> SupplyMetrics:
        """
        Analyze the supply side for a keyword.
        
        Counts how many videos were uploaded recently.
        
        Args:
            keyword: The keyword to analyze
            days: How many days to look back
            use_cache: Whether to use cached results
            
        Returns:
            SupplyMetrics object
        """
        cache_key = f"supply_{keyword}_{days}"
        
        if use_cache:
            cached = cache.get("supply", cache_key)
            if cached:
                return SupplyMetrics(**cached)
        
        now = datetime.utcnow()
        
        # Videos in last 30 days
        videos_30d = self.search_videos(
            keyword,
            max_results=50,
            order="date",
            published_after=now - timedelta(days=30),
            use_cache=use_cache
        )
        
        # Videos in last 7 days
        videos_7d = self.search_videos(
            keyword,
            max_results=50,
            order="date",
            published_after=now - timedelta(days=7),
            use_cache=use_cache
        )
        
        # Get top 10 by relevance for competition analysis
        top_videos_data = self.search_videos(
            keyword,
            max_results=10,
            order="relevance",
            use_cache=use_cache
        )
        
        if top_videos_data:
            video_ids = [v["video_id"] for v in top_videos_data]
            top_videos = self.get_video_details(video_ids, use_cache)
            
            # Get channel subscribers
            channel_ids = list(set(v.channel_id for v in top_videos))
            subs = self.get_channel_subscribers(channel_ids, use_cache)
            
            # Add subscriber info to videos
            for video in top_videos:
                video.subscriber_count = subs.get(video.channel_id, 0)
            
            # Calculate metrics
            avg_subs = sum(v.subscriber_count or 0 for v in top_videos) / len(top_videos)
            small_channels = sum(1 for v in top_videos if (v.subscriber_count or 0) < 10000)
            avg_age = sum(v.age_days for v in top_videos) / len(top_videos)
        else:
            avg_subs = 0
            small_channels = 0
            avg_age = 0
        
        metrics = SupplyMetrics(
            videos_last_30_days=len(videos_30d),
            videos_last_7_days=len(videos_7d),
            avg_channel_subscribers=avg_subs,
            small_channels_in_top_10=small_channels,
            avg_video_age_days=avg_age,
        )
        
        # Cache results
        cache.set("supply", cache_key, {
            "videos_last_30_days": metrics.videos_last_30_days,
            "videos_last_7_days": metrics.videos_last_7_days,
            "avg_channel_subscribers": metrics.avg_channel_subscribers,
            "small_channels_in_top_10": metrics.small_channels_in_top_10,
            "avg_video_age_days": metrics.avg_video_age_days,
        }, ttl_hours=12)
        
        return metrics
    
    def analyze_keyword_demand(
        self,
        keyword: str,
        trend_index: float = 50.0,
        use_cache: bool = True
    ) -> tuple[DemandMetrics, list[VideoInfo]]:
        """
        Analyze the demand side for a keyword.
        
        Args:
            keyword: The keyword to analyze
            trend_index: Google Trends index (0-100), passed in from Trends module
            use_cache: Whether to use cached results
            
        Returns:
            Tuple of (DemandMetrics, list of top videos)
        """
        # Get top 10 videos by relevance
        top_videos_data = self.search_videos(
            keyword,
            max_results=10,
            order="relevance",
            use_cache=use_cache
        )
        
        if not top_videos_data:
            return DemandMetrics(
                trend_index=trend_index,
                avg_views_top_10=0,
                total_views_top_10=0,
                avg_engagement_rate=0,
            ), []
        
        video_ids = [v["video_id"] for v in top_videos_data]
        top_videos = self.get_video_details(video_ids, use_cache)
        
        if not top_videos:
            return DemandMetrics(
                trend_index=trend_index,
                avg_views_top_10=0,
                total_views_top_10=0,
                avg_engagement_rate=0,
            ), []
        
        total_views = sum(v.view_count for v in top_videos)
        avg_views = total_views / len(top_videos)
        avg_engagement = sum(v.engagement_rate for v in top_videos) / len(top_videos)
        
        metrics = DemandMetrics(
            trend_index=trend_index,
            avg_views_top_10=avg_views,
            total_views_top_10=total_views,
            avg_engagement_rate=avg_engagement,
        )
        
        return metrics, top_videos


# Convenience function
def get_youtube_api(api_key: Optional[str] = None) -> YouTubeAPI:
    """Get a YouTubeAPI instance."""
    return YouTubeAPI(api_key)
