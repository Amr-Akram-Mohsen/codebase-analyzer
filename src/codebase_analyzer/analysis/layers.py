"""
Checks architecture layer constraints.
"""

from codebase_analyzer.core.model import Finding, FindingKind, LayerRule, Location, Module, Severity


def _get_layer_index(qualified_name: str, rules: list[LayerRule]) -> int | None:
    """
    Returns the index of the first layer rule that matches the module.
    If no rule matches, returns None.
    """
    for i, rule in enumerate(rules):
        for prefix in rule.prefixes:
            # Check if it's an exact match or a submodule (e.g. 'a.b' matches 'a.b.c' and 'a.b')
            if qualified_name == prefix or qualified_name.startswith(f"{prefix}."):
                return i
    return None


def check_layer_violations(modules: list[Module], rules: list[LayerRule]) -> list[Finding]:
    """
    Verifies that modules do not import modules from a higher layer.
    
    A module in layer `i` may only import from layer `j` where `j >= i`.
    If a module imports from layer `j < i`, it is a LAYER_VIOLATION.
    Modules that do not match any layer rule are ignored.
    """
    if not rules:
        return []
        
    findings = []
    
    # Precompute layer assignments for fast lookup
    # Only map project-internal modules
    module_layers: dict[str, int] = {}
    for m in modules:
        idx = _get_layer_index(m.qualified_name, rules)
        if idx is not None:
            module_layers[m.qualified_name] = idx
            
    sorted_known = sorted(list(module_layers.keys()), key=len, reverse=True)
            
    for m in modules:
        source_idx = module_layers.get(m.qualified_name)
        if source_idx is None:
            continue
            
        for imp in m.imports:
            target = imp.target_module
            target_idx = None
            matched_module = None
            
            for k in sorted_known:
                if target == k or target.startswith(f"{k}."):
                    target_idx = module_layers[k]
                    matched_module = k
                    break
                    
            if target_idx is None or matched_module is None:
                # Target is either external or not assigned to a layer, so it's ignored
                continue
                
            if target_idx < source_idx:
                source_layer = rules[source_idx].name
                target_layer = rules[target_idx].name
                message = (
                    f"Architecture violation: '{m.qualified_name}' (layer '{source_layer}') "
                    f"imports '{matched_module}' (layer '{target_layer}'). "
                    f"Layer '{source_layer}' cannot depend on layer '{target_layer}'."
                )
                findings.append(
                    Finding(
                        kind=FindingKind.LAYER_VIOLATION,
                        severity=Severity.ERROR,
                        message=message,
                        location=Location(module=m.qualified_name, line=imp.line_number),
                    )
                )
                
    # Sort findings by location module and line to ensure deterministic output
    findings.sort(key=lambda f: (f.location.module if f.location else "", f.location.line if f.location and f.location.line else 0))
    
    return findings
