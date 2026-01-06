"""Data models for YouTube SEO Tool."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from ..constants import (
    GAP_SCORE_EXCELLENT_THRESHOLD,
    GAP_SCORE_GOOD_THRESHOLD,
    GAP_SCORE_MAX,
    TREND_RISING_THRESHOLD,
    TREND_FALLING_THRESHOLD,
    SMALL_CHANNEL_SUBSCRIBER_THRESHOLD,
    OLD_VIDEO_AGE_DAYS,
    DEMAND_TREND_WEIGHT,
    DEMAND_VIEW_WEIGHT,
    SUPPLY_VOLUME_WEIGHT,
    SUPPLY_CHANNEL_WEIGHT,
    BONUS_OLD_VIDEO_DOMINANCE,
    BONUS_SMALL_CHANNEL_WINS,
    BONUS_RISING_TREND,
    SMALL_CHANNEL_WINS_THRESHOLD,
    HIGH_ENGAGEMENT_RATE,
    LOW_UPLOAD_VOLUME,
    VIEW_SCORE_LOG_DIVISOR,
    VIEW_SCORE_MAX,
)


def _utc_now() -> datetime:
    """Get current UTC time as timezone-naive datetime for consistency."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class GapScoreRating(Enum):
    """Gap score rating categories."""
    EXCELLENT = "excellent"
    GOOD = "good"
    POOR = "poor"


