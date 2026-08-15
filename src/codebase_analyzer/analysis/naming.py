"""
Detects top-level name collisions.
"""

from collections import defaultdict

from codebase_analyzer.core.model import Finding, FindingKind, Location, Module, Severity


def detect_name_collisions(modules: list[Module]) -> list[Finding]:
    """
    Detects intra-file naming collisions (e.g., defining `def my_func()` twice
    in the exact same file), which is a genuine bug.
    
    Cross-file module and function collisions are intentionally ignored to 
    embrace Python namespaces and avoid pedantic noise.
    """
    findings = []
    
    for m in modules:
        # Check intra-file class collisions
        seen_classes: dict[str, list[int]] = defaultdict(list)
        for c in m.classes:
            seen_classes[c.name].append(c.line_number)
            
        for name, lines in seen_classes.items():
            if len(lines) > 1:
                lines_str = ", ".join(map(str, sorted(lines)))
                findings.append(
                    Finding(
                        kind=FindingKind.NAME_COLLISION,
                        severity=Severity.ERROR,
                        message=f"Multiple class name collisions in {m.path}:\n  - '{name}' at lines {lines_str}",
                        location=Location(module=m.qualified_name, line=lines[0]),
                    )
                )
                
        # Check intra-file function collisions
        seen_funcs: dict[str, list[int]] = defaultdict(list)
        for f in m.functions:
            seen_funcs[f.name].append(f.line_number)
            
        for name, lines in seen_funcs.items():
            if len(lines) > 1:
                lines_str = ", ".join(map(str, sorted(lines)))
                findings.append(
                    Finding(
                        kind=FindingKind.NAME_COLLISION,
                        severity=Severity.ERROR,
                        message=f"Multiple function name collisions in {m.path}:\n  - '{name}' at lines {lines_str}",
                        location=Location(module=m.qualified_name, line=lines[0]),
                    )
                )

    # Sort findings by location module to ensure deterministic output
    findings.sort(key=lambda f: (f.location.module if f.location else "", f.message))
    
    return findings
