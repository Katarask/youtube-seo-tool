"""Streamlit Web UI for Video Validator - 'Should I make this video?' Tool"""
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Video Validator - Should I Make This Video?",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for dark mode
st.markdown("""
<style>
    .big-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF0000, #FF4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .verdict-yes {
        background: linear-gradient(135deg, #00C851, #007E33);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 1.5rem;
        text-align: center;
    }
    .verdict-no {
        background: linear-gradient(135deg, #ff4444, #CC0000);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 1.5rem;
        text-align: center;
    }
    .metric-card {
        background: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FF0000;
    }
</style>
""", unsafe_allow_html=True)

# Import after config
try:
    from src.core.video_validator import VideoValidator, VideoValidationResult
    from src.core.apify_scraper import APIFY_AVAILABLE
    from src.core.gemini_analyzer import GEMINI_AVAILABLE
    VALIDATOR_AVAILABLE = True
except ImportError as e:
    VALIDATOR_AVAILABLE = False
    st.error(f"Import error: {e}")

st.markdown('<p class="big-title">🎬 VIDEO VALIDATOR</p>', unsafe_allow_html=True)
st.markdown("*Should I make this video? Get AI-powered insights before you invest time.*")

# Sidebar - Status
st.sidebar.header("🔌 API Status")
apify_key = os.getenv("APIFY_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

st.sidebar.write("**Apify:**", "✅ Connected" if apify_key else "❌ Missing key")
st.sidebar.write("**Gemini:**", "✅ Connected" if gemini_key else "❌ Missing key")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Settings")
channel_size = st.sidebar.selectbox(
    "Your channel size",
    ["small", "medium", "large"],
    index=0,
    help="Affects competition analysis"
)
max_videos = st.sidebar.slider("Videos to analyze", 5, 20, 10)
include_comments = st.sidebar.checkbox("Analyze comments", value=True)

# Main input
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    keyword = st.text_input(
        "🔍 Enter your video idea / keyword",
        placeholder="notion tutorial für anfänger",
        help="What topic are you considering for your next video?"
    )
with col2:
    st.write("")
    st.write("")
    validate_btn = st.button("🚀 VALIDATE", type="primary", use_container_width=True)

# Validation
if validate_btn and keyword and VALIDATOR_AVAILABLE:
    with st.spinner("🔍 Analyzing your video idea... (this may take 30-60 seconds)"):
        try:
            validator = VideoValidator(
                channel_size=channel_size
            )
            result = validator.validate(
                keyword,
                max_videos=max_videos,
                include_comments=include_comments
            )

            st.markdown("---")

            # Verdict Banner
            if result.decision and result.decision.should_make:
                st.markdown(f"""
                <div class="verdict-yes">
                    ✅ MAKE THIS VIDEO<br>
                    <small>Confidence: {result.decision.confidence:.0%}</small>
                </div>
                """, unsafe_allow_html=True)
            elif result.decision:
                st.markdown(f"""
                <div class="verdict-no">
                    ❌ SKIP THIS ONE<br>
                    <small>Confidence: {result.decision.confidence:.0%}</small>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")

            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                gap_color = "🟢" if result.gap_score >= 7 else ("🟡" if result.gap_score >= 4 else "🔴")
                st.metric("Gap Score", f"{result.gap_score:.1f}/10", delta=gap_color)
            with col2:
                st.metric("Competition", result.competition_level.upper())
            with col3:
                st.metric("Avg Views", f"{result.avg_views:,}")
            with col4:
                st.metric("Comments Analyzed", result.total_comments_analyzed)

            # Two columns for details
            left_col, right_col = st.columns(2)

            with left_col:
                # Top Videos
                st.subheader("🎬 Top Ranking Videos")
                for i, video in enumerate(result.top_videos[:5], 1):
                    with st.expander(f"{i}. {video['title'][:50]}..."):
                        st.write(f"**Views:** {video['views']:,}")
                        st.write(f"**Channel:** {video['channel']}")
                        st.write(f"**Subscribers:** {video['subscribers']:,}")
                        st.write(f"[Watch Video]({video['url']})")

                # Comment Sentiment
                if result.comment_sentiment:
                    st.subheader("💬 Comment Analysis")
                    sent = result.comment_sentiment

                    # Sentiment bar
                    col_pos, col_neg = st.columns(2)
                    with col_pos:
                        st.metric("👍 Positive", f"{sent.positive_percentage}%")
                    with col_neg:
                        st.metric("👎 Negative", f"{sent.negative_percentage}%")

                    if sent.pain_points:
                        st.write("**🔥 Pain Points:**")
                        for p in sent.pain_points[:3]:
                            st.write(f"• {p}")

                    if sent.wishes:
                        st.write("**💡 What viewers want:**")
                        for w in sent.wishes[:3]:
                            st.write(f"• {w}")

                    if sent.questions:
                        st.write("**❓ Unanswered questions:**")
                        for q in sent.questions[:3]:
                            st.write(f"• {q}")

            with right_col:
                # Title Suggestions
                if result.title_suggestions:
                    st.subheader("🎯 AI Title Suggestions")
                    for i, title in enumerate(result.title_suggestions[:5], 1):
                        with st.expander(f"{i}. {title.title}"):
                            st.write(f"**Why it works:** {title.reason}")
                            st.write(f"**Est. CTR:** {title.estimated_ctr.upper()}")
                            st.write(f"**SEO Score:** {title.seo_score}/10")

                # Decision Details
                if result.decision:
                    st.subheader("🤔 AI Recommendation")

                    if result.decision.reasons_for:
                        st.write("**✅ Reasons FOR:**")
                        for r in result.decision.reasons_for:
                            st.success(f"• {r}")

                    if result.decision.reasons_against:
                        st.write("**❌ Reasons AGAINST:**")
                        for r in result.decision.reasons_against:
                            st.error(f"• {r}")

                    if result.decision.recommended_angle:
                        st.info(f"**🎬 Recommended Angle:** {result.decision.recommended_angle}")

                    if result.decision.content_gaps:
                        st.write("**📝 Content Gaps (what's missing):**")
                        for gap in result.decision.content_gaps:
                            st.write(f"• {gap}")

                    st.markdown("---")
                    st.write(f"**📋 Summary:** {result.decision.summary}")

        except Exception as e:
            st.error(f"Validation failed: {e}")
            import traceback
            st.code(traceback.format_exc())

elif validate_btn and not keyword:
    st.warning("Please enter a keyword/video idea to validate")

elif not VALIDATOR_AVAILABLE:
    st.error("Video Validator not available. Check imports.")

# Footer
st.markdown("---")
st.caption("🎬 Video Validator | Powered by Apify + Gemini AI")
