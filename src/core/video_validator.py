"""Video Validator - "Should I make this video?" decision tool."""

import os
from typing import Optional
from dataclasses import dataclass, field

from .apify_scraper import ApifyScraper, ScrapedVideo, APIFY_AVAILABLE
from .gemini_analyzer import (
    GeminiAnalyzer,
    CommentSentiment,
    TitleSuggestion,
    VideoDecision,
    GEMINI_AVAILABLE
)
from .analyzer import KeywordAnalyzer
from ..data.models import KeywordAnalysis


@dataclass
class VideoValidationResult:
    """Complete validation result for a video idea."""
    keyword: str

    # Gap Score Analysis
    gap_score: float = 0.0
    demand_score: float = 0.0
    supply_score: float = 0.0

    # Top Videos Data
    top_videos: list = field(default_factory=list)
    avg_views: int = 0
    avg_subscribers: int = 0
    total_comments_analyzed: int = 0

    # AI Analysis
    comment_sentiment: Optional[CommentSentiment] = None
    title_suggestions: list = field(default_factory=list)
    decision: Optional[VideoDecision] = None

    # Quick Stats
    competition_level: str = "unknown"  # low, medium, high
    opportunity_rating: str = "unknown"  # poor, fair, good, excellent

    def __str__(self) -> str:
        """Pretty print the validation result."""
        emoji = {
            "excellent": "🟢", "good": "🟡", "fair": "🟠", "poor": "🔴"
        }.get(self.opportunity_rating, "⚪")

        decision_emoji = "✅" if self.decision and self.decision.should_make else "❌"

        lines = [
            f"\n{'='*60}",
            f"📊 VIDEO VALIDATION: {self.keyword}",
            f"{'='*60}",
            f"",
            f"{emoji} Opportunity Rating: {self.opportunity_rating.upper()}",
            f"   Gap Score: {self.gap_score:.1f}/10",
            f"   Demand: {self.demand_score:.1f} | Supply: {self.supply_score:.1f}",
            f"   Competition: {self.competition_level}",
            f"",
            f"📈 Top Videos Analysis ({len(self.top_videos)} videos):",
            f"   Avg Views: {self.avg_views:,}",
            f"   Avg Subscribers: {self.avg_subscribers:,}",
        ]

        if self.comment_sentiment:
            lines.extend([
                f"",
                f"💬 Comment Sentiment ({self.total_comments_analyzed} comments):",
                f"   Overall: {self.comment_sentiment.overall_sentiment} "
                f"({self.comment_sentiment.sentiment_score:+.2f})",
                f"   👍 {self.comment_sentiment.positive_percentage}% positive | "
                f"👎 {self.comment_sentiment.negative_percentage}% negative",
            ])
            if self.comment_sentiment.pain_points:
                lines.append(f"   🔥 Pain points: {', '.join(self.comment_sentiment.pain_points[:3])}")
            if self.comment_sentiment.wishes:
                lines.append(f"   💡 Viewers want: {', '.join(self.comment_sentiment.wishes[:3])}")
            if self.comment_sentiment.questions:
                lines.append(f"   ❓ Open questions: {', '.join(self.comment_sentiment.questions[:3])}")

        if self.title_suggestions:
            lines.extend([
                f"",
                f"🎯 Title Suggestions:",
            ])
            for i, ts in enumerate(self.title_suggestions[:5], 1):
                lines.append(f"   {i}. \"{ts.title}\"")
                lines.append(f"      CTR: {ts.estimated_ctr} | SEO: {ts.seo_score}/10")

        if self.decision:
            lines.extend([
                f"",
                f"{'='*60}",
                f"{decision_emoji} VERDICT: {'MAKE THIS VIDEO' if self.decision.should_make else 'SKIP THIS ONE'}",
                f"   Confidence: {self.decision.confidence:.0%}",
                f"{'='*60}",
            ])
            if self.decision.reasons_for:
                lines.append(f"   ✅ Reasons FOR:")
                for r in self.decision.reasons_for[:3]:
                    lines.append(f"      • {r}")
            if self.decision.reasons_against:
                lines.append(f"   ❌ Reasons AGAINST:")
                for r in self.decision.reasons_against[:3]:
                    lines.append(f"      • {r}")
            if self.decision.recommended_angle:
                lines.append(f"   🎬 Recommended angle: {self.decision.recommended_angle}")
            if self.decision.content_gaps:
                lines.append(f"   📝 Content gaps to fill: {', '.join(self.decision.content_gaps[:3])}")
            lines.extend([
                f"",
                f"   📋 Summary: {self.decision.summary}",
            ])

        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


