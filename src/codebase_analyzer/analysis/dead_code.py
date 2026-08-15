"""
Detects orphaned code (e.g. files that are never imported anywhere in the project).
"""

from pathlib import Path

from codebase_analyzer.core.model import Finding, FindingKind, Location, Module, Severity


def detect_dead_code(
    modules: list[Module], graph: dict[str, list[str]], entry_points: list[str]
) -> list[Finding]:
    """
    Calculates the Fan-In for each module in the project.
    If a module has Fan-In == 0, and is not an entry point, __init__, or test file,
    it is flagged as DEAD_CODE.
    """
    findings = []
    
    # Calculate Fan-In
    # graph is source -> list[target]
    fan_in: dict[str, int] = {m.qualified_name: 0 for m in modules}
    for targets in graph.values():
        for t in targets:
            if t in fan_in:
                fan_in[t] += 1
                
    # Entry points are typically whitelist of qualified names or prefixes
    # We will treat them as prefixes so you can whitelist `cli` or `cli.main`
    
    # Default ubiquitous entry points in the Python ecosystem
    DEFAULT_ENTRY_POINTS = ("migrations", "alembic", "scripts", "bin", "setup.py", "manage.py", "demo", "example")
    
    for m in modules:
        qname = m.qualified_name
        path_str = m.path.replace("\\", "/")
        
        # Check standard ignores (using path instead of qualified name because __init__ is stripped from qname)
        if path_str.endswith("__init__.py") or path_str.endswith("__main__.py") or path_str == "__main__.py":
            continue
            
        if "test_" in path_str or "/tests/" in path_str or path_str.startswith("tests/"):
            continue
            
        if path_str == "conftest.py" or path_str.endswith("/conftest.py"):
            continue
            
        # Check default ubiquitous entry points
        is_default = False
        for dep in DEFAULT_ENTRY_POINTS:
            if path_str == dep or path_str.startswith(f"{dep}/") or path_str.startswith(f"{dep}_"):
                is_default = True
                break
                
        if is_default:
            continue
            
        # Check if it's explicitly allowed as an entry point
        is_entry_point = False
        for ep in entry_points:
            if qname == ep or qname.startswith(ep + "."):
                is_entry_point = True
                break
                
        if is_entry_point:
            continue
            
        # Check Fan-In
        if fan_in.get(qname, 0) == 0:
            findings.append(
                Finding(
                    kind=FindingKind.DEAD_CODE,
                    severity=Severity.WARNING,
                    message=f"Orphaned Module: '{qname}' is never imported by any other file.",
                    location=Location(module=qname, line=None),
                )
            )
            
    return findings
