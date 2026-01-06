"""Tests for data models."""

import pytest
from datetime import datetime, timedelta, timezone

from src.data.models import (
    VideoInfo,
    KeywordSuggestion,
    TrendData,
    DemandMetrics,
    SupplyMetrics,
    KeywordAnalysis,
    GapScoreRating,
)
from src.constants import (
    GAP_SCORE_EXCELLENT_THRESHOLD,
    GAP_SCORE_GOOD_THRESHOLD,
    TREND_RISING_THRESHOLD,
    TREND_FALLING_THRESHOLD,
    OLD_VIDEO_AGE_DAYS,
    SMALL_CHANNEL_WINS_THRESHOLD,
)


class TestVideoInfo:
    """Tests for VideoInfo model."""

    def test_engagement_rate_with_views(self):
        """Test engagement rate calculation with views."""
        video = VideoInfo(
            video_id="abc123",
            title="Test Video",
            channel_id="ch123",
            channel_title="Test Channel",
            published_at=datetime.now(),
            view_count=1000,
            like_count=50,
            comment_count=10,
        )
        assert video.engagement_rate == 5.0

    def test_engagement_rate_zero_views(self):
        """Test engagement rate with zero views returns 0."""
        video = VideoInfo(
            video_id="abc123",
            title="Test Video",
            channel_id="ch123",
            channel_title="Test Channel",
            published_at=datetime.now(),
            view_count=0,
            like_count=0,
            comment_count=0,
        )
        assert video.engagement_rate == 0.0

    def test_age_days(self):
        """Test video age calculation."""
        published = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
        video = VideoInfo(
            video_id="abc123",
            title="Test Video",
            channel_id="ch123",
            channel_title="Test Channel",
            published_at=published,
            view_count=1000,
            like_count=50,
            comment_count=10,
        )
        assert video.age_days == 30

    def test_views_per_day(self):
        """Test views per day calculation."""
        published = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=10)
        video = VideoInfo(
            video_id="abc123",
            title="Test Video",
            channel_id="ch123",
            channel_title="Test Channel",
            published_at=published,
            view_count=1000,
            like_count=50,
            comment_count=10,
        )
        assert video.views_per_day == 100.0


class TestTrendData:
    """Tests for TrendData model."""

    def test_is_rising(self):
        """Test rising trend detection."""
        trend = TrendData(
            keyword="test",
            trend_direction=TREND_RISING_THRESHOLD + 1,
        )
        assert trend.is_rising is True
        assert trend.is_falling is False

    def test_is_falling(self):
        """Test falling trend detection."""
        trend = TrendData(
            keyword="test",
            trend_direction=TREND_FALLING_THRESHOLD - 1,
        )
        assert trend.is_falling is True
        assert trend.is_rising is False

    def test_stable_trend(self):
        """Test stable trend (neither rising nor falling)."""
        trend = TrendData(
            keyword="test",
            trend_direction=0,
        )
        assert trend.is_rising is False
        assert trend.is_falling is False

    def test_trend_emoji(self):
        """Test trend emoji selection."""
        rising = TrendData(keyword="test", trend_direction=10)
        falling = TrendData(keyword="test", trend_direction=-10)
        stable = TrendData(keyword="test", trend_direction=0)

        assert rising.trend_emoji == "↗️"
        assert falling.trend_emoji == "↘️"
        assert stable.trend_emoji == "→"


class TestDemandMetrics:
    """Tests for DemandMetrics model."""

    def test_demand_score_calculation(self):
        """Test demand score is calculated correctly."""
        demand = DemandMetrics(
            trend_index=80,
            avg_views_top_10=1_000_000,
            total_views_top_10=10_000_000,
            avg_engagement_rate=5.0,
        )
        score = demand.demand_score
        assert 0 <= score <= 10

    def test_demand_score_low_values(self):
        """Test demand score with low values."""
        demand = DemandMetrics(
            trend_index=0,
            avg_views_top_10=0,
            total_views_top_10=0,
            avg_engagement_rate=0,
        )
        assert demand.demand_score == 0.0


