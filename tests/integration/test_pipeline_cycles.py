"""
Integration tests for the parser -> dependency graph -> cycle detection pipeline.
"""

from pathlib import Path

from codebase_analyzer.analysis.cycles import find_cycles
from codebase_analyzer.analysis.dependencies import build_dependency_graph
from codebase_analyzer.core.model import FindingKind
from codebase_analyzer.python.discovery import discover_python_files
from codebase_analyzer.python.parser import parse_module


def test_pipeline_detects_cycle() -> None:
    # 1. Discovery + parser
    project_root = Path(__file__).parent.parent / "fixtures" / "cyclic_project"
    files = discover_python_files(project_root)
    assert len(files) == 3  # __init__.py, module_a.py, module_b.py
    
    modules = []
    for f in files:
        res = parse_module(f, project_root)
        from codebase_analyzer.core.model import Module
        assert isinstance(res, Module), f"Failed to parse {f}: {res.message}"
        modules.append(res)
        
    # 2. Build graph
    graph = build_dependency_graph(modules)
    
    # 5. Assert external imports do not appear as graph nodes
    # module_a.py imports `os`
    assert "os" not in graph
    
    # 3. Find cycles
    findings = find_cycles(graph)
    
    # 4. Assert exactly one IMPORT_CYCLE finding, naming the expected modules
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == FindingKind.IMPORT_CYCLE
    assert "module_a" in f.message
    assert "module_b" in f.message
