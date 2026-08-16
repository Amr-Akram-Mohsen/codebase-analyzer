"""
Enforces public API encapsulation boundaries.
"""

from codebase_analyzer.core.model import Finding, FindingKind, Location, Module, Severity


def detect_encapsulation_violations(
    modules: list[Module], boundaries: list[str], public_apis: dict[str, list[str]] = None
) -> list[Finding]:
    """
    Detects two types of encapsulation violations:
    1. Private Module Rule: Importing a module with a leading underscore (e.g., `_internal`)
       from outside its parent package.
    2. Strict Boundary Rule: If boundaries are defined, importing a sub-module of a boundary
       from outside that boundary, unless it is listed in public_apis.
    """
    if public_apis is None:
        public_apis = {}
        
    findings = []
    
    # Pre-calculate boundary prefixes (e.g., "myapp.domain.")
    boundary_prefixes = [f"{b}." for b in boundaries]

    for m in modules:
        source = m.qualified_name
        if not source:
            continue
            
        for imp in m.imports:
            target = imp.target_module
            target_parts = target.split(".")
            
            # Rule 1: Private Module Enforcement
            private_index = -1
            for i, part in enumerate(target_parts):
                if part.startswith("_") and not part.startswith("__"):
                    private_index = i
                    break
                    
            if private_index != -1:
                # The parent package that is allowed to access this private module
                parent_parts = target_parts[:private_index]
                parent_prefix = ".".join(parent_parts) + "." if parent_parts else ""
                
                # If parent_prefix is empty, the private module is at the root (e.g., `_utils.py`)
                # Only modules starting with `_utils` would be allowed.
                if not source.startswith(parent_prefix):
                    findings.append(
                        Finding(
                            kind=FindingKind.ENCAPSULATION_VIOLATION,
                            severity=Severity.WARNING,
                            message=f"Imported private module '{target}'",
                            location=Location(module=source, line=imp.line_number),
                        )
                    )
                    # Skip boundary checks if we already flagged as private violation
                    continue
                    
            # Rule 2: Strict Boundary Enforcement
            for boundary, boundary_prefix in zip(boundaries, boundary_prefixes):
                # Is the target INSIDE the boundary? (e.g. target="domain.internal", boundary="domain.")
                if target.startswith(boundary_prefix):
                    # Is the source OUTSIDE the boundary?
                    if not (source.startswith(boundary_prefix) or source == boundary):
                        # It's an outside import targeting inside the boundary.
                        
                        # Check if it hits an allowed public API
                        allowed_public_apis = public_apis.get(boundary, [])
                        is_public_api = False
                        for pub in allowed_public_apis:
                            if target == pub or target.startswith(f"{pub}."):
                                is_public_api = True
                                break
                                
                        if not is_public_api:
                            findings.append(
                                Finding(
                                    kind=FindingKind.ENCAPSULATION_VIOLATION,
                                    severity=Severity.ERROR,
                                    message=f"Bypassed public API by directly importing '{target}'",
                                    location=Location(module=source, line=imp.line_number),
                                )
                            )
                        break

    # Sort findings by location to ensure deterministic output
    findings.sort(key=lambda f: (f.location.module if f.location else "", f.location.line if f.location else 0))
    return findings
