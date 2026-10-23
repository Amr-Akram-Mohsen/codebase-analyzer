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
    DEFAULT_ENTRY_POINTS = ("migrations", "alembic", "scripts", "bin", "setup.py", "manage.py", "demo", "example", "helpers")
    
    # Collect all string literals across the entire project
    all_strings = set()
    for m in modules:
        all_strings.update(getattr(m, "string_literals", []))
    
    for m in modules:
        if getattr(m, "has_main_block", False):
            continue
            
        qname = m.qualified_name
        
        # If the module's qualified name appears as a full module or dotted attribute path ANYWHERE in the project,
        # it is highly likely to be dynamically loaded (e.g., FastAPI routers, Django apps, Celery tasks).
        is_dynamic = False
        for s in all_strings:
            if s == qname or s.startswith(f"{qname}.") or s.endswith(f".{qname}") or f".{qname}." in s:
                is_dynamic = True
                break
        if is_dynamic:
            continue
            
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
                    message=f"'{qname}' is never imported",
                    location=Location(module=qname, line=None),
                )
            )
            
    return findings


def detect_dead_symbols(
    modules: list[Module], entry_points: list[str] = None
) -> list[Finding]:
    """
    Detects unused functions, classes, and global variables/constants across the codebase.
    """
    if entry_points is None:
        entry_points = []
        
    findings = []
    
    DEFAULT_ENTRY_POINTS = ("migrations", "alembic", "scripts", "bin", "setup.py", "manage.py", "demo", "example", "helpers")
    FRAMEWORK_DECORATOR_KEYWORDS = (
        "get", "post", "put", "delete", "patch", "route", "router", "endpoint",
        "fixture", "mark", "task", "job", "receiver", "signal", "hook",
        "property", "cached_property", "classmethod", "staticmethod", "abstractmethod",
        "validator", "field_validator", "root_validator", "override", "listener", "command"
    )
    
    # 1. Aggregate all project-wide loaded names, attribute accesses, and imported symbols
    all_referenced_names: set[str] = set()
    all_strings: set[str] = set()
    
    for m in modules:
        all_referenced_names.update(getattr(m, "referenced_names", set()))
        all_strings.update(getattr(m, "string_literals", []))
        for imp in m.imports:
            parts = imp.target_module.split(".")
            all_referenced_names.add(parts[-1])
            
    # 2. Check each module's symbols
    for m in modules:
        path_str = m.path.replace("\\", "/")
        
        # Skip entry points, tests, __init__, and scripts
        if getattr(m, "has_main_block", False):
            continue
        if path_str.endswith("__init__.py") or path_str.endswith("__main__.py") or path_str == "__main__.py":
            continue
        if "test_" in path_str or "/tests/" in path_str or path_str.startswith("tests/"):
            continue
        if path_str == "conftest.py" or path_str.endswith("/conftest.py"):
            continue
            
        is_default_entry = any(
            path_str == dep or path_str.startswith(f"{dep}/") or path_str.startswith(f"{dep}_")
            for dep in DEFAULT_ENTRY_POINTS
        )
        if is_default_entry:
            continue
            
        is_explicit_entry = any(
            m.qualified_name == ep or m.qualified_name.startswith(ep + ".")
            for ep in entry_points
        )
        if is_explicit_entry:
            continue
            
        exported = getattr(m, "exported_names", set())
        
        def is_exempt_name(name: str) -> bool:
            return (
                name.startswith("__")
                or name.startswith("test_")
                or name.startswith("Test")
                or name in exported
            )
            
        def has_framework_decorator(decorators: list[str]) -> bool:
            for dec in decorators:
                dec_lower = dec.lower()
                if any(kw in dec_lower for kw in FRAMEWORK_DECORATOR_KEYWORDS):
                    return True
            return False
            
        # Check Top-level functions & methods
        for fn in m.functions:
            short_name = fn.name.split(".")[-1]
            
            if is_exempt_name(short_name):
                continue
                
            if has_framework_decorator(fn.decorators):
                continue
                
            if short_name not in all_referenced_names and short_name not in all_strings:
                symbol_type = "method" if fn.is_method else "function"
                findings.append(
                    Finding(
                        kind=FindingKind.DEAD_CODE,
                        severity=Severity.WARNING,
                        message=f"Unused {symbol_type} '{fn.name}'",
                        location=Location(module=m.qualified_name, line=fn.line_number, end_line=fn.end_line_number),
                    )
                )
                
        # Check Classes
        for cls in m.classes:
            if is_exempt_name(cls.name):
                continue
                
            if has_framework_decorator(cls.decorators):
                continue
                
            if cls.name not in all_referenced_names and cls.name not in all_strings:
                findings.append(
                    Finding(
                        kind=FindingKind.DEAD_CODE,
                        severity=Severity.WARNING,
                        message=f"Unused class '{cls.name}'",
                        location=Location(module=m.qualified_name, line=cls.line_number, end_line=cls.end_line_number),
                    )
                )
                
        # Check Variables / Constants
        for var in getattr(m, "variables", []):
            if is_exempt_name(var.name):
                continue
                
            if var.name not in all_referenced_names and var.name not in all_strings:
                findings.append(
                    Finding(
                        kind=FindingKind.DEAD_CODE,
                        severity=Severity.WARNING,
                        message=f"Unused variable '{var.name}'",
                        location=Location(module=m.qualified_name, line=var.line_number),
                    )
                )
                
    findings.sort(key=lambda f: (f.location.module if f.location else "", f.location.line or 0))
    return findings
