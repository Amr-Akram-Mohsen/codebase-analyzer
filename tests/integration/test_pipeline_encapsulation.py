"""
Integration tests for the analyzer pipeline regarding encapsulation violations.
"""

from pathlib import Path

from codebase_analyzer.core.analyzer import analyze
from codebase_analyzer.core.model import AnalysisConfig, FindingKind, Severity


def test_pipeline_detects_encapsulation_violations(tmp_path: Path) -> None:
    # Set up a dummy project structure
    project_root = tmp_path / "encapsulation_project"
    
    # 1. Private module
    (project_root / "domain").mkdir(parents=True)
    (project_root / "domain" / "__init__.py").write_text("")
    (project_root / "domain" / "_internal.py").write_text("def helper(): pass")
    
    # 2. Public API module (boundary)
    (project_root / "api").mkdir(parents=True)
    (project_root / "api" / "__init__.py").write_text("")
    
    # 3. Code that violates private rule
    (project_root / "api" / "routes.py").write_text(
        "from domain._internal import helper\n"
        "from domain.service import process\n"
    )
    
    # 4. Deep internal module for strict boundary rule
    (project_root / "domain" / "service.py").write_text("def process(): pass")

    config = AnalysisConfig(layer_rules=[], encapsulation_boundaries=["domain"])
    result = analyze(project_root, config)
    
    encap_findings = [f for f in result.findings if f.kind == FindingKind.ENCAPSULATION_VIOLATION]
    
    # Should find 2 violations:
    # 1. api.routes imported domain._internal (Private rule)
    # 2. api.routes imported domain.service directly, bypassing boundary "domain"
    
    assert len(encap_findings) == 2
    
    # Private rule check
    private_violation = next(f for f in encap_findings if "private module" in f.message)
    assert private_violation.severity == Severity.WARNING
    assert "api.routes" in private_violation.location.module
    
    # Boundary rule check
    boundary_violation = next(f for f in encap_findings if "Bypassed public API" in f.message)
    assert boundary_violation.severity == Severity.ERROR
    assert "api.routes" in boundary_violation.location.module
