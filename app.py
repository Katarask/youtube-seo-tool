"""Streamlit Web UI for YouTube SEO Tool"""
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="YouTube Keyword Research",
    page_icon="🎯",
    layout="wide"
)

# Import after streamlit config
from src.core.analyzer import KeywordAnalyzer
from src.core.autocomplete import get_autocomplete_suggestions
from src.exporters.notion_export import NotionExporter

st.title("🎯 YouTube Keyword Research Tool")
st.markdown("*Find content opportunities with Gap Score analysis*")

# Sidebar
st.sidebar.header("⚙️ Settings")
expand_keywords = st.sidebar.checkbox("Expand with prefixes/suffixes", value=False)
export_to_notion = st.sidebar.checkbox("Export to Notion", value=True)
use_cache = st.sidebar.checkbox("Use cache", value=True)

# Main input
col1, col2 = st.columns([3, 1])
with col1:
    keywords_input = st.text_area(
        "Enter keywords (one per line)",
        placeholder="defense recruiting\naerospace jobs germany\nheadhunter IT",
        height=100
    )
with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

# Autocomplete section
st.markdown("---")
st.subheader("💡 Keyword Suggestions")
autocomplete_input = st.text_input("Get autocomplete suggestions for:", placeholder="defense recruiting")
if autocomplete_input:
    with st.spinner("Fetching suggestions..."):
        suggestions = get_autocomplete_suggestions(autocomplete_input)
        if suggestions:
            cols = st.columns(4)
            for i, sug in enumerate(suggestions[:12]):
                cols[i % 4].code(sug)
        else:
            st.info("No suggestions found")

# Analysis
if analyze_btn and keywords_input:
    keywords = [k.strip() for k in keywords_input.strip().split("\n") if k.strip()]
    
    if not keywords:
        st.error("Please enter at least one keyword")
    else:
        analyzer = KeywordAnalyzer(use_cache=use_cache)
        
        progress = st.progress(0)
        status = st.empty()
        
        results = []
        for i, kw in enumerate(keywords):
            status.text(f"Analyzing: {kw}")
            progress.progress((i + 1) / len(keywords))
            
            try:
                analysis = analyzer.analyze_keyword(kw, expand=expand_keywords)
                if analysis:
                    results.extend(analysis if isinstance(analysis, list) else [analysis])
            except Exception as e:
                st.warning(f"Error analyzing '{kw}': {e}")
        
        progress.empty()
        status.empty()
        
        if results:
            st.markdown("---")
            st.subheader("📊 Results")
            
            # Sort by gap score
            results.sort(key=lambda x: x.gap_score, reverse=True)
            
            # Display as table
            data = []
            for r in results:
                rating_emoji = "🟢" if r.gap_score >= 7 else ("🟡" if r.gap_score >= 4 else "🔴")
                trend_arrow = {"rising": "↗️", "falling": "↘️", "stable": "→"}.get(r.demand.trend_direction, "→")
                data.append({
                    "Keyword": r.keyword,
                    "Gap Score": f"{r.gap_score:.1f}",
                    "Rating": rating_emoji,
                    "Demand": f"{r.demand.score:.1f}",
                    "Supply": f"{r.supply.score:.1f}",
                    "Trend": trend_arrow,
                    "Videos/30d": r.supply.recent_videos_30d,
                    "Avg Views": f"{r.supply.avg_views:,.0f}" if r.supply.avg_views else "N/A"
                })
            
            st.dataframe(data, use_container_width=True, hide_index=True)
            
            # Top opportunity
            best = results[0]
            st.success(f"**💎 Top Opportunity:** {best.keyword} (Gap Score: {best.gap_score:.1f})")
            
            # Export to Notion
            if export_to_notion:
                notion_key = os.getenv("NOTION_API_KEY")
                notion_db = os.getenv("NOTION_DATABASE_ID")
                
                if notion_key and notion_db:
                    with st.spinner("Exporting to Notion..."):
                        try:
                            exporter = NotionExporter(notion_key, notion_db)
                            exported = 0
                            for r in results:
                                if exporter.export_analysis(r):
                                    exported += 1
                            st.info(f"✅ Exported {exported} keywords to Notion")
                        except Exception as e:
                            st.error(f"Notion export failed: {e}")
                else:
                    st.warning("Notion credentials not configured")
            
            # Quota info
            st.caption(f"YouTube API quota used: ~{analyzer.api.quota_used} units")
        else:
            st.warning("No results found")

# Footer
st.markdown("---")
st.caption("Built for TEKOM | YouTube SEO Research Tool")
