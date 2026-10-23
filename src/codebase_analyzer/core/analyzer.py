"""
Orchestrates the analysis pipeline.
"""

from pathlib import Path

from codebase_analyzer.analysis.comments import detect_commented_code
from codebase_analyzer.analysis.cycles import find_cycles
from codebase_analyzer.analysis.dependencies import build_dependency_graph
from codebase_analyzer.analysis.encapsulation import detect_encapsulation_violations
from codebase_analyzer.analysis.layers import check_layer_violations
from codebase_analyzer.analysis.naming import detect_name_collisions
from codebase_analyzer.core.model import AnalysisConfig, AnalysisResult, Finding, Module
from codebase_analyzer.python.discovery import discover_python_files
from codebase_analyzer.python.parser import parse_module


def analyze(path: str | Path, config: AnalysisConfig) -> AnalysisResult:
    """
    Runs the full analysis pipeline on the given project directory.
    
    Coordinates discovery, parsing, and analysis engines. Does not perform
    analysis itself. Returns the combined findings in an AnalysisResult.
    """
    project_root = Path(path).resolve()
    
    # 1. Discover files
    python_files = discover_python_files(project_root)
    
    # 2. Parse modules
    modules: list[Module] = []
    findings: list[Finding] = []
    
    for f in python_files:
        res = parse_module(f, project_root)
        if isinstance(res, Module):
            modules.append(res)
        else:
            findings.append(res)
            
    # 3. Build graph
    graph = build_dependency_graph(modules)
    
    # 4. Detect cycles
    cycle_findings = find_cycles(graph)
    findings.extend(cycle_findings)
    
    # 5. Detect name collisions
    naming_findings = detect_name_collisions(modules)
    findings.extend(naming_findings)
    
    # 6. Check architecture layers
    layer_findings = check_layer_violations(modules, config.layer_rules)
    findings.extend(layer_findings)
    
    # 7. Check encapsulation violations
    encapsulation_findings = detect_encapsulation_violations(
        modules, 
        config.encapsulation_boundaries, 
        config.encapsulation_public_apis
    )
    findings.extend(encapsulation_findings)
    
    # 8. Detect commented code
    commented_code_findings = detect_commented_code(modules, str(project_root))
    findings.extend(commented_code_findings)
    
    # 9. Detect dead code (orphaned modules & dead symbols)
    from codebase_analyzer.analysis.dead_code import detect_dead_code, detect_dead_symbols
    dead_code_findings = detect_dead_code(modules, graph, config.dead_code_entry_points)
    findings.extend(dead_code_findings)
    
    dead_symbol_findings = detect_dead_symbols(modules, config.dead_code_entry_points)
    findings.extend(dead_symbol_findings)
    
    # 10. Detect God Objects (metrics)
    from codebase_analyzer.analysis.metrics import detect_god_objects, detect_complex_functions
    god_object_findings = detect_god_objects(modules, graph, config.metrics_max_fan_out)
    findings.extend(god_object_findings)
    
    # 11. Detect Complex Functions
    complex_function_findings = detect_complex_functions(modules, config.metrics_max_complexity)
    findings.extend(complex_function_findings)
    
    return AnalysisResult(
        project_root=str(project_root), modules=modules, findings=findings
    )
