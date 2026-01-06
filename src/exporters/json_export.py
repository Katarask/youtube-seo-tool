"""JSON export for keyword analysis results."""

import json
from pathlib import Path
from datetime import datetime
from typing import Union

from ..data.models import KeywordAnalysis


def export_to_json(
    analyses: list[KeywordAnalysis],
    output_path: Union[str, Path],
    pretty: bool = True
) -> Path:
    """
    Export keyword analyses to JSON file.
    
    Args:
        analyses: List of KeywordAnalysis objects
        output_path: Output file path
        pretty: Whether to format JSON with indentation
        
    Returns:
        Path to created file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_keywords": len(analyses),
        "keywords": [analysis.to_dict() for analysis in analyses]
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)
    
    return output_path


def generate_json_filename(prefix: str = "keywords_analysis") -> str:
    """Generate a timestamped filename for JSON export."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.json"
