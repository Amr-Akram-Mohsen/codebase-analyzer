from codebase_analyzer.analysis.encapsulation import detect_encapsulation_violations
from codebase_analyzer.core.model import FindingKind, ImportRef, Module, Severity


class TestEncapsulation:
    def test_private_module_allowed_within_package(self) -> None:
        modules = [
            Module(
                path="myapp/domain/service.py",
                qualified_name="myapp.domain.service",
                classes=[],
                functions=[],
                imports=[ImportRef(source_module="myapp.domain.service", target_module="myapp.domain._internal.db", line_number=5)],
            )
        ]
        
        findings = detect_encapsulation_violations(modules, boundaries=[])
        assert len(findings) == 0

    def test_private_module_blocked_outside_package(self) -> None:
        modules = [
            Module(
                path="myapp/other/service.py",
                qualified_name="myapp.other.service",
                classes=[],
                functions=[],
                imports=[ImportRef(source_module="myapp.other.service", target_module="myapp.domain._internal.db", line_number=5)],
            )
        ]
        
        findings = detect_encapsulation_violations(modules, boundaries=[])
        assert len(findings) == 1
        assert findings[0].kind == FindingKind.ENCAPSULATION_VIOLATION
        assert findings[0].severity == Severity.WARNING
        assert "private module" in findings[0].message
        assert findings[0].location.module == "myapp.other.service"

    def test_boundary_rule_blocks_deep_imports(self) -> None:
        modules = [
            Module(
                path="myapp/api/routes.py",
                qualified_name="myapp.api.routes",
                classes=[],
                functions=[],
                imports=[ImportRef(source_module="myapp.api.routes", target_module="myapp.domain.service", line_number=10)],
            )
        ]
        
        findings = detect_encapsulation_violations(modules, boundaries=["myapp.domain"])
        assert len(findings) == 1
        assert findings[0].kind == FindingKind.ENCAPSULATION_VIOLATION
        assert findings[0].severity == Severity.ERROR
        assert "bypassed public API" in findings[0].message

    def test_boundary_rule_allows_root_import(self) -> None:
        modules = [
            Module(
                path="myapp/api/routes.py",
                qualified_name="myapp.api.routes",
                classes=[],
                functions=[],
                imports=[ImportRef(source_module="myapp.api.routes", target_module="myapp.domain", line_number=10)],
            )
        ]
        
        findings = detect_encapsulation_violations(modules, boundaries=["myapp.domain"])
        assert len(findings) == 0

    def test_boundary_rule_allows_internal_imports(self) -> None:
        modules = [
            Module(
                path="myapp/domain/api.py",
                qualified_name="myapp.domain.api",
                classes=[],
                functions=[],
                imports=[ImportRef(source_module="myapp.domain.api", target_module="myapp.domain.service", line_number=10)],
            )
        ]
        
        findings = detect_encapsulation_violations(modules, boundaries=["myapp.domain"])
        assert len(findings) == 0

    def test_boundary_rule_allows_configured_public_api(self) -> None:
        modules = [
            Module(
                path="myapp/api/routes.py",
                qualified_name="myapp.api.routes",
                classes=[],
                functions=[],
                imports=[
                    # This targets the public API, should be allowed
                    ImportRef(source_module="myapp.api.routes", target_module="myapp.domain.public", line_number=1),
                    # This targets a child of the public API, should be allowed
                    ImportRef(source_module="myapp.api.routes", target_module="myapp.domain.public.utils", line_number=2),
                    # This bypasses the public API, should be blocked
                    ImportRef(source_module="myapp.api.routes", target_module="myapp.domain.internal.db", line_number=3),
                ],
            )
        ]
        
        findings = detect_encapsulation_violations(
            modules, 
            boundaries=["myapp.domain"], 
            public_apis={"myapp.domain": ["myapp.domain.public"]}
        )
        
        # Only the 3rd import should be blocked
        assert len(findings) == 1
        assert "bypassed public API by directly importing 'myapp.domain.internal.db'" in findings[0].message
