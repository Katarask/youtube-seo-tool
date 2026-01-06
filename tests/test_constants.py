"""Tests for constants module."""

import pytest

from src.constants import (
    # Gap Score
    GAP_SCORE_EXCELLENT_THRESHOLD,
    GAP_SCORE_GOOD_THRESHOLD,
    GAP_SCORE_MAX,
    # Trend
    TREND_RISING_THRESHOLD,
    TREND_FALLING_THRESHOLD,
    TREND_DEFAULT_INTEREST,
    # Supply
    SMALL_CHANNEL_SUBSCRIBER_THRESHOLD,
    OLD_VIDEO_AGE_DAYS,
    # Weights
    DEMAND_TREND_WEIGHT,
    DEMAND_VIEW_WEIGHT,
    SUPPLY_VOLUME_WEIGHT,
    SUPPLY_CHANNEL_WEIGHT,
    # Bonuses
    BONUS_OLD_VIDEO_DOMINANCE,
    BONUS_SMALL_CHANNEL_WINS,
    BONUS_RISING_TREND,
    # API
    YOUTUBE_SEARCH_QUOTA_COST,
    YOUTUBE_DAILY_QUOTA_LIMIT,
)


class TestGapScoreConstants:
    """Tests for gap score constants."""

    def test_threshold_ordering(self):
        """Test thresholds are in correct order."""
        assert GAP_SCORE_EXCELLENT_THRESHOLD > GAP_SCORE_GOOD_THRESHOLD
        assert GAP_SCORE_GOOD_THRESHOLD > 0
        assert GAP_SCORE_MAX >= GAP_SCORE_EXCELLENT_THRESHOLD

    def test_max_is_10(self):
        """Test max gap score is 10."""
        assert GAP_SCORE_MAX == 10.0


class TestTrendConstants:
    """Tests for trend constants."""

    def test_rising_falling_opposite(self):
        """Test rising and falling thresholds are opposite."""
        assert TREND_RISING_THRESHOLD > 0
        assert TREND_FALLING_THRESHOLD < 0
        assert abs(TREND_RISING_THRESHOLD) == abs(TREND_FALLING_THRESHOLD)

    def test_default_interest_midpoint(self):
        """Test default interest is midpoint."""
        assert TREND_DEFAULT_INTEREST == 50.0


class TestWeightConstants:
    """Tests for weight constants."""

    def test_demand_weights_sum_to_1(self):
        """Test demand weights sum to 1."""
        assert DEMAND_TREND_WEIGHT + DEMAND_VIEW_WEIGHT == 1.0

    def test_supply_weights_sum_to_1(self):
        """Test supply weights sum to 1."""
        assert SUPPLY_VOLUME_WEIGHT + SUPPLY_CHANNEL_WEIGHT == 1.0


class TestBonusConstants:
    """Tests for bonus constants."""

    def test_bonuses_are_greater_than_1(self):
        """Test all bonuses are multipliers > 1."""
        assert BONUS_OLD_VIDEO_DOMINANCE > 1.0
        assert BONUS_SMALL_CHANNEL_WINS > 1.0
        assert BONUS_RISING_TREND > 1.0

    def test_bonuses_are_reasonable(self):
        """Test bonuses aren't too extreme."""
        assert BONUS_OLD_VIDEO_DOMINANCE < 2.0
        assert BONUS_SMALL_CHANNEL_WINS < 2.0
        assert BONUS_RISING_TREND < 2.0


class TestApiConstants:
    """Tests for API constants."""

    def test_search_quota_cost(self):
        """Test search quota cost is 100."""
        assert YOUTUBE_SEARCH_QUOTA_COST == 100

    def test_daily_quota_reasonable(self):
        """Test daily quota is reasonable."""
        assert YOUTUBE_DAILY_QUOTA_LIMIT == 10_000
        # Should allow at least 100 searches per day
        assert YOUTUBE_DAILY_QUOTA_LIMIT / YOUTUBE_SEARCH_QUOTA_COST >= 100


class TestSupplyConstants:
    """Tests for supply constants."""

    def test_small_channel_threshold(self):
        """Test small channel threshold is 10k."""
        assert SMALL_CHANNEL_SUBSCRIBER_THRESHOLD == 10_000

    def test_old_video_threshold(self):
        """Test old video threshold is 1 year."""
        assert OLD_VIDEO_AGE_DAYS == 365