class VideoValidator:
    """
    Main class that combines all tools to validate a video idea.

    Usage:
        validator = VideoValidator()
        result = validator.validate("notion tutorial")
        print(result)
    """

    def __init__(
        self,
        apify_key: Optional[str] = None,
        gemini_key: Optional[str] = None,
        youtube_key: Optional[str] = None,
        channel_size: str = "small"
    ):
        """
        Initialize the video validator.

        Args:
            apify_key: Apify API key (or APIFY_API_KEY env var)
            gemini_key: Gemini API key (or GEMINI_API_KEY env var)
            youtube_key: YouTube API key (or YOUTUBE_API_KEY env var)
            channel_size: Your channel size (small/medium/large)
        """
        self.channel_size = channel_size

        # Initialize Apify scraper
        self.apify = None
        if APIFY_AVAILABLE:
            try:
                self.apify = ApifyScraper(apify_key)
            except Exception as e:
                print(f"⚠️  Apify not available: {e}")

        # Initialize Gemini analyzer
        self.gemini = None
        if GEMINI_AVAILABLE:
            try:
                self.gemini = GeminiAnalyzer(gemini_key)
            except Exception as e:
                print(f"⚠️  Gemini not available: {e}")

        # Initialize keyword analyzer (uses YouTube API)
        try:
            self.keyword_analyzer = KeywordAnalyzer(youtube_api_key=youtube_key)
        except Exception as e:
            print(f"⚠️  Keyword analyzer not available: {e}")
            self.keyword_analyzer = None

    def validate(
        self,
        keyword: str,
        max_videos: int = 10,
        include_comments: bool = True,
        max_comments: int = 50,
        generate_titles: bool = True
    ) -> VideoValidationResult:
        """
        Validate a video idea with full analysis.

        Args:
            keyword: Video topic/keyword to validate
            max_videos: Number of top videos to analyze
            include_comments: Whether to analyze comments
            max_comments: Max comments per video to analyze
            generate_titles: Whether to generate title suggestions

        Returns:
            VideoValidationResult with complete analysis
        """
        result = VideoValidationResult(keyword=keyword)
        all_comments = []

        print(f"\n🔍 Validating video idea: \"{keyword}\"")
        print("-" * 40)

        # Step 1: Gap Score Analysis
        print("📊 Analyzing keyword gap score...")
        if self.keyword_analyzer:
            try:
                kw_analysis = self.keyword_analyzer.analyze_keyword(keyword)
                result.gap_score = kw_analysis.gap_score
                result.demand_score = kw_analysis.demand.score if kw_analysis.demand else 0
                result.supply_score = kw_analysis.supply.score if kw_analysis.supply else 0
            except Exception as e:
                print(f"   ⚠️  Gap score analysis failed: {e}")

        # Step 2: Scrape top videos with Apify
        print("🎬 Scraping top videos...")
        if self.apify:
            try:
                videos = self.apify.search_videos(
                    keyword,
                    max_results=max_videos,
                    include_comments=include_comments,
                    max_comments=max_comments
                )

                for v in videos:
                    result.top_videos.append({
                        "title": v.title,
                        "views": v.view_count,
                        "likes": v.like_count,
                        "subscribers": v.subscriber_count,
                        "channel": v.channel_name,
                        "url": v.url
                    })
                    # Collect comments
                    all_comments.extend([c.text for c in v.comments])

                if videos:
                    result.avg_views = sum(v.view_count for v in videos) // len(videos)
                    result.avg_subscribers = sum(v.subscriber_count for v in videos) // len(videos)

                result.total_comments_analyzed = len(all_comments)
                print(f"   ✅ Found {len(videos)} videos, {len(all_comments)} comments")

            except Exception as e:
                print(f"   ⚠️  Video scraping failed: {e}")

        # Step 3: Analyze comments with Gemini
        if self.gemini and all_comments:
            print("💬 Analyzing comment sentiment...")
            try:
                result.comment_sentiment = self.gemini.analyze_comments_sentiment(
                    all_comments,
                    keyword=keyword
                )
                print(f"   ✅ Sentiment: {result.comment_sentiment.overall_sentiment}")
            except Exception as e:
                print(f"   ⚠️  Sentiment analysis failed: {e}")

        # Step 4: Generate title suggestions
        if self.gemini and generate_titles:
            print("🎯 Generating title suggestions...")
            try:
                existing_titles = [v["title"] for v in result.top_videos]
                result.title_suggestions = self.gemini.generate_title_suggestions(
                    keyword,
                    existing_titles=existing_titles
                )
                print(f"   ✅ Generated {len(result.title_suggestions)} title ideas")
            except Exception as e:
                print(f"   ⚠️  Title generation failed: {e}")

        # Step 5: Make final decision
        if self.gemini:
            print("🤔 Making final recommendation...")
            try:
                result.decision = self.gemini.make_video_decision(
                    keyword=keyword,
                    gap_score=result.gap_score,
                    top_videos=result.top_videos,
                    comment_sentiment=result.comment_sentiment,
                    channel_size=self.channel_size
                )
                print(f"   ✅ Decision made!")
            except Exception as e:
                print(f"   ⚠️  Decision making failed: {e}")

        # Calculate competition level and opportunity rating
        result.competition_level = self._calculate_competition(result)
        result.opportunity_rating = self._calculate_opportunity(result)

        return result

    def _calculate_competition(self, result: VideoValidationResult) -> str:
        """Calculate competition level based on data."""
        if result.avg_subscribers > 1_000_000:
            return "high"
        elif result.avg_subscribers > 100_000:
            return "medium"
        else:
            return "low"

    def _calculate_opportunity(self, result: VideoValidationResult) -> str:
        """Calculate opportunity rating."""
        score = result.gap_score

        if score >= 7:
            return "excellent"
        elif score >= 5:
            return "good"
        elif score >= 3:
            return "fair"
        else:
            return "poor"

    def quick_check(self, keyword: str) -> dict:
        """
        Quick validation without full analysis.

        Returns basic gap score and recommendation.
        """
        result = {
            "keyword": keyword,
            "gap_score": 0,
            "quick_verdict": "unknown",
            "reason": ""
        }

        if self.keyword_analyzer:
            try:
                analysis = self.keyword_analyzer.analyze_keyword(keyword)
                result["gap_score"] = analysis.gap_score

                if analysis.gap_score >= 7:
                    result["quick_verdict"] = "GO"
                    result["reason"] = "High opportunity - low competition, good demand"
                elif analysis.gap_score >= 4:
                    result["quick_verdict"] = "MAYBE"
                    result["reason"] = "Moderate opportunity - consider your unique angle"
                else:
                    result["quick_verdict"] = "SKIP"
                    result["reason"] = "Low opportunity - high competition or low demand"

            except Exception as e:
                result["reason"] = f"Analysis failed: {e}"

        return result


# Convenience function
def validate_video_idea(keyword: str, **kwargs) -> VideoValidationResult:
    """
    Quick function to validate a video idea.

    Args:
        keyword: Video topic to validate
        **kwargs: Additional arguments for VideoValidator

    Returns:
        VideoValidationResult
    """
    validator = VideoValidator(**kwargs)
    return validator.validate(keyword)
