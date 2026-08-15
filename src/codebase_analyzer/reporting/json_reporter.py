"""
Formats analysis results for JSON output.
"""

import json
from dataclasses import asdict

from codebase_analyzer.core.model import AnalysisResult


def format_json(result: AnalysisResult) -> str:
    """
    Serializes the AnalysisResult into a JSON string.
    
    The resulting JSON matches the structure of the dataclasses directly,
    converting enums to their string values automatically where necessary.
    """
    
    def enum_encoder(obj):
        if hasattr(obj, "value"):
            return obj.value
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    # asdict converts the dataclasses to dictionaries recursively
    data = asdict(result)
    
    return json.dumps(data, default=enum_encoder, indent=2)
