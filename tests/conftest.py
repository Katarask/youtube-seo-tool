"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# Disable logging during tests
from src.utils.logger import disable_logging
disable_logging()


@pytest.fixture
def sample_video_info():
    """Create a sample VideoInfo for testing."""
    from datetime import datetime, timezone, timedelta
    from src.data.models import VideoInfo

    return VideoInfo(
        video_id="test123",
        title="Test Video Title",
        channel_id="channel123",
        channel_title="Test Channel",
        published_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30),
        view_count=100_000,
        like_count=5_000,
        comment_count=500,
        subscriber_count=50_000,
    )


@pytest.fixture
def sample_demand_metrics():
    """Create sample DemandMetrics for testing."""
    from src.data.models import DemandMetrics

    return DemandMetrics(
        trend_index=65.0,
        avg_views_top_10=500_000,
        total_views_top_10=5_000_000,
        avg_engagement_rate=4.5,
    )


@pytest.fixture
def sample_supply_metrics():
    """Create sample SupplyMetrics for testing."""
    from src.data.models import SupplyMetrics

    return SupplyMetrics(
        videos_last_30_days=45,
        videos_last_7_days=12,
        avg_channel_subscribers=75_000,
        small_channels_in_top_10=3,
        avg_video_age_days=200,
    )


@pytest.fixture
def sample_trend_data():
    """Create sample TrendData for testing."""
    from src.data.models import TrendData

    return TrendData(
        keyword="test keyword",
        interest_over_time=[],
        average_interest=60.0,
        trend_direction=8.0,
        peak_month="January 2024",
    )


@pytest.fixture
def sample_keyword_analysis(sample_demand_metrics, sample_supply_metrics, sample_trend_data):
    """Create a sample KeywordAnalysis for testing."""
    from src.data.models import KeywordAnalysis

    return KeywordAnalysis(
        keyword="test keyword",
        suggestions=[],
        top_videos=[],
        trend_data=sample_trend_data,
        demand=sample_demand_metrics,
        supply=sample_supply_metrics,
    )
