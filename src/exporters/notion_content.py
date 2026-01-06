"""Notion page content builder for keyword analysis."""

from ..data.models import KeywordAnalysis


def build_page_content(analysis: KeywordAnalysis) -> list[dict]:
    """Build rich page content with insights and metrics."""
    blocks = []
    
    # Header
    blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": f"🎯 {analysis.keyword}"}}]
        }
    })
    
    # Gap Score callout
    color = "green_background" if analysis.gap_score >= 7 else \
            "yellow_background" if analysis.gap_score >= 4 else "red_background"
    
    blocks.append({
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{
                "type": "text",
                "text": {"content": f"Gap Score: {analysis.gap_score:.1f}/10 {analysis.gap_emoji}"}
            }],
            "icon": {"type": "emoji", "emoji": "📊"},
            "color": color
        }
    })
    
    blocks.append({"object": "block", "type": "divider", "divider": {}})
    
    # Demand Metrics
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📈 Demand Metrics"}}]
        }
    })
    
    if analysis.demand:
        demand_text = f"""• Trend Index: {analysis.demand.trend_index:.0f}/100
• Avg Views (Top 10): {analysis.demand.avg_views_top_10:,.0f}
• Engagement Rate: {analysis.demand.avg_engagement_rate:.1f}%
• Demand Score: {analysis.demand.demand_score:.1f}/10"""
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": demand_text}}]
            }
        })
    
    # Supply Metrics
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "📦 Supply Metrics"}}]
        }
    })
    
    if analysis.supply:
        supply_text = f"""• Videos (last 30 days): {analysis.supply.videos_last_30_days}
• Videos (last 7 days): {analysis.supply.videos_last_7_days}
• Avg Channel Size: {analysis.supply.avg_channel_subscribers:,.0f} subs
• Small Channels in Top 10: {analysis.supply.small_channels_in_top_10}
• Avg Video Age: {analysis.supply.avg_video_age_days:.0f} days
• Supply Score: {analysis.supply.supply_score:.1f}/10"""
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": supply_text}}]
            }
        })
    
    # Insights
    if analysis.insights:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "💡 Insights"}}]
            }
        })
        
        for insight in analysis.insights:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": insight}}]
                }
            })
    
    # Trend Info
    if analysis.trend_data and analysis.trend_data.peak_month:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📊 Trend Info"}}]
            }
        })
        
        trend_text = f"""• Direction: {analysis.trend_data.trend_emoji} {analysis.trend_data.trend_direction:+.0f}%
• Peak Month: {analysis.trend_data.peak_month}
• Average Interest: {analysis.trend_data.average_interest:.0f}/100"""
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": trend_text}}]
            }
        })
    
    # Related Keywords
    if analysis.suggestions:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🔗 Related Keywords"}}]
            }
        })
        
        for suggestion in analysis.suggestions[:10]:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": suggestion.keyword}}]
                }
            })
    
    return blocks
