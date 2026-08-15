"""
Unit tests for reporting/terminal.py.
"""

from codebase_analyzer.core.model import AnalysisResult, Finding, FindingKind, Location, Severity, Module
from codebase_analyzer.reporting.terminal import format_terminal


class TestTerminalReporter:
    def test_no_findings(self) -> None:
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
            findings=[],
        )
        
        output = format_terminal(result, use_color=False)
        assert isinstance(output, str)
        assert "/path/to/project" in output
        assert "Modules parsed: 1" in output
        assert "Detailed Findings:" not in output
        assert "Errors: 0" in output

    def test_with_error_finding(self) -> None:
        result = AnalysisResult(
            project_root="/path/to/project",
            modules=[],
            findings=[
                Finding(
                    kind=FindingKind.IMPORT_CYCLE,
                    severity=Severity.ERROR,
                    message="A circular dependency occurred",
                    location=Location(module="myapp.a", line=10),
                )
            ],
        )
        
        output = format_terminal(result, use_color=False)
        assert isinstance(output, str)
        assert "Detailed Findings:" in output
        assert "IMPORT_CYCLE" in output
        assert "A circular dependency occurred" in output
        assert "[myapp.a:10]" in output
        assert "Errors: 1" in output

    def test_no_color(self) -> None:
        result = AnalysisResult(
            project_root="/path/to/project",
            modules=[],
            findings=[
                Finding(
                    kind=FindingKind.IMPORT_CYCLE,
                    severity=Severity.ERROR,
                    message="Msg",
                    location=None,
                )
            ],
        )
        
        output = format_terminal(result, use_color=False)
        # Ensure no ANSI escape codes (starting with \033) are present
        assert "\033[" not in output

    def test_with_color(self) -> None:
        result = AnalysisResult(
            project_root="/path/to/project",
            modules=[],
            findings=[
                Finding(
                    kind=FindingKind.IMPORT_CYCLE,
                    severity=Severity.ERROR,
                    message="Msg",
                    location=None,
                )
            ],
        )
        
        output = format_terminal(result, use_color=True)
        # Verify ANSI escape codes are used
        assert "\033[" in output