@dataclass
class VideoInfo:
    """Information about a YouTube video."""
    
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    published_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    subscriber_count: Optional[int] = None  # Channel subscribers
    
    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate (likes / views * 100)."""
        if self.view_count == 0:
            return 0.0
        return (self.like_count / self.view_count) * 100
    
    @property
    def age_days(self) -> int:
        """Get video age in days."""
        return (_utc_now() - self.published_at).days
    
    @property
    def views_per_day(self) -> float:
        """Calculate average views per day."""
        if self.age_days == 0:
            return float(self.view_count)
        return self.view_count / self.age_days


@dataclass
class KeywordSuggestion:
    """A keyword suggestion from autocomplete."""
    
    keyword: str
    position: int  # Position in autocomplete (lower = more popular)
    source: str = "youtube_autocomplete"


@dataclass
class TrendData:
    """Google Trends data for a keyword."""
    
    keyword: str
    interest_over_time: list[tuple[datetime, int]] = field(default_factory=list)
    average_interest: float = 0.0
    trend_direction: float = 0.0  # Positive = rising, negative = falling
    peak_month: Optional[str] = None
    
    @property
    def is_rising(self) -> bool:
        """Check if trend is rising."""
        return self.trend_direction > TREND_RISING_THRESHOLD

    @property
    def is_falling(self) -> bool:
        """Check if trend is falling."""
        return self.trend_direction < TREND_FALLING_THRESHOLD
    
    @property
    def trend_emoji(self) -> str:
        """Get trend direction emoji."""
        if self.is_rising:
            return "↗️"
        elif self.is_falling:
            return "↘️"
        return "→"


@dataclass
class DemandMetrics:
    """Demand-side metrics for a keyword."""
    
    trend_index: float  # 0-100 from Google Trends
    avg_views_top_10: float
    total_views_top_10: int
    avg_engagement_rate: float
    
    @property
    def demand_score(self) -> float:
        """
        Calculate demand score (0-10).

        Combines trend index and view potential.
        """
        import math
        # Normalize views (log scale, cap at 10M)
        view_score = min(
            VIEW_SCORE_MAX,
            math.log10(max(1, self.avg_views_top_10)) / VIEW_SCORE_LOG_DIVISOR * VIEW_SCORE_MAX
        )

        # Combine with trend
        trend_score = self.trend_index / 10

        return (trend_score * DEMAND_TREND_WEIGHT + view_score * DEMAND_VIEW_WEIGHT)


@dataclass
class SupplyMetrics:
    """Supply-side metrics for a keyword."""
    
    videos_last_30_days: int
    videos_last_7_days: int
    avg_channel_subscribers: float
    small_channels_in_top_10: int  # Channels with < 10k subs
    avg_video_age_days: float
    
    @property
    def supply_score(self) -> float:
        """
        Calculate supply score (0-10).

        Higher score = more saturated market.
        """
        import math

        # Video volume score (log scale)
        volume_score = min(VIEW_SCORE_MAX, math.log10(max(1, self.videos_last_30_days + 1)) * 3)

        # Channel size score
        channel_score = min(VIEW_SCORE_MAX, math.log10(max(1, self.avg_channel_subscribers)) / 6 * VIEW_SCORE_MAX)

        return (volume_score * SUPPLY_VOLUME_WEIGHT + channel_score * SUPPLY_CHANNEL_WEIGHT)

    @property
    def has_small_channel_wins(self) -> bool:
        """Check if small channels are ranking."""
        return self.small_channels_in_top_10 >= SMALL_CHANNEL_WINS_THRESHOLD

    @property
    def has_old_video_dominance(self) -> bool:
        """Check if old videos dominate (opportunity for fresh content)."""
        return self.avg_video_age_days > OLD_VIDEO_AGE_DAYS


@dataclass
class KeywordAnalysis:
    """Complete analysis for a keyword."""
    
    keyword: str
    suggestions: list[KeywordSuggestion] = field(default_factory=list)
    top_videos: list[VideoInfo] = field(default_factory=list)
    trend_data: Optional[TrendData] = None
    demand: Optional[DemandMetrics] = None
    supply: Optional[SupplyMetrics] = None
    analyzed_at: datetime = field(default_factory=_utc_now)
    
    @property
    def gap_score(self) -> float:
        """
        Calculate the Gap Score (0-10).
        
        Gap Score = (Demand / Supply) × Bonuses
        
        Higher score = better opportunity.
        """
        if not self.demand or not self.supply:
            return 0.0

        if self.supply.supply_score == 0:
            return GAP_SCORE_MAX  # No supply = maximum opportunity

        # Base gap ratio
        base_score = (self.demand.demand_score / max(0.1, self.supply.supply_score)) * 5

        # Apply bonuses
        bonuses = 1.0

        # Freshness bonus: Old videos dominating = opportunity
        if self.supply.has_old_video_dominance:
            bonuses *= BONUS_OLD_VIDEO_DOMINANCE

        # Small channel bonus: If small channels rank, you can too
        if self.supply.has_small_channel_wins:
            bonuses *= BONUS_SMALL_CHANNEL_WINS

        # Rising trend bonus
        if self.trend_data and self.trend_data.is_rising:
            bonuses *= BONUS_RISING_TREND

        return min(GAP_SCORE_MAX, base_score * bonuses)
    
    @property
    def gap_rating(self) -> GapScoreRating:
        """Get the gap score rating category."""
        score = self.gap_score
        if score >= GAP_SCORE_EXCELLENT_THRESHOLD:
            return GapScoreRating.EXCELLENT
        elif score >= GAP_SCORE_GOOD_THRESHOLD:
            return GapScoreRating.GOOD
        return GapScoreRating.POOR
    
    @property
    def gap_emoji(self) -> str:
        """Get emoji for gap rating."""
        rating = self.gap_rating
        if rating == GapScoreRating.EXCELLENT:
            return "🟢"
        elif rating == GapScoreRating.GOOD:
            return "🟡"
        return "🔴"
    
    @property
    def insights(self) -> list[str]:
        """Generate insights about this keyword."""
        insights = []
        
        if not self.supply or not self.demand:
            return insights
        
        # Old video opportunity
        if self.supply.has_old_video_dominance:
            insights.append(
                f"Top 10 dominated by old videos (avg {self.supply.avg_video_age_days:.0f} days) "
                "- opportunity for fresh content!"
            )
        
        # Small channel wins
        if self.supply.has_small_channel_wins:
            insights.append(
                f"{self.supply.small_channels_in_top_10} small channels "
                f"(<{SMALL_CHANNEL_SUBSCRIBER_THRESHOLD // 1000}k subs) in Top 10 "
                "- you can compete!"
            )
        
        # Trend direction
        if self.trend_data:
            if self.trend_data.is_rising:
                insights.append(
                    f"Trend: {self.trend_data.trend_emoji} Rising "
                    f"(+{self.trend_data.trend_direction:.0f}% vs last year)"
                )
            elif self.trend_data.is_falling:
                insights.append(
                    f"Trend: {self.trend_data.trend_emoji} Falling "
                    f"({self.trend_data.trend_direction:.0f}% vs last year)"
                )
        
        # High engagement
        if self.demand.avg_engagement_rate > HIGH_ENGAGEMENT_RATE:
            insights.append(
                f"High engagement rate ({self.demand.avg_engagement_rate:.1f}%) "
                "- audience is active!"
            )

        # Low competition
        if self.supply.videos_last_30_days < LOW_UPLOAD_VOLUME:
            insights.append(
                f"Low upload volume ({self.supply.videos_last_30_days} videos/month) "
                "- not saturated!"
            )
        
        return insights
    
    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            "keyword": self.keyword,
            "gap_score": round(self.gap_score, 2),
            "gap_rating": self.gap_rating.value,
            "demand_score": round(self.demand.demand_score, 2) if self.demand else None,
            "supply_score": round(self.supply.supply_score, 2) if self.supply else None,
            "trend_index": self.trend_data.average_interest if self.trend_data else None,
            "trend_direction": self.trend_data.trend_direction if self.trend_data else None,
            "avg_views_top_10": int(self.demand.avg_views_top_10) if self.demand else None,
            "videos_last_30_days": self.supply.videos_last_30_days if self.supply else None,
            "avg_channel_size": int(self.supply.avg_channel_subscribers) if self.supply else None,
            "small_channels_in_top_10": self.supply.small_channels_in_top_10 if self.supply else None,
            "avg_video_age_days": int(self.supply.avg_video_age_days) if self.supply else None,
            "suggestions_count": len(self.suggestions),
            "insights": self.insights,
            "analyzed_at": self.analyzed_at.isoformat(),
        }
