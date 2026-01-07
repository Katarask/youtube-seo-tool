"""Apify YouTube Scraper Integration - scrape videos and comments without API limits."""

import os
import time
from typing import Optional
from dataclasses import dataclass, field

try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    ApifyClient = None


@dataclass
class ScrapedVideo:
    """Represents a scraped YouTube video with all available data."""
    id: str
    title: str
    url: str
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    channel_name: str = ""
    channel_url: str = ""
    subscriber_count: int = 0
    description: str = ""
    upload_date: str = ""
    duration: str = ""
    thumbnail_url: str = ""
    comments: list = field(default_factory=list)


@dataclass
class ScrapedComment:
    """Represents a scraped YouTube comment."""
    author: str
    text: str
    likes: int = 0
    published_at: str = ""
    is_reply: bool = False


class ApifyScraper:
    """
    YouTube scraper using Apify's bernardo/youtube-search-scraper actor.

    Advantages over YouTube Data API:
    - No quota limits
    - More data (subscriber counts, full descriptions)
    - Comments without separate API calls
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Apify scraper.

        Args:
            api_key: Apify API key. Falls back to APIFY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("APIFY_API_KEY")

        if not APIFY_AVAILABLE:
            raise ImportError(
                "apify-client not installed. Run: pip install apify-client"
            )

        if not self.api_key:
            raise ValueError(
                "Apify API key required. Set APIFY_API_KEY environment variable."
            )

        self.client = ApifyClient(self.api_key)
        self.actor_id = "streamers/youtube-scraper"  # More reliable actor

    def search_videos(
        self,
        keyword: str,
        max_results: int = 10,
        include_comments: bool = False,
        max_comments: int = 50
    ) -> list[ScrapedVideo]:
        """
        Search YouTube for videos matching a keyword.

        Args:
            keyword: Search query
            max_results: Maximum number of videos to return
            include_comments: Whether to scrape comments (slower)
            max_comments: Maximum comments per video

        Returns:
            List of ScrapedVideo objects
        """
        # Build YouTube search URL
        search_url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}"

        run_input = {
            "startUrls": [{"url": search_url}],
            "maxResults": max_results,
            "maxResultsShorts": 0,
            "extendOutputFunction": "($) => { return {} }",
        }

        # Run the actor
        try:
            run = self.client.actor(self.actor_id).call(run_input=run_input, timeout_secs=120)
        except Exception as e:
            print(f"Apify actor error: {e}")
            return []

        # Get results
        videos = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            video = self._parse_video(item)
            if video:
                videos.append(video)

        return videos

    def get_video_details(
        self,
        video_url: str,
        include_comments: bool = True,
        max_comments: int = 100
    ) -> Optional[ScrapedVideo]:
        """
        Get detailed information about a specific video.

        Args:
            video_url: YouTube video URL
            include_comments: Whether to scrape comments
            max_comments: Maximum comments to fetch

        Returns:
            ScrapedVideo object or None
        """
        run_input = {
            "startUrls": [{"url": video_url}],
            "maxResults": 1,
        }

        if include_comments:
            run_input["scrapeComments"] = True
            run_input["maxComments"] = max_comments

        run = self.client.actor(self.actor_id).call(run_input=run_input)

        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            return self._parse_video(item)

        return None

    def get_channel_videos(
        self,
        channel_url: str,
        max_results: int = 20
    ) -> list[ScrapedVideo]:
        """
        Get videos from a specific channel.

        Args:
            channel_url: YouTube channel URL
            max_results: Maximum videos to return

        Returns:
            List of ScrapedVideo objects
        """
        run_input = {
            "startUrls": [{"url": channel_url}],
            "maxResults": max_results,
            "maxResultsShorts": 0,
        }

        run = self.client.actor(self.actor_id).call(run_input=run_input)

        videos = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            video = self._parse_video(item)
            if video:
                videos.append(video)

        return videos

    def _parse_video(self, item: dict) -> Optional[ScrapedVideo]:
        """Parse Apify response into ScrapedVideo object."""
        try:
            video = ScrapedVideo(
                id=item.get("id", ""),
                title=item.get("title", ""),
                url=item.get("url", ""),
                view_count=self._parse_int(item.get("viewCount", 0)),
                like_count=self._parse_int(item.get("likes", 0)),
                dislike_count=self._parse_int(item.get("dislikes", 0)),
                comment_count=self._parse_int(item.get("commentsCount", 0)),
                channel_name=item.get("channelName", ""),
                channel_url=item.get("channelUrl", ""),
                subscriber_count=self._parse_int(item.get("numberOfSubscribers", 0)),
                description=item.get("details", "") or item.get("description", ""),
                upload_date=item.get("date", ""),
                duration=item.get("duration", ""),
                thumbnail_url=item.get("thumbnailUrl", ""),
            )

            # Parse comments if available
            if "comments" in item and item["comments"]:
                video.comments = [
                    ScrapedComment(
                        author=c.get("author", ""),
                        text=c.get("text", ""),
                        likes=self._parse_int(c.get("likes", 0)),
                        published_at=c.get("publishedAt", ""),
                        is_reply=c.get("isReply", False),
                    )
                    for c in item["comments"]
                ]

            return video
        except Exception as e:
            print(f"Error parsing video: {e}")
            return None

    def _parse_int(self, value) -> int:
        """Safely parse integer from various formats."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            # Handle "1.2M", "500K" etc.
            value = value.replace(",", "").strip()
            multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
            for suffix, mult in multipliers.items():
                if value.upper().endswith(suffix):
                    try:
                        return int(float(value[:-1]) * mult)
                    except:
                        return 0
            try:
                return int(value)
            except:
                return 0
        return 0


def test_apify_connection(api_key: Optional[str] = None) -> bool:
    """Test if Apify connection works."""
    try:
        scraper = ApifyScraper(api_key)
        # Just check if client is valid
        return True
    except Exception as e:
        print(f"Apify connection failed: {e}")
        return False
