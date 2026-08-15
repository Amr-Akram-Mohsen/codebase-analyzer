"""
Unit tests for reporting/json_reporter.py.
"""

import json

from codebase_analyzer.core.model import AnalysisResult, Finding, FindingKind, Location, Severity, Module
from codebase_analyzer.reporting.json_reporter import format_json


class TestJsonReporter:
    def test_json_serialization(self) -> None:
        result = AnalysisResult(
            project_root="/path/to/project",
            modules=[
                Module(
                    path="a.py",
                    qualified_name="a",
                    classes=[],
                    functions=[],
                    imports=[],
                )
            ],
            findings=[
                Finding(
                    kind=FindingKind.IMPORT_CYCLE,
                    severity=Severity.ERROR,
                    message="A cycle",
                    location=Location(module="a", line=1),
                )
            ],
        )
        
        output = format_json(result)
        
        # Should be valid JSON
        parsed = json.loads(output)
        
        # Verify structure
        assert parsed["project_root"] == "/path/to/project"
        assert len(parsed["modules"]) == 1
        assert parsed["modules"][0]["qualified_name"] == "a"
        
        # Verify enum serialization
        assert len(parsed["findings"]) == 1
        finding = parsed["findings"][0]
        assert finding["kind"] == "IMPORT_CYCLE"
        assert finding["severity"] == "ERROR"
        assert finding["message"] == "A cycle"
        assert finding["location"]["module"] == "a"
        assert finding["location"]["line"] == 1
