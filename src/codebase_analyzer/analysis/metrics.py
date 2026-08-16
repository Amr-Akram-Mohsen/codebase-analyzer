"""
Analyzes architectural metrics and identifies God Objects.
"""

from codebase_analyzer.core.model import Finding, FindingKind, Location, Module, Severity


def detect_god_objects(
    modules: list[Module], graph: dict[str, list[str]], max_fan_out: int
) -> list[Finding]:
    """
    Calculates Fan-In and Fan-Out for each module to detect highly unstable 'God Objects'.
    Provides tailored architectural refactoring advice based on the combination of metrics.
    """
    findings = []
    
    # Calculate Fan-In
    # graph is source -> list[target] (this represents Fan-Out directly)
    fan_in: dict[str, int] = {m.qualified_name: 0 for m in modules}
    for targets in graph.values():
        for t in targets:
            if t in fan_in:
                fan_in[t] += 1
                
    for m in modules:
        qname = m.qualified_name
        # Internal Fan-Out (only dependencies inside the project)
        fan_out = len(set(graph.get(qname, [])))
        f_in = fan_in.get(qname, 0)
        
        # We only flag if it exceeds the maximum allowed fan out and is not an __init__.py
        if fan_out > max_fan_out and not m.path.replace("\\", "/").endswith("__init__.py"):
            # Calculate Instability (0 = stable, 1 = unstable)
            instability = fan_out / (f_in + fan_out) if (f_in + fan_out) > 0 else 1.0
            
            # Tailor the advice based on Fan-In
            if f_in > 5:
                advice = (
                    "This module is a severe bottleneck (The Danger Zone). "
                    "It relies on many files (highly unstable) but is also relied upon by many (hard to change). "
                    "Suggestion: Extract the core interfaces/DTOs into a separate stable module, and split the implementation into smaller domain services."
                )
            else:
                advice = (
                    "This module acts as a massive orchestrator. "
                    "It heavily depends on the rest of the system, making it fragile to changes elsewhere. "
                    "Suggestion: Consider applying the Facade or Mediator pattern to delegate the heavy lifting to smaller, focused handlers."
                )
                
            msg = f"'{qname}' (Fan-Out: {fan_out}, Fan-In: {f_in}, Instability: {instability:.2f})"
            
            findings.append(
                Finding(
                    kind=FindingKind.GOD_OBJECT,
                    severity=Severity.WARNING,
                    message=msg,
                    location=Location(module=qname, line=None),
                )
            )
            
    # Sort findings by highest fan-out first
    findings.sort(key=lambda f: float(f.message.split("Fan-Out: ")[1].split(",")[0]), reverse=True)
            
    return findings


def detect_complex_functions(
    modules: list[Module], max_complexity: int
) -> list[Finding]:
    """
    Identifies functions with Cyclomatic Complexity exceeding the threshold.
    """
    findings = []
    
    for module in modules:
        for func in module.functions:
            if func.complexity > max_complexity:
                msg = f"'{func.name}' (Complexity: {func.complexity})"
                findings.append(
                    Finding(
                        kind=FindingKind.COMPLEX_FUNCTION,
                        severity=Severity.WARNING,
                        message=msg,
                        location=Location(module=module.qualified_name, line=func.line_number, end_line=func.end_line_number),
                    )
                )
                
    findings.sort(key=lambda f: int(f.message.split("Complexity: ")[1].split(")")[0]), reverse=True)
                
    return findings
