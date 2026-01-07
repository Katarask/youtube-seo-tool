"""Streamlit Web UI for Video Validator - Original YOUTUBE Design"""
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str) -> str:
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, "")

st.set_page_config(
    page_title="VIDEO VALIDATOR",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Original YOUTUBE Design CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

    * { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #0A0A0A;
        background-image: radial-gradient(ellipse at top, rgba(255,0,0,0.08) 0%, transparent 50%);
    }

    [data-testid="stSidebar"] { display: none; }

    .main .block-container {
        max-width: 800px;
        padding: 3rem 1rem;
    }

    .gradient-text {
        font-size: 6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF0000 0%, #FF4444 50%, #CC0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        letter-spacing: -3px;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #71717a;
        font-size: 1.25rem;
        font-weight: 500;
        margin-bottom: 3rem;
    }

    .glass {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.5rem;
        padding: 2.5rem;
        box-shadow: 0 0 60px rgba(255, 0, 0, 0.15);
        margin-bottom: 1.5rem;
    }

    .label {
        color: #71717a;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.75rem;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(24, 24, 27, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 1rem !important;
        color: white !important;
        font-size: 1.25rem !important;
        padding: 1.25rem 1.5rem !important;
        height: auto !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 0, 0, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.2) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #52525b !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        padding: 1rem 2rem !important;
        border-radius: 1rem !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 10px 40px rgba(255, 0, 0, 0.4) !important;
    }

    /* Top Result Card */
    .top-result {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(34, 197, 94, 0.4);
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 0 40px rgba(34, 197, 94, 0.15);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .top-result.skip {
        border-color: rgba(239, 68, 68, 0.4);
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.15);
    }

    .top-result-icon {
        font-size: 3.5rem;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }

    .top-result-content { flex: 1; }

    .top-result-label {
        color: #22c55e;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.25rem;
    }

    .top-result-label.skip { color: #ef4444; }

    .top-result-title {
        color: white;
        font-size: 1.75rem;
        font-weight: 700;
    }

    .top-result-score {
        text-align: right;
    }

    .score-value {
        font-size: 3.5rem;
        font-weight: 700;
        color: #22c55e;
        line-height: 1;
        text-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
    }

    .score-value.skip { color: #ef4444; text-shadow: 0 0 30px rgba(239, 68, 68, 0.5); }
    .score-value.medium { color: #eab308; text-shadow: 0 0 30px rgba(234, 179, 8, 0.5); }

    .score-label {
        color: #71717a;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Results Card */
    .results-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.5rem;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }

    .results-header {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .results-title {
        color: white;
        font-size: 1.25rem;
        font-weight: 700;
    }

    .result-item {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }

    .result-item:hover {
        background: rgba(255, 255, 255, 0.02);
    }

    .result-item:last-child { border-bottom: none; }

    .result-row {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .result-content { flex: 1; }

    .result-name {
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .result-meta {
        color: #71717a;
        font-size: 0.85rem;
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }

    .result-score-box {
        width: 70px;
        height: 70px;
        border-radius: 1rem;
        background: rgba(24, 24, 27, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .result-score {
        font-size: 1.75rem;
        font-weight: 700;
    }

    .score-green { color: #22c55e; box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); }
    .score-yellow { color: #eab308; box-shadow: 0 0 20px rgba(234, 179, 8, 0.3); }
    .score-red { color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }

    /* Insight Cards */
    .insight-card {
        background: rgba(24, 24, 27, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 1rem;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }

    .insight-card.pain { border-left: 3px solid #f97316; }
    .insight-card.wish { border-left: 3px solid #3b82f6; }
    .insight-card.question { border-left: 3px solid #a855f7; }
    .insight-card.pro { border-left: 3px solid #22c55e; background: rgba(34, 197, 94, 0.05); }
    .insight-card.con { border-left: 3px solid #ef4444; background: rgba(239, 68, 68, 0.05); }

    .insight-text {
        color: #e4e4e7;
        font-size: 0.95rem;
    }

    .insight-text.pain { color: #fdba74; }
    .insight-text.wish { color: #93c5fd; }
    .insight-text.question { color: #d8b4fe; }
    .insight-text.pro { color: #86efac; }
    .insight-text.con { color: #fca5a5; }

    /* Title Suggestion */
    .title-card {
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.08) 0%, rgba(255, 0, 0, 0.02) 100%);
        border: 1px solid rgba(255, 0, 0, 0.2);
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }

    .title-text {
        color: white;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .title-meta {
        color: #a1a1aa;
        font-size: 0.8rem;
    }

    .title-reason {
        color: #71717a;
        font-size: 0.8rem;
        margin-top: 0.5rem;
        font-style: italic;
    }

    /* Metrics */
    .metrics-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .metric-box {
        flex: 1;
        background: rgba(24, 24, 27, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.25rem;
        text-align: center;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: white;
        line-height: 1.2;
    }

    .metric-label {
        color: #71717a;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.25rem;
    }

    /* Summary Box */
    .summary-box {
        background: rgba(255, 0, 0, 0.05);
        border: 1px solid rgba(255, 0, 0, 0.2);
        border-radius: 1rem;
        padding: 1.25rem;
        margin-top: 1rem;
    }

    .summary-label {
        color: #fca5a5;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .summary-text {
        color: white;
        font-size: 1rem;
        line-height: 1.5;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #3f3f46;
        font-size: 0.85rem;
        margin-top: 3rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Spinner */
    .spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(255, 0, 0, 0.1);
        border-top-color: #FF0000;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 2rem auto;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Hide Streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# Import modules
VALIDATOR_AVAILABLE = False
try:
    from src.core.video_validator import VideoValidator, VideoValidationResult, AI_PROVIDER
    from src.core.apify_scraper import APIFY_AVAILABLE
    VALIDATOR_AVAILABLE = True
except ImportError as e:
    APIFY_AVAILABLE = False

# Set API keys
apify_key = get_secret("APIFY_API_KEY")
anthropic_key = get_secret("ANTHROPIC_API_KEY")
gemini_key = get_secret("GEMINI_API_KEY")

if apify_key:
    os.environ["APIFY_API_KEY"] = apify_key
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key

# Hero
st.markdown('<h1 class="gradient-text">VIDEO VALIDATOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Soll ich dieses Video machen? KI-gestützte Entscheidungshilfe.</p>', unsafe_allow_html=True)

# Main Input Card
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<p class="label">Video Idee / Keyword</p>', unsafe_allow_html=True)

keyword = st.text_input("", placeholder="z.B. notion tutorial für anfänger", label_visibility="collapsed")
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
validate_btn = st.button("🚀 VALIDIEREN", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Validation
if validate_btn and keyword and VALIDATOR_AVAILABLE:
    with st.spinner(""):
        st.markdown('<div class="spinner"></div>', unsafe_allow_html=True)

        try:
            validator = VideoValidator(channel_size="small")
            result = validator.validate(keyword, max_videos=10, include_comments=True)

            # Top Result Banner
            if result.decision:
                is_go = result.decision.should_make
                score_class = "" if result.gap_score >= 7 else ("medium" if result.gap_score >= 4 else "skip")

                st.markdown(f"""
                <div class="top-result {'skip' if not is_go else ''}">
                    <div class="top-result-icon">{'💎' if is_go else '⚠️'}</div>
                    <div class="top-result-content">
                        <div class="top-result-label {'skip' if not is_go else ''}">
                            {'Mach dieses Video!' if is_go else 'Lieber überspringen'}
                        </div>
                        <div class="top-result-title">{keyword}</div>
                    </div>
                    <div class="top-result-score">
                        <div class="score-value {score_class}">{result.gap_score:.1f}</div>
                        <div class="score-label">Gap Score</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Metrics Row
            st.markdown(f"""
            <div class="metrics-row">
                <div class="metric-box">
                    <div class="metric-value">{result.competition_level.upper()}</div>
                    <div class="metric-label">Konkurrenz</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{result.avg_views:,}</div>
                    <div class="metric-label">Ø Views</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{len(result.top_videos)}</div>
                    <div class="metric-label">Videos</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{result.total_comments_analyzed}</div>
                    <div class="metric-label">Kommentare</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Two columns layout
            col1, col2 = st.columns(2)

            with col1:
                # Top Videos
                if result.top_videos:
                    videos_html = ""
                    for i, v in enumerate(result.top_videos[:5], 1):
                        score = 7  # Placeholder since we don't have individual scores
                        score_class = "score-green" if i <= 2 else ("score-yellow" if i <= 4 else "score-red")
                        videos_html += f"""
                        <div class="result-item">
                            <div class="result-row">
                                <div class="result-content">
                                    <div class="result-name">{v['title'][:45]}...</div>
                                    <div class="result-meta">
                                        <span>{v['views']:,} views</span>
                                        <span>•</span>
                                        <span>{v['channel']}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """

                    st.markdown(f"""
                    <div class="results-card">
                        <div class="results-header">
                            <div class="results-title">🎬 Top Videos</div>
                        </div>
                        {videos_html}
                    </div>
                    """, unsafe_allow_html=True)

                # Comment Insights
                if result.comment_sentiment and result.comment_sentiment.overall_sentiment != "error":
                    sent = result.comment_sentiment
                    insights_html = ""

                    if sent.pain_points:
                        for p in sent.pain_points[:3]:
                            insights_html += f'<div class="insight-card pain"><div class="insight-text pain">🔥 {p}</div></div>'

                    if sent.wishes:
                        for w in sent.wishes[:3]:
                            insights_html += f'<div class="insight-card wish"><div class="insight-text wish">💡 {w}</div></div>'

                    if sent.questions:
                        for q in sent.questions[:3]:
                            insights_html += f'<div class="insight-card question"><div class="insight-text question">❓ {q}</div></div>'

                    if insights_html:
                        st.markdown(f"""
                        <div class="results-card">
                            <div class="results-header">
                                <div class="results-title">💬 Was Zuschauer sagen</div>
                            </div>
                            <div style="padding: 1rem;">
                                {insights_html}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            with col2:
                # Title Suggestions
                if result.title_suggestions:
                    titles_html = ""
                    for i, t in enumerate(result.title_suggestions[:5], 1):
                        titles_html += f"""
                        <div class="title-card">
                            <div class="title-text">{i}. {t.title}</div>
                            <div class="title-meta">CTR: {t.estimated_ctr.upper()} • SEO: {t.seo_score}/10</div>
                            <div class="title-reason">{t.reason}</div>
                        </div>
                        """

                    st.markdown(f"""
                    <div class="results-card">
                        <div class="results-header">
                            <div class="results-title">🎯 Titel-Vorschläge</div>
                        </div>
                        <div style="padding: 1rem;">
                            {titles_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # AI Decision
                if result.decision:
                    decision_html = ""

                    if result.decision.reasons_for:
                        for r in result.decision.reasons_for[:3]:
                            decision_html += f'<div class="insight-card pro"><div class="insight-text pro">✓ {r}</div></div>'

                    if result.decision.reasons_against:
                        for r in result.decision.reasons_against[:3]:
                            decision_html += f'<div class="insight-card con"><div class="insight-text con">✗ {r}</div></div>'

                    summary_html = ""
                    if result.decision.recommended_angle:
                        summary_html = f"""
                        <div class="summary-box">
                            <div class="summary-label">Empfohlener Ansatz</div>
                            <div class="summary-text">{result.decision.recommended_angle}</div>
                        </div>
                        """

                    st.markdown(f"""
                    <div class="results-card">
                        <div class="results-header">
                            <div class="results-title">🤖 KI-Empfehlung</div>
                        </div>
                        <div style="padding: 1rem;">
                            {decision_html}
                            {summary_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Fehler: {e}")

elif validate_btn and not keyword:
    st.warning("Bitte ein Keyword eingeben")

elif validate_btn and not VALIDATOR_AVAILABLE:
    st.error("Video Validator nicht verfügbar")

# Footer
st.markdown('<div class="footer">Video Validator</div>', unsafe_allow_html=True)
