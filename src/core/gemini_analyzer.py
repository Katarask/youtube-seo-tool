"""Gemini AI Integration for intelligent YouTube analysis."""

import os
import json
from typing import Optional
from dataclasses import dataclass, field

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


@dataclass
class CommentSentiment:
    """Sentiment analysis result for comments."""
    overall_sentiment: str  # positive, negative, neutral, mixed
    sentiment_score: float  # -1.0 to 1.0
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    main_themes: list = field(default_factory=list)
    pain_points: list = field(default_factory=list)  # What people complain about
    wishes: list = field(default_factory=list)  # What people want to see
    questions: list = field(default_factory=list)  # Unanswered questions
    summary: str = ""


@dataclass
class TitleSuggestion:
    """AI-generated title suggestion."""
    title: str
    reason: str
    estimated_ctr: str  # low, medium, high
    seo_score: int  # 1-10


@dataclass
class VideoDecision:
    """Final recommendation on whether to make the video."""
    should_make: bool
    confidence: float  # 0.0 to 1.0
    reasons_for: list = field(default_factory=list)
    reasons_against: list = field(default_factory=list)
    recommended_angle: str = ""
    content_gaps: list = field(default_factory=list)  # What's missing in existing videos
    summary: str = ""


class GeminiAnalyzer:
    """
    AI-powered analysis using Google's Gemini API.

    Free tier: 1,500 requests/day with Gemini 1.5 Flash
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini analyzer.

        Args:
            api_key: Gemini API key. Falls back to GEMINI_API_KEY env var.
            model: Model to use (default: gemini-1.5-flash for free tier)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai not installed. Run: pip install google-generativeai"
            )

        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    def analyze_comments_sentiment(
        self,
        comments: list[str],
        video_title: str = "",
        keyword: str = ""
    ) -> CommentSentiment:
        """
        Analyze sentiment and extract insights from YouTube comments.

        Args:
            comments: List of comment texts
            video_title: Title of the video (for context)
            keyword: Search keyword (for context)

        Returns:
            CommentSentiment object with analysis
        """
        if not comments:
            return CommentSentiment(
                overall_sentiment="neutral",
                sentiment_score=0.0,
                positive_percentage=0,
                negative_percentage=0,
                neutral_percentage=100,
                summary="No comments to analyze"
            )

        # Limit comments to avoid token limits
        sample_comments = comments[:100]
        comments_text = "\n".join([f"- {c}" for c in sample_comments])

        prompt = f"""Analyze these YouTube comments and provide insights in JSON format.

Context:
- Video topic/keyword: {keyword or video_title or 'Unknown'}
- Number of comments: {len(comments)} (sample of {len(sample_comments)})

Comments:
{comments_text}

Respond with ONLY valid JSON (no markdown, no explanation):
{{
    "overall_sentiment": "positive|negative|neutral|mixed",
    "sentiment_score": <float from -1.0 to 1.0>,
    "positive_percentage": <int 0-100>,
    "negative_percentage": <int 0-100>,
    "neutral_percentage": <int 0-100>,
    "main_themes": ["theme1", "theme2", "theme3"],
    "pain_points": ["what people complain about or struggle with"],
    "wishes": ["what people explicitly want or request"],
    "questions": ["unanswered questions from viewers"],
    "summary": "2-3 sentence summary of what the audience feels and wants"
}}"""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            return CommentSentiment(
                overall_sentiment=result.get("overall_sentiment", "neutral"),
                sentiment_score=float(result.get("sentiment_score", 0)),
                positive_percentage=result.get("positive_percentage", 0),
                negative_percentage=result.get("negative_percentage", 0),
                neutral_percentage=result.get("neutral_percentage", 100),
                main_themes=result.get("main_themes", []),
                pain_points=result.get("pain_points", []),
                wishes=result.get("wishes", []),
                questions=result.get("questions", []),
                summary=result.get("summary", "")
            )
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return CommentSentiment(
                overall_sentiment="error",
                sentiment_score=0,
                positive_percentage=0,
                negative_percentage=0,
                neutral_percentage=0,
                summary=f"Analysis failed: {str(e)}"
            )

    def generate_title_suggestions(
        self,
        keyword: str,
        existing_titles: list[str] = None,
        target_audience: str = "",
        style: str = "informative"
    ) -> list[TitleSuggestion]:
        """
        Generate SEO-optimized, clickable title suggestions.

        Args:
            keyword: Main keyword/topic
            existing_titles: Titles that already rank (to differentiate)
            target_audience: Who the video is for
            style: informative, entertaining, tutorial, listicle

        Returns:
            List of TitleSuggestion objects
        """
        existing = "\n".join([f"- {t}" for t in (existing_titles or [])[:10]])

        prompt = f"""Generate 5 YouTube video title suggestions for the keyword: "{keyword}"

