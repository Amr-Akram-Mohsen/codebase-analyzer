"""
Builds project-internal dependency graphs from Module IR objects.
"""

from codebase_analyzer.core.model import Module


def build_dependency_graph(modules: list[Module]) -> dict[str, set[str]]:
    """
    Constructs a project-internal module dependency graph.
    
    Includes only import edges where the target module is part of the analyzed
    project (present in the input modules list). External libraries and stdlib
    imports are silently excluded.
    
    Returns a dictionary mapping each module's qualified_name to the set of
    qualified_names of the modules it imports. Every module from the input list
    will appear as a key in the result.
    """
    known_modules = {module.qualified_name for module in modules}
    graph: dict[str, set[str]] = {name: set() for name in known_modules}
    
    # Sort by length descending to match the longest (most specific) module name
    sorted_known = sorted(list(known_modules), key=len, reverse=True)
    
    for module in modules:
        for imp in module.imports:
            target = imp.target_module
            for k in sorted_known:
                if target == k or target.startswith(f"{k}."):
                    graph[module.qualified_name].add(k)
                    break
                    
    return graph
