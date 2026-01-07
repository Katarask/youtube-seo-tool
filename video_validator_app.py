"""Streamlit Web UI for Video Validator - Exact YOUTUBE Design"""
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

# Exact YOUTUBE Design CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #0A0A0A;
    }

    [data-testid="stSidebar"] { display: none; }

    .main .block-container {
        max-width: 900px;
        padding: 2rem 1rem 4rem 1rem;
    }

    /* Header */
    .header-label {
        text-align: center;
        color: #52525b;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 1rem;
    }

    /* Split color title like YOUTUBE */
    .split-title {
        text-align: center;
        font-size: 8rem;
        font-weight: 300;
        letter-spacing: -4px;
        line-height: 1;
        margin-bottom: 1.5rem;
    }

    .title-white {
        color: #e4e4e7;
    }

    .title-red {
        color: #7f1d1d;
    }

    .subtitle {
        text-align: center;
        color: #52525b;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 3rem;
        letter-spacing: 1px;
    }

    .field-label {
        color: #52525b;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.75rem;
    }

    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(24, 24, 27, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 1rem !important;
        color: #a1a1aa !important;
        font-size: 1.1rem !important;
        padding: 1.25rem 1.5rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(127, 29, 29, 0.5) !important;
        box-shadow: none !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #3f3f46 !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%) !important;
        color: #fecaca !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 1rem 2rem !important;
        border-radius: 1rem !important;
        border: none !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
        box-shadow: 0 10px 40px rgba(127, 29, 29, 0.3) !important;
    }

    /* Top Result */
    .verdict-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 1.5rem;
        padding: 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .verdict-card.no {
        border-color: rgba(239, 68, 68, 0.3);
    }

    .verdict-icon {
        font-size: 3rem;
    }

    .verdict-content { flex: 1; }

    .verdict-label {
        color: #22c55e;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .verdict-label.no { color: #ef4444; }

    .verdict-keyword {
        color: #e4e4e7;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    .verdict-score {
        text-align: right;
    }

    .score-big {
        font-size: 3rem;
        font-weight: 700;
        color: #22c55e;
    }

    .score-big.medium { color: #eab308; }
    .score-big.low { color: #ef4444; }

    .score-label {
        color: #52525b;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Results Section */
    .results-section {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 1.5rem;
        overflow: hidden;
        margin-bottom: 1rem;
    }

    .results-header {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        color: #e4e4e7;
        font-weight: 600;
        font-size: 1rem;
    }

    .results-body {
        padding: 1rem;
    }

    .result-row {
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    .result-row:last-child { border-bottom: none; }

    .result-title {
        color: #e4e4e7;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }

    .result-meta {
        color: #52525b;
        font-size: 0.85rem;
    }

    /* Insight Items */
    .insight-item {
        background: rgba(24, 24, 27, 0.5);
        border-radius: 0.75rem;
        padding: 0.875rem 1rem;
        margin-bottom: 0.5rem;
        color: #a1a1aa;
        font-size: 0.9rem;
    }

    .insight-item.pain { border-left: 3px solid #f97316; color: #fdba74; }
    .insight-item.wish { border-left: 3px solid #3b82f6; color: #93c5fd; }
    .insight-item.question { border-left: 3px solid #a855f7; color: #d8b4fe; }
    .insight-item.pro { border-left: 3px solid #22c55e; color: #86efac; }
    .insight-item.con { border-left: 3px solid #ef4444; color: #fca5a5; }

    /* Title Card */
    .title-item {
        background: rgba(127, 29, 29, 0.1);
        border: 1px solid rgba(127, 29, 29, 0.2);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    .title-text {
        color: #e4e4e7;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .title-meta {
        color: #71717a;
        font-size: 0.8rem;
    }

    /* Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }

    .metric-box {
        background: rgba(24, 24, 27, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 1rem;
        padding: 1rem;
        text-align: center;
    }

    .metric-value {
        color: #e4e4e7;
        font-size: 1.5rem;
        font-weight: 600;
    }

    .metric-label {
        color: #52525b;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.25rem;
    }

    /* Angle Box */
    .angle-box {
        background: rgba(127, 29, 29, 0.1);
        border: 1px solid rgba(127, 29, 29, 0.3);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-top: 0.75rem;
    }

    .angle-label {
        color: #fca5a5;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .angle-text {
        color: #e4e4e7;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #27272a;
        font-size: 0.75rem;
        margin-top: 3rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* Hide elements */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Fix spinner */
    .stSpinner > div { border-top-color: #7f1d1d !important; }
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

# Header
st.markdown("""
<p class="header-label">01 — Video Validator</p>
<h1 class="split-title"><span class="title-white">VIDEO</span><span class="title-red">CHECK</span></h1>
<p class="subtitle">Soll ich dieses Video machen? Finde es heraus.</p>
<p class="field-label">Video Idee / Keyword</p>
""", unsafe_allow_html=True)

keyword = st.text_input("", placeholder="z.B. notion tutorial für anfänger", label_visibility="collapsed")

# Button
validate_btn = st.button("VALIDIEREN", use_container_width=True)

# Validation
if validate_btn and keyword and VALIDATOR_AVAILABLE:
    with st.spinner("Analysiere..."):
        try:
            validator = VideoValidator(channel_size="small")
            result = validator.validate(keyword, max_videos=10, include_comments=True)

            # Verdict Card
            if result.decision:
                is_go = result.decision.should_make
                score_class = "" if result.gap_score >= 7 else ("medium" if result.gap_score >= 4 else "low")

                st.markdown(f"""
                <div class="verdict-card {'no' if not is_go else ''}">
                    <div class="verdict-icon">{'💎' if is_go else '⚠️'}</div>
                    <div class="verdict-content">
                        <div class="verdict-label {'no' if not is_go else ''}">
                            {'Mach dieses Video!' if is_go else 'Lieber überspringen'}
                        </div>
                        <div class="verdict-keyword">{keyword}</div>
                    </div>
                    <div class="verdict-score">
                        <div class="score-big {score_class}">{result.gap_score:.1f}</div>
                        <div class="score-label">Gap Score</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Metrics
            st.markdown(f"""
            <div class="metrics-grid">
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

            # Two columns
            col1, col2 = st.columns(2)

            with col1:
                # Top Videos
                if result.top_videos:
                    videos_html = ""
                    for v in result.top_videos[:5]:
                        videos_html += f"""
                        <div class="result-row">
                            <div class="result-title">{v['title'][:50]}...</div>
                            <div class="result-meta">{v['views']:,} views • {v['channel']}</div>
                        </div>
                        """
                    st.markdown(f"""
                    <div class="results-section">
                        <div class="results-header">🎬 Top Videos</div>
                        {videos_html}
                    </div>
                    """, unsafe_allow_html=True)

                # Comments
                if result.comment_sentiment and result.comment_sentiment.overall_sentiment != "error":
                    sent = result.comment_sentiment
                    insights_html = ""

                    for p in (sent.pain_points or [])[:2]:
                        insights_html += f'<div class="insight-item pain">🔥 {p}</div>'
                    for w in (sent.wishes or [])[:2]:
                        insights_html += f'<div class="insight-item wish">💡 {w}</div>'
                    for q in (sent.questions or [])[:2]:
                        insights_html += f'<div class="insight-item question">❓ {q}</div>'

                    if insights_html:
                        st.markdown(f"""
                        <div class="results-section">
                            <div class="results-header">💬 Was Zuschauer sagen</div>
                            <div class="results-body">{insights_html}</div>
                        </div>
                        """, unsafe_allow_html=True)

            with col2:
                # Titles
                if result.title_suggestions:
                    titles_html = ""
                    for i, t in enumerate(result.title_suggestions[:4], 1):
                        titles_html += f"""
                        <div class="title-item">
                            <div class="title-text">{i}. {t.title}</div>
                            <div class="title-meta">CTR: {t.estimated_ctr.upper()} • SEO: {t.seo_score}/10</div>
                        </div>
                        """
                    st.markdown(f"""
                    <div class="results-section">
                        <div class="results-header">🎯 Titel-Vorschläge</div>
                        <div class="results-body">{titles_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # AI Decision
                if result.decision:
                    decision_html = ""
                    for r in (result.decision.reasons_for or [])[:2]:
                        decision_html += f'<div class="insight-item pro">✓ {r}</div>'
                    for r in (result.decision.reasons_against or [])[:2]:
                        decision_html += f'<div class="insight-item con">✗ {r}</div>'

                    angle_html = ""
                    if result.decision.recommended_angle:
                        angle_html = f"""
                        <div class="angle-box">
                            <div class="angle-label">Empfohlener Ansatz</div>
                            <div class="angle-text">{result.decision.recommended_angle}</div>
                        </div>
                        """

                    st.markdown(f"""
                    <div class="results-section">
                        <div class="results-header">🤖 KI-Empfehlung</div>
                        <div class="results-body">
                            {decision_html}
                            {angle_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Fehler: {e}")

elif validate_btn and not keyword:
    st.warning("Bitte ein Keyword eingeben")

elif validate_btn and not VALIDATOR_AVAILABLE:
    st.error("Video Validator nicht verfügbar")

# Footer
st.markdown('<div class="footer">Video Validator</div>', unsafe_allow_html=True)