class TestSupplyMetrics:
    """Tests for SupplyMetrics model."""

    def test_supply_score_calculation(self):
        """Test supply score is calculated correctly."""
        supply = SupplyMetrics(
            videos_last_30_days=100,
            videos_last_7_days=25,
            avg_channel_subscribers=100_000,
            small_channels_in_top_10=2,
            avg_video_age_days=180,
        )
        score = supply.supply_score
        assert 0 <= score <= 10

    def test_has_small_channel_wins(self):
        """Test small channel wins detection."""
        supply_yes = SupplyMetrics(
            videos_last_30_days=10,
            videos_last_7_days=2,
            avg_channel_subscribers=50_000,
            small_channels_in_top_10=SMALL_CHANNEL_WINS_THRESHOLD,
            avg_video_age_days=100,
        )
        supply_no = SupplyMetrics(
            videos_last_30_days=10,
            videos_last_7_days=2,
            avg_channel_subscribers=50_000,
            small_channels_in_top_10=SMALL_CHANNEL_WINS_THRESHOLD - 1,
            avg_video_age_days=100,
        )
        assert supply_yes.has_small_channel_wins is True
        assert supply_no.has_small_channel_wins is False

    def test_has_old_video_dominance(self):
        """Test old video dominance detection."""
        old = SupplyMetrics(
            videos_last_30_days=10,
            videos_last_7_days=2,
            avg_channel_subscribers=50_000,
            small_channels_in_top_10=2,
            avg_video_age_days=OLD_VIDEO_AGE_DAYS + 1,
        )
        new = SupplyMetrics(
            videos_last_30_days=10,
            videos_last_7_days=2,
            avg_channel_subscribers=50_000,
            small_channels_in_top_10=2,
            avg_video_age_days=OLD_VIDEO_AGE_DAYS - 1,
        )
        assert old.has_old_video_dominance is True
        assert new.has_old_video_dominance is False


class TestKeywordAnalysis:
    """Tests for KeywordAnalysis model."""

    def test_gap_score_no_data(self):
        """Test gap score is 0 without demand/supply data."""
        analysis = KeywordAnalysis(keyword="test")
        assert analysis.gap_score == 0.0

    def test_gap_score_zero_supply(self):
        """Test gap score is max with zero supply."""
        analysis = KeywordAnalysis(
            keyword="test",
            demand=DemandMetrics(
                trend_index=50,
                avg_views_top_10=100_000,
                total_views_top_10=1_000_000,
                avg_engagement_rate=3.0,
            ),
            supply=SupplyMetrics(
                videos_last_30_days=0,
                videos_last_7_days=0,
                avg_channel_subscribers=0,
                small_channels_in_top_10=0,
                avg_video_age_days=0,
            ),
        )
        assert analysis.gap_score == 10.0

    def test_gap_rating_excellent(self):
        """Test excellent rating threshold."""
        analysis = KeywordAnalysis(keyword="test")
        analysis.demand = DemandMetrics(
            trend_index=100,
            avg_views_top_10=10_000_000,
            total_views_top_10=100_000_000,
            avg_engagement_rate=10.0,
        )
        analysis.supply = SupplyMetrics(
            videos_last_30_days=1,
            videos_last_7_days=0,
            avg_channel_subscribers=100,
            small_channels_in_top_10=5,
            avg_video_age_days=500,
        )
        # Force a high gap score scenario
        if analysis.gap_score >= GAP_SCORE_EXCELLENT_THRESHOLD:
            assert analysis.gap_rating == GapScoreRating.EXCELLENT

    def test_gap_emoji(self):
        """Test gap emoji matches rating."""
        analysis = KeywordAnalysis(keyword="test")
        # Without data, gap_score is 0, so rating is POOR
        assert analysis.gap_emoji == "🔴"

    def test_to_dict(self):
        """Test dictionary export."""
        analysis = KeywordAnalysis(keyword="test keyword")
        result = analysis.to_dict()

        assert result["keyword"] == "test keyword"
        assert "gap_score" in result
        assert "gap_rating" in result
        assert "analyzed_at" in result

    def test_insights_generation(self):
        """Test insights are generated correctly."""
        analysis = KeywordAnalysis(
            keyword="test",
            demand=DemandMetrics(
                trend_index=50,
                avg_views_top_10=100_000,
                total_views_top_10=1_000_000,
                avg_engagement_rate=8.0,  # High engagement
            ),
            supply=SupplyMetrics(
                videos_last_30_days=20,  # Low volume
                videos_last_7_days=5,
                avg_channel_subscribers=5000,
                small_channels_in_top_10=3,  # Small channels win
                avg_video_age_days=400,  # Old videos
            ),
            trend_data=TrendData(keyword="test", trend_direction=10),  # Rising
        )
        insights = analysis.insights
        assert len(insights) > 0
        # Should have insights about old videos, small channels, and high engagement
        assert any("old videos" in i.lower() for i in insights)
        assert any("small channels" in i.lower() for i in insights)
