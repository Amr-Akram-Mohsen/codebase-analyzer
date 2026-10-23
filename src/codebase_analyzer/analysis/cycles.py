"""
Detects import cycles in project-internal dependency graphs.
"""

from codebase_analyzer.core.model import Finding, FindingKind, Severity, Location


def _find_cycles_in_scc(scc: list[str], graph: dict[str, set[str]]) -> list[list[str]]:
    """
    Extracts true directed elementary cycles from a strongly connected component.
    """
    scc_set = set(scc)
    subgraph = {u: sorted([v for v in graph.get(u, set()) if v in scc_set]) for u in scc}
    
    found_cycles: list[list[str]] = []
    seen_tuples: set[tuple[str, ...]] = set()
    
    def dfs(start: str, current: str, path: list[str], visited: set[str]) -> None:
        for nxt in subgraph.get(current, []):
            if nxt == start:
                if len(path) > 1:
                    min_idx = path.index(min(path))
                    canonical = tuple(path[min_idx:] + path[:min_idx])
                    if canonical not in seen_tuples:
                        seen_tuples.add(canonical)
                        found_cycles.append(list(canonical))
            elif nxt not in visited and nxt > start:
                visited.add(nxt)
                dfs(start, nxt, path + [nxt], visited)
                visited.remove(nxt)
                
    nodes = sorted(scc)
    for start_node in nodes:
        dfs(start_node, start_node, [start_node], {start_node})
        
    if not found_cycles:
        # Fallback to trace any directed cycle in the SCC
        def find_any_cycle(u: str, current_path: list[str], in_path: dict[str, int]) -> list[str] | None:
            for v in subgraph.get(u, []):
                if v in in_path:
                    cycle_start = in_path[v]
                    return current_path[cycle_start:]
                res = find_any_cycle(v, current_path + [v], {**in_path, v: len(current_path)})
                if res:
                    return res
            return None
            
        fallback = find_any_cycle(nodes[0], [nodes[0]], {nodes[0]: 0})
        if fallback:
            min_idx = fallback.index(min(fallback))
            canonical_fb = fallback[min_idx:] + fallback[:min_idx]
            return [canonical_fb]
        return [nodes]
        
    return found_cycles


def find_cycles(graph: dict[str, set[str]]) -> list[Finding]:
    """
    Detects circular dependencies in the module graph using Tarjan's SCC algorithm
    combined with directed cycle path extraction.
    
    Each directed cycle is reported with its true dependency path (e.g. A -> B -> C -> A).
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
            
            # SCC of size > 1 is a cycle (extract true directed cycle paths)
            if len(scc) > 1:
                directed_cycles = _find_cycles_in_scc(scc, graph)
                cycles.extend(directed_cycles)
            # Self-loop
            elif len(scc) == 1 and node in graph.get(node, set()):
                cycles.append([node])
                
    for node in graph:
        if node not in indices:
            strongconnect(node)
            
    findings = []
    for cycle in sorted(cycles, key=lambda c: (c[0], len(c), c)):
        modules_str = " -> ".join(cycle + [cycle[0]])
        message = f"Cycle: {modules_str}"
        findings.append(
            Finding(
                kind=FindingKind.IMPORT_CYCLE,
                severity=Severity.ERROR,
                message=message,
                location=Location(module=cycle[0], line=None),
            )
        )
        
    return findings
