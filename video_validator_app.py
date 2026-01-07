"""Streamlit Web UI for Video Validator - 'Should I make this video?' Tool"""
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Support Streamlit Cloud secrets
def get_secret(key: str) -> str:
    """Get secret from Streamlit Cloud or .env file."""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, "")

st.set_page_config(
    page_title="VIDEO VALIDATOR",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS - Matching the original YOUTUBE design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stApp {
        background: #0A0A0A;
        background-image: radial-gradient(ellipse at top, rgba(255,0,0,0.08) 0%, transparent 50%);
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 3rem;
    }

    .gradient-title {
        font-size: 5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF0000 0%, #FF4444 50%, #CC0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }

    .subtitle {
        text-align: center;
        color: #71717a;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.5rem;
        padding: 2.5rem;
        box-shadow: 0 0 60px rgba(255, 0, 0, 0.15);
        margin-bottom: 1.5rem;
    }

    .verdict-yes {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.1) 100%);
        border: 2px solid rgba(34, 197, 94, 0.5);
        border-radius: 1.5rem;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 0 40px rgba(34, 197, 94, 0.2);
    }

    .verdict-no {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 2px solid rgba(239, 68, 68, 0.5);
        border-radius: 1.5rem;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.2);
    }

    .verdict-text {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
    }

    .confidence-text {
        color: #a1a1aa;
        font-size: 1rem;
    }

    .metric-card {
        background: rgba(24, 24, 27, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }

    .metric-label {
        color: #71717a;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }

    .score-green { color: #22c55e; text-shadow: 0 0 20px rgba(34, 197, 94, 0.5); }
    .score-yellow { color: #eab308; text-shadow: 0 0 20px rgba(234, 179, 8, 0.5); }
    .score-red { color: #ef4444; text-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }

    .section-title {
        color: #a1a1aa;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin-bottom: 1rem;
        margin-top: 2rem;
    }

    .video-item {
        background: rgba(24, 24, 27, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }

    .video-item:hover {
        background: rgba(24, 24, 27, 0.8);
        border-color: rgba(255, 0, 0, 0.3);
    }

    .title-suggestion {
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.1) 0%, rgba(255, 0, 0, 0.05) 100%);
        border: 1px solid rgba(255, 0, 0, 0.2);
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        margin-bottom: 0.75rem;
    }

    .reason-for {
        background: rgba(34, 197, 94, 0.1);
        border-left: 3px solid #22c55e;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #86efac;
    }

    .reason-against {
        background: rgba(239, 68, 68, 0.1);
        border-left: 3px solid #ef4444;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #fca5a5;
    }

    .pain-point {
        background: rgba(249, 115, 22, 0.1);
        border-left: 3px solid #f97316;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #fdba74;
    }

    .wish-item {
        background: rgba(59, 130, 246, 0.1);
        border-left: 3px solid #3b82f6;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #93c5fd;
    }

    .question-item {
        background: rgba(168, 85, 247, 0.1);
        border-left: 3px solid #a855f7;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #d8b4fe;
    }

    /* Streamlit overrides */
    .stTextInput > div > div > input {
        background: rgba(24, 24, 27, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 1rem !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 1rem 1.5rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 0, 0, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.2) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.3) !important;
    }

    .stSelectbox > div > div {
        background: rgba(24, 24, 27, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
    }

    .stSlider > div > div > div {
        background: #FF0000 !important;
    }

    .stCheckbox > label {
        color: #a1a1aa !important;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    .stExpander {
        background: rgba(24, 24, 27, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 1rem !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #3f3f46;
        font-size: 0.85rem;
        margin-top: 4rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Import after config
VALIDATOR_AVAILABLE = False
AI_PROVIDER = "none"
import_error = None

try:
    from src.core.video_validator import VideoValidator, VideoValidationResult, AI_PROVIDER
    from src.core.apify_scraper import APIFY_AVAILABLE
    VALIDATOR_AVAILABLE = True
except ImportError as e:
    import_error = str(e)
    APIFY_AVAILABLE = False

# Hero Title
st.markdown('<h1 class="gradient-title">VIDEO VALIDATOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Should I make this video? Get AI-powered insights.</p>', unsafe_allow_html=True)

# Show import error if any
if import_error:
    st.error(f"⚠️ Import Error: {import_error}")

# Get API keys
apify_key = get_secret("APIFY_API_KEY")
anthropic_key = get_secret("ANTHROPIC_API_KEY")
gemini_key = get_secret("GEMINI_API_KEY")

# Set environment variables
if apify_key:
    os.environ["APIFY_API_KEY"] = apify_key
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    channel_size = st.selectbox("Channel Size", ["small", "medium", "large"], index=0)
    max_videos = st.slider("Videos to analyze", 5, 20, 10)
    include_comments = st.checkbox("Analyze comments", value=True)
    debug_mode = st.checkbox("Debug mode", value=False)

    st.markdown("---")
    st.markdown("### 🔌 API Status")
    st.write("**Apify:**", "✅" if apify_key else "❌")
    if anthropic_key:
        st.write("**Claude:**", "✅")
    elif gemini_key:
        st.write("**Gemini:**", "✅")
    else:
        st.write("**AI:**", "❌")

# Main Input Card
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-title">Video Idea / Keyword</p>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    keyword = st.text_input(
        "",
        placeholder="z.B. notion tutorial für anfänger",
        label_visibility="collapsed"
    )
with col2:
    validate_btn = st.button("VALIDATE", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Validation
if validate_btn and keyword and VALIDATOR_AVAILABLE:
    with st.spinner("🔍 Analyzing..."):
        try:
            if debug_mode:
                st.info(f"🔧 Starting validation for: {keyword}")

            validator = VideoValidator(channel_size=channel_size)
            result = validator.validate(
                keyword,
                max_videos=max_videos,
                include_comments=include_comments
            )

            # Verdict Banner
            if result.decision and result.decision.should_make:
                st.markdown(f"""
                <div class="verdict-yes">
                    <div class="verdict-text">✅ MAKE THIS VIDEO</div>
                    <div class="confidence-text">Confidence: {result.decision.confidence:.0%}</div>
                </div>
                """, unsafe_allow_html=True)
            elif result.decision:
                st.markdown(f"""
                <div class="verdict-no">
                    <div class="verdict-text">❌ SKIP THIS ONE</div>
                    <div class="confidence-text">Confidence: {result.decision.confidence:.0%}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Could not make a decision")

            st.markdown("")

            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)

            score_class = "score-green" if result.gap_score >= 7 else ("score-yellow" if result.gap_score >= 4 else "score-red")

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value {score_class}">{result.gap_score:.1f}</div>
                    <div class="metric-label">Gap Score</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{result.competition_level.upper()}</div>
                    <div class="metric-label">Competition</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{result.avg_views:,}</div>
                    <div class="metric-label">Avg Views</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{result.total_comments_analyzed}</div>
                    <div class="metric-label">Comments</div>
                </div>
                """, unsafe_allow_html=True)

            # Two columns
            left_col, right_col = st.columns(2)

            with left_col:
                # Top Videos
                if result.top_videos:
                    st.markdown('<p class="section-title">🎬 Top Videos</p>', unsafe_allow_html=True)
                    for i, video in enumerate(result.top_videos[:5], 1):
                        st.markdown(f"""
                        <div class="video-item">
                            <div style="color: white; font-weight: 600; margin-bottom: 0.25rem;">{i}. {video['title'][:50]}...</div>
                            <div style="color: #71717a; font-size: 0.85rem;">
                                {video['views']:,} views • {video['channel']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Comment Sentiment
                if result.comment_sentiment and result.comment_sentiment.overall_sentiment != "error":
                    st.markdown('<p class="section-title">💬 Comment Analysis</p>', unsafe_allow_html=True)
                    sent = result.comment_sentiment

                    st.markdown(f"""
                    <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                        <div class="metric-card" style="flex: 1;">
                            <div class="metric-value score-green">{sent.positive_percentage}%</div>
                            <div class="metric-label">Positive</div>
                        </div>
                        <div class="metric-card" style="flex: 1;">
                            <div class="metric-value score-red">{sent.negative_percentage}%</div>
                            <div class="metric-label">Negative</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if sent.pain_points:
                        st.markdown("**🔥 Pain Points:**")
                        for p in sent.pain_points[:3]:
                            st.markdown(f'<div class="pain-point">{p}</div>', unsafe_allow_html=True)

                    if sent.wishes:
                        st.markdown("**💡 What viewers want:**")
                        for w in sent.wishes[:3]:
                            st.markdown(f'<div class="wish-item">{w}</div>', unsafe_allow_html=True)

                    if sent.questions:
                        st.markdown("**❓ Open questions:**")
                        for q in sent.questions[:3]:
                            st.markdown(f'<div class="question-item">{q}</div>', unsafe_allow_html=True)

            with right_col:
                # Title Suggestions
                if result.title_suggestions:
                    st.markdown('<p class="section-title">🎯 Title Suggestions</p>', unsafe_allow_html=True)
                    for i, title in enumerate(result.title_suggestions[:5], 1):
                        st.markdown(f"""
                        <div class="title-suggestion">
                            <div style="color: white; font-weight: 600; margin-bottom: 0.5rem;">{i}. {title.title}</div>
                            <div style="color: #a1a1aa; font-size: 0.85rem;">
                                CTR: {title.estimated_ctr.upper()} • SEO: {title.seo_score}/10
                            </div>
                            <div style="color: #71717a; font-size: 0.8rem; margin-top: 0.25rem;">
                                {title.reason}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # AI Decision Details
                if result.decision:
                    st.markdown('<p class="section-title">🤔 AI Recommendation</p>', unsafe_allow_html=True)

                    if result.decision.reasons_for:
                        st.markdown("**Reasons FOR:**")
                        for r in result.decision.reasons_for:
                            st.markdown(f'<div class="reason-for">✓ {r}</div>', unsafe_allow_html=True)

                    if result.decision.reasons_against:
                        st.markdown("**Reasons AGAINST:**")
                        for r in result.decision.reasons_against:
                            st.markdown(f'<div class="reason-against">✗ {r}</div>', unsafe_allow_html=True)

                    if result.decision.recommended_angle:
                        st.markdown(f"""
                        <div style="background: rgba(255, 0, 0, 0.1); border: 1px solid rgba(255, 0, 0, 0.3); border-radius: 0.75rem; padding: 1rem; margin-top: 1rem;">
                            <div style="color: #fca5a5; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Recommended Angle</div>
                            <div style="color: white; margin-top: 0.25rem;">{result.decision.recommended_angle}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if result.decision.summary:
                        st.markdown(f"""
                        <div style="background: rgba(24, 24, 27, 0.8); border-radius: 0.75rem; padding: 1rem; margin-top: 1rem;">
                            <div style="color: white;">{result.decision.summary}</div>
                        </div>
                        """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Validation failed: {e}")
            import traceback
            st.code(traceback.format_exc())

elif validate_btn and not keyword:
    st.warning("Please enter a keyword")

elif validate_btn and not VALIDATOR_AVAILABLE:
    st.error("Video Validator not available")

# Footer
ai_info = "Claude" if anthropic_key else ("Gemini" if gemini_key else "No AI")
st.markdown(f'<div class="footer">VIDEO VALIDATOR • Powered by Apify + {ai_info}</div>', unsafe_allow_html=True)