Target audience: {target_audience or 'General'}
Style: {style}

Existing titles that rank (differentiate from these):
{existing or 'None provided'}

YouTube SEO rules to follow:
1. Keyword at the beginning (first 3-4 words)
2. Max 60 characters (will be cut off otherwise)
3. Use numbers when appropriate ("5 Ways...", "in 10 Minutes")
4. Create curiosity gap (don't reveal everything)
5. Emotional triggers work (but avoid clickbait)
6. Be specific, not generic

Respond with ONLY valid JSON (no markdown):
{{
    "titles": [
        {{
            "title": "Exact title text (max 60 chars)",
            "reason": "Why this title works",
            "estimated_ctr": "low|medium|high",
            "seo_score": <int 1-10>
        }}
    ]
}}"""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            suggestions = []
            for t in result.get("titles", []):
                suggestions.append(TitleSuggestion(
                    title=t.get("title", ""),
                    reason=t.get("reason", ""),
                    estimated_ctr=t.get("estimated_ctr", "medium"),
                    seo_score=t.get("seo_score", 5)
                ))

            return suggestions
        except Exception as e:
            print(f"Gemini title generation error: {e}")
            return []

    def make_video_decision(
        self,
        keyword: str,
        gap_score: float,
        top_videos: list[dict],
        comment_sentiment: Optional[CommentSentiment] = None,
        channel_size: str = "small"  # small, medium, large
    ) -> VideoDecision:
        """
        Make a recommendation on whether to create this video.

        Args:
            keyword: Video topic/keyword
            gap_score: Gap score from keyword analysis (0-10)
            top_videos: List of top ranking videos with their stats
            comment_sentiment: Sentiment analysis of comments
            channel_size: Your channel size category

        Returns:
            VideoDecision with recommendation
        """
        videos_info = "\n".join([
            f"- {v.get('title', 'Unknown')}: {v.get('views', 0):,} views, "
            f"{v.get('subscribers', 0):,} subs, {v.get('likes', 0):,} likes"
            for v in (top_videos or [])[:10]
        ])

        sentiment_info = ""
        if comment_sentiment:
            sentiment_info = f"""
Comment Analysis:
- Overall sentiment: {comment_sentiment.overall_sentiment} ({comment_sentiment.sentiment_score:.2f})
- Main themes: {', '.join(comment_sentiment.main_themes[:5])}
- Pain points: {', '.join(comment_sentiment.pain_points[:3])}
- What viewers want: {', '.join(comment_sentiment.wishes[:3])}
- Unanswered questions: {', '.join(comment_sentiment.questions[:3])}"""

        prompt = f"""Analyze if I should make a YouTube video about: "{keyword}"

My channel size: {channel_size}
Gap Score: {gap_score}/10 (higher = more opportunity)

Top ranking videos:
{videos_info or 'No data'}
{sentiment_info}

Consider:
1. Can a {channel_size} channel compete?
2. Is there demand (gap score, views)?
3. What unique angle could differentiate?
4. What's missing in existing content?

Respond with ONLY valid JSON:
{{
    "should_make": true|false,
    "confidence": <float 0.0-1.0>,
    "reasons_for": ["reason1", "reason2"],
    "reasons_against": ["reason1", "reason2"],
    "recommended_angle": "Specific angle or approach to take",
    "content_gaps": ["What existing videos are missing"],
    "summary": "2-3 sentence final recommendation"
}}"""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            return VideoDecision(
                should_make=result.get("should_make", False),
                confidence=float(result.get("confidence", 0.5)),
                reasons_for=result.get("reasons_for", []),
                reasons_against=result.get("reasons_against", []),
                recommended_angle=result.get("recommended_angle", ""),
                content_gaps=result.get("content_gaps", []),
                summary=result.get("summary", "")
            )
        except Exception as e:
            print(f"Gemini decision error: {e}")
            return VideoDecision(
                should_make=False,
                confidence=0,
                summary=f"Analysis failed: {str(e)}"
            )

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from Gemini response, handling markdown code blocks."""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        return json.loads(text.strip())


def test_gemini_connection(api_key: Optional[str] = None) -> bool:
    """Test if Gemini connection works."""
    try:
        analyzer = GeminiAnalyzer(api_key)
        response = analyzer.model.generate_content("Say 'OK' if you can read this.")
        return "OK" in response.text or "ok" in response.text.lower()
    except Exception as e:
        print(f"Gemini connection failed: {e}")
        return False
