"""
Detects import cycles in project-internal dependency graphs.
"""

from codebase_analyzer.core.model import Finding, FindingKind, Severity


def find_cycles(graph: dict[str, set[str]]) -> list[Finding]:
    """
    Detects circular dependencies in the module graph using Tarjan's SCC algorithm.
    
    Each strongly connected component with more than one node represents a cycle.
    Self-loops (a module importing itself) are also reported as cycles.
    """
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    
    cycles: list[list[str]] = []
    
    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        
        for neighbor in graph.get(node, set()):
            if neighbor not in indices:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])
                
        if lowlinks[node] == indices[node]:
            scc: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            
            # SCC of size > 1 is a cycle
            if len(scc) > 1:
                cycles.append(sorted(scc))
            # Self-loop
            elif len(scc) == 1 and node in graph.get(node, set()):
                cycles.append([node])
                
    for node in graph:
        if node not in indices:
            strongconnect(node)
            
    findings = []
    for cycle in sorted(cycles, key=lambda c: c[0]):
        modules_str = " -> ".join(cycle + [cycle[0]])
        message = f"Circular import detected: {modules_str}"
        findings.append(
            Finding(
                kind=FindingKind.IMPORT_CYCLE,
                severity=Severity.ERROR,
                message=message,
                location=None,
            )
        )
        
    return findings
