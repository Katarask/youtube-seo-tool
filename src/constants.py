"""Constants and configuration values for YouTube SEO Tool.

This module centralizes magic numbers and configuration constants
to improve maintainability and make tuning easier.
"""

# =============================================================================
# Gap Score Thresholds
# =============================================================================
GAP_SCORE_EXCELLENT_THRESHOLD = 7.0  # Score >= this is "excellent"
GAP_SCORE_GOOD_THRESHOLD = 4.0       # Score >= this is "good", below is "poor"
GAP_SCORE_MAX = 10.0                 # Maximum possible gap score

# =============================================================================
# Trend Analysis
# =============================================================================
TREND_RISING_THRESHOLD = 5.0    # % change to consider "rising"
TREND_FALLING_THRESHOLD = -5.0  # % change to consider "falling"
TREND_DEFAULT_INTEREST = 50.0   # Default when trends unavailable

# =============================================================================
# Supply Metrics
# =============================================================================
SMALL_CHANNEL_SUBSCRIBER_THRESHOLD = 10_000  # Channels below this are "small"
OLD_VIDEO_AGE_DAYS = 365                      # Videos older than this = opportunity
SUPPLY_ANALYSIS_DAYS = 30                     # Default lookback for supply analysis
RECENT_VIDEO_DAYS = 7                         # "Recent" video threshold

# =============================================================================
# Demand Metrics - Scoring Weights
# =============================================================================
DEMAND_TREND_WEIGHT = 0.4     # Weight of trend score in demand calculation
DEMAND_VIEW_WEIGHT = 0.6      # Weight of view score in demand calculation
SUPPLY_VOLUME_WEIGHT = 0.5    # Weight of volume in supply calculation
SUPPLY_CHANNEL_WEIGHT = 0.5   # Weight of channel size in supply calculation

# =============================================================================
# Gap Score Bonuses
# =============================================================================
BONUS_OLD_VIDEO_DOMINANCE = 1.2   # Multiplier when old videos dominate
BONUS_SMALL_CHANNEL_WINS = 1.15   # Multiplier when small channels rank
BONUS_RISING_TREND = 1.1          # Multiplier for rising trends
SMALL_CHANNEL_WINS_THRESHOLD = 2  # Min small channels in top 10 for bonus

# =============================================================================
# High Engagement Threshold
# =============================================================================
HIGH_ENGAGEMENT_RATE = 5.0    # % engagement considered "high"
LOW_UPLOAD_VOLUME = 50        # Videos/month considered "low competition"

# =============================================================================
# API & Rate Limiting
# =============================================================================
YOUTUBE_SEARCH_QUOTA_COST = 100   # Quota units per search call
YOUTUBE_VIDEO_QUOTA_COST = 1      # Quota units per video details call
YOUTUBE_CHANNEL_QUOTA_COST = 1    # Quota units per channel call
YOUTUBE_DAILY_QUOTA_LIMIT = 10_000  # Daily quota limit

YOUTUBE_MAX_RESULTS = 50          # Max results per API call
YOUTUBE_BATCH_SIZE = 50           # Max IDs per batch request

# =============================================================================
# Caching TTL (hours)
# =============================================================================
CACHE_TTL_SEARCH = 12       # Search results
CACHE_TTL_VIDEO = 24        # Video details
CACHE_TTL_CHANNEL = 48      # Channel info
CACHE_TTL_TRENDS = 24       # Trend data
CACHE_TTL_AUTOCOMPLETE = 24 # Autocomplete suggestions

# =============================================================================
# Autocomplete Scraping
# =============================================================================
MAX_RELATED_SEARCHES_PER_BATCH = 20  # Limit to prevent explosion
MAX_SUGGESTIONS_TO_ANALYZE = 30       # Limit for opportunity finding

# =============================================================================
# View Score Normalization
# =============================================================================
VIEW_SCORE_LOG_DIVISOR = 7    # log10(10M) = 7, used for normalization
VIEW_SCORE_MAX = 10           # Maximum view score
