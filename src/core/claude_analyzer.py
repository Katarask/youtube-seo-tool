"""Claude AI Integration for intelligent YouTube analysis."""

import os
import json
from typing import Optional
from dataclasses import dataclass, field

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    anthropic = None


@dataclass
class CommentSentiment:
    """Sentiment analysis result for comments."""
    overall_sentiment: str  # positive, negative, neutral, mixed
    sentiment_score: float  # -1.0 to 1.0
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    main_themes: list = field(default_factory=list)
    pain_points: list = field(default_factory=list)
    wishes: list = field(default_factory=list)
    questions: list = field(default_factory=list)
    summary: str = ""


@dataclass
class TitleSuggestion:
    """AI-generated title suggestion."""
    title: str
    reason: str
    estimated_ctr: str
    seo_score: int


@dataclass
class VideoDecision:
    """Final recommendation on whether to make the video."""
    should_make: bool
    confidence: float
    reasons_for: list = field(default_factory=list)
    reasons_against: list = field(default_factory=list)
    recommended_angle: str = ""
    content_gaps: list = field(default_factory=list)
    summary: str = ""


class ClaudeAnalyzer:
    """AI-powered analysis using Anthropic's Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not CLAUDE_AVAILABLE:
            raise ImportError("anthropic not installed. Run: pip install anthropic")

        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def analyze_comments_sentiment(
        self,
        comments: list[str],
        video_title: str = "",
        keyword: str = ""
    ) -> CommentSentiment:
        if not comments:
            return CommentSentiment(
                overall_sentiment="neutral",
                sentiment_score=0.0,
                positive_percentage=0,
                negative_percentage=0,
                neutral_percentage=100,
                summary="No comments to analyze"
            )

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
    "pain_points": ["what people complain about"],
    "wishes": ["what people want"],
    "questions": ["unanswered questions"],
    "summary": "2-3 sentence summary"
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            result = self._parse_json_response(message.content[0].text)

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
        existing = "\n".join([f"- {t}" for t in (existing_titles or [])[:10]])

        prompt = f"""Generate 5 YouTube video title suggestions for: "{keyword}"

Target audience: {target_audience or 'General'}
Style: {style}

Existing titles (differentiate from these):
{existing or 'None'}

YouTube SEO rules:
1. Keyword at beginning (first 3-4 words)
2. Max 60 characters
3. Use numbers when appropriate
4. Create curiosity gap
5. Be specific, not generic

Respond with ONLY valid JSON:
{{
    "titles": [
        {{
            "title": "Exact title (max 60 chars)",
            "reason": "Why this works",
            "estimated_ctr": "low|medium|high",
            "seo_score": <int 1-10>
        }}
    ]
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            result = self._parse_json_response(message.content[0].text)

            return [
                TitleSuggestion(
                    title=t.get("title", ""),
                    reason=t.get("reason", ""),
                    estimated_ctr=t.get("estimated_ctr", "medium"),
                    seo_score=t.get("seo_score", 5)
                )
                for t in result.get("titles", [])
            ]
        except Exception as e:
            print(f"Title generation error: {e}")
            return []

    def make_video_decision(
        self,
        keyword: str,
        gap_score: float,
        top_videos: list[dict],
        comment_sentiment: Optional[CommentSentiment] = None,
        channel_size: str = "small"
    ) -> VideoDecision:
        videos_info = "\n".join([
            f"- {v.get('title', 'Unknown')}: {v.get('views', 0):,} views, "
            f"{v.get('subscribers', 0):,} subs"
            for v in (top_videos or [])[:10]
        ])

        sentiment_info = ""
        if comment_sentiment:
            sentiment_info = f"""
Comment Analysis:
- Sentiment: {comment_sentiment.overall_sentiment} ({comment_sentiment.sentiment_score:.2f})
- Themes: {', '.join(comment_sentiment.main_themes[:5])}
- Pain points: {', '.join(comment_sentiment.pain_points[:3])}
- Wishes: {', '.join(comment_sentiment.wishes[:3])}"""

        prompt = f"""Should I make a YouTube video about: "{keyword}"?

My channel size: {channel_size}
Gap Score: {gap_score}/10

Top ranking videos:
{videos_info or 'No data'}
{sentiment_info}

Consider:
1. Can a {channel_size} channel compete?
2. Is there demand?
3. What unique angle?
4. What's missing?

Respond with ONLY valid JSON:
{{
    "should_make": true|false,
    "confidence": <float 0.0-1.0>,
    "reasons_for": ["reason1", "reason2"],
    "reasons_against": ["reason1", "reason2"],
    "recommended_angle": "Specific angle",
    "content_gaps": ["What's missing"],
    "summary": "2-3 sentence recommendation"
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            result = self._parse_json_response(message.content[0].text)

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
            return VideoDecision(
                should_make=False,
                confidence=0,
                summary=f"Analysis failed: {str(e)}"
            )

    def _parse_json_response(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())


def test_claude_connection(api_key: Optional[str] = None) -> bool:
    try:
        analyzer = ClaudeAnalyzer(api_key)
        message = analyzer.client.messages.create(
            model=analyzer.model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Say OK"}]
        )
        return "OK" in message.content[0].text or "ok" in message.content[0].text.lower()
    except Exception as e:
        print(f"Claude connection failed: {e}")
        return False
