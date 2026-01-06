"""Notion export functions for keyword analysis."""

from typing import Optional
from notion_client.errors import APIResponseError

from ..data.models import KeywordAnalysis
from .notion_base import NotionExporter
from .notion_content import build_page_content


def _build_properties(exporter: NotionExporter, analysis: KeywordAnalysis) -> dict:
    """Build Notion page properties from analysis."""
    properties = {
        "Keyword": {"title": [{"text": {"content": analysis.keyword}}]},
        "Gap Score": {"number": round(analysis.gap_score, 2)},
        "Rating": {"select": {"name": exporter._get_rating_text(analysis.gap_rating)}},
        "Analyzed At": {"date": {"start": analysis.analyzed_at.isoformat()}},
        "Suggestions Count": {"number": len(analysis.suggestions)},
    }
    
    if analysis.demand:
        properties["Demand Score"] = {"number": round(analysis.demand.demand_score, 2)}
        properties["Trend Index"] = {"number": round(analysis.demand.trend_index, 0)}
        properties["Avg Views (Top 10)"] = {"number": int(analysis.demand.avg_views_top_10)}
    
    if analysis.supply:
        properties["Supply Score"] = {"number": round(analysis.supply.supply_score, 2)}
        properties["Videos (30 days)"] = {"number": analysis.supply.videos_last_30_days}
        properties["Avg Channel Size"] = {"number": int(analysis.supply.avg_channel_subscribers)}
        properties["Small Channels %"] = {"number": analysis.supply.small_channels_in_top_10}
        properties["Avg Video Age (days)"] = {"number": int(analysis.supply.avg_video_age_days)}
    
    if analysis.trend_data:
        trend_text = f"{analysis.trend_data.trend_emoji} {analysis.trend_data.trend_direction:+.0f}%"
        properties["Trend Direction"] = {"rich_text": [{"text": {"content": trend_text}}]}
    
    return properties


def export_analysis(
    exporter: NotionExporter,
    analysis: KeywordAnalysis,
    include_content: bool = True
) -> str:
    """
    Export a single keyword analysis to Notion.
    
    Args:
        exporter: NotionExporter instance
        analysis: The KeywordAnalysis to export
        include_content: Whether to include detailed page content
        
    Returns:
        The created page ID
    """
    if not exporter.database_id:
        raise ValueError("No database ID configured. Create a database first.")
    
    properties = _build_properties(exporter, analysis)
    
    # Set icon based on rating
    icon_emoji = "🟢" if analysis.gap_score >= 7 else "🟡" if analysis.gap_score >= 4 else "🔴"
    
    try:
        page_data = {
            "parent": {"database_id": exporter.database_id},
            "properties": properties,
            "icon": {"type": "emoji", "emoji": icon_emoji},
        }
        
        if include_content:
            page_data["children"] = build_page_content(analysis)
        
        response = exporter.client.pages.create(**page_data)
        return response["id"]
        
    except APIResponseError as e:
        print(f"Error creating page: {e}")
        raise


def export_multiple(
    exporter: NotionExporter,
    analyses: list[KeywordAnalysis],
    include_content: bool = True,
    progress_callback=None
) -> list[str]:
    """
    Export multiple keyword analyses to Notion.
    
    Args:
        exporter: NotionExporter instance
        analyses: List of KeywordAnalysis objects
        include_content: Whether to include detailed page content
        progress_callback: Optional callback(current, total, keyword)
        
    Returns:
        List of created page IDs
    """
    page_ids = []
    total = len(analyses)
    
    for i, analysis in enumerate(analyses):
        if progress_callback:
            progress_callback(i + 1, total, analysis.keyword)
        
        try:
            page_id = export_analysis(exporter, analysis, include_content)
            page_ids.append(page_id)
        except Exception as e:
            print(f"Error exporting '{analysis.keyword}': {e}")
    
    return page_ids


# Add methods to NotionExporter class
NotionExporter.export_analysis = lambda self, analysis, include_content=True: \
    export_analysis(self, analysis, include_content)

NotionExporter.export_multiple = lambda self, analyses, include_content=True, progress_callback=None: \
    export_multiple(self, analyses, include_content, progress_callback)
