"""CSV export for keyword analysis results."""

import csv
from pathlib import Path
from datetime import datetime
from typing import Union

from ..data.models import KeywordAnalysis


def export_to_csv(
    analyses: list[KeywordAnalysis],
    output_path: Union[str, Path],
    include_insights: bool = True
) -> Path:
    """
    Export keyword analyses to CSV file.
    
    Args:
        analyses: List of KeywordAnalysis objects
        output_path: Output file path
        include_insights: Whether to include insights column
        
    Returns:
        Path to created file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define columns
    fieldnames = [
        "keyword",
        "gap_score",
        "gap_rating",
        "demand_score",
        "supply_score",
        "trend_index",
        "trend_direction",
        "avg_views_top_10",
        "videos_last_30_days",
        "videos_last_7_days",
        "avg_channel_subscribers",
        "small_channels_in_top_10",
        "avg_video_age_days",
        "suggestions_count",
        "analyzed_at",
    ]
    
    if include_insights:
        fieldnames.append("insights")
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for analysis in analyses:
            row = {
                "keyword": analysis.keyword,
                "gap_score": round(analysis.gap_score, 2),
                "gap_rating": analysis.gap_rating.value,
                "suggestions_count": len(analysis.suggestions),
                "analyzed_at": analysis.analyzed_at.isoformat(),
            }
            
            if analysis.demand:
                row["demand_score"] = round(analysis.demand.demand_score, 2)
                row["trend_index"] = round(analysis.demand.trend_index, 0)
                row["avg_views_top_10"] = int(analysis.demand.avg_views_top_10)
            
            if analysis.supply:
                row["supply_score"] = round(analysis.supply.supply_score, 2)
                row["videos_last_30_days"] = analysis.supply.videos_last_30_days
                row["videos_last_7_days"] = analysis.supply.videos_last_7_days
                row["avg_channel_subscribers"] = int(analysis.supply.avg_channel_subscribers)
                row["small_channels_in_top_10"] = analysis.supply.small_channels_in_top_10
                row["avg_video_age_days"] = int(analysis.supply.avg_video_age_days)
            
            if analysis.trend_data:
                row["trend_direction"] = f"{analysis.trend_data.trend_direction:+.0f}%"
            
            if include_insights:
                row["insights"] = " | ".join(analysis.insights)
            
            writer.writerow(row)
    
    return output_path


def generate_csv_filename(prefix: str = "keywords_analysis") -> str:
    """Generate a timestamped filename for CSV export."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.csv"
