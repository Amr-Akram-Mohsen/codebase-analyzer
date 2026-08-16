"""
Integration tests for the analyzer pipeline regarding name collisions.
"""

from pathlib import Path

from codebase_analyzer.core.analyzer import analyze
from codebase_analyzer.core.model import AnalysisConfig, FindingKind


def test_pipeline_detects_name_collisions() -> None:
    project_root = Path(__file__).parent.parent / "fixtures" / "collision_project"
    
    result = analyze(project_root, AnalysisConfig(layer_rules=[]))
    
    collision_findings = [f for f in result.findings if f.kind == FindingKind.NAME_COLLISION]
    
    assert len(collision_findings) == 1
    
    msg = collision_findings[0].message
    assert "'setup' is already defined at line 4" in msg
