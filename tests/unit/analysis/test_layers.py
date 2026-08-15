"""
Unit tests for analysis/layers.py.
"""

from codebase_analyzer.analysis.layers import check_layer_violations
from codebase_analyzer.core.model import FindingKind, ImportRef, LayerRule, Module


class TestLayers:
    def test_no_violations(self) -> None:
        rules = [
            LayerRule(name="cli", prefixes=["myapp.cli"]),
            LayerRule(name="api", prefixes=["myapp.api"]),
            LayerRule(name="core", prefixes=["myapp.core"]),
        ]
        
        modules = [
            Module(
                path="cli.py",
                qualified_name="myapp.cli",
                classes=[],
                functions=[],
                imports=[ImportRef("myapp.cli", "myapp.api", 10), ImportRef("myapp.cli", "myapp.core", 11)],
            ),
            Module(
                path="api.py",
                qualified_name="myapp.api",
                classes=[],
                functions=[],
                imports=[ImportRef("myapp.api", "myapp.core", 5)],
            ),
            Module(
                path="core.py",
                qualified_name="myapp.core",
                classes=[],
                functions=[],
                imports=[],
            )
        ]
        
        findings = check_layer_violations(modules, rules)
        assert len(findings) == 0

    def test_layer_violation(self) -> None:
        rules = [
            LayerRule(name="cli", prefixes=["myapp.cli"]),
            LayerRule(name="core", prefixes=["myapp.core"]),
        ]
        
        modules = [
            Module(
                path="core.py",
                qualified_name="myapp.core",
                classes=[],
                functions=[],
                imports=[ImportRef("myapp.core", "myapp.cli", 5)],
            ),
            Module(
                path="cli.py",
                qualified_name="myapp.cli",
                classes=[],
                functions=[],
                imports=[],
            )
        ]
        
        findings = check_layer_violations(modules, rules)
        assert len(findings) == 1
        assert findings[0].kind == FindingKind.LAYER_VIOLATION
        assert "'myapp.core' (layer 'core') imports 'myapp.cli' (layer 'cli')" in findings[0].message
        assert findings[0].location is not None
        assert findings[0].location.module == "myapp.core"
        assert findings[0].location.line == 5

    def test_same_layer_import_allowed(self) -> None:
        rules = [
            LayerRule(name="api", prefixes=["myapp.api"]),
        ]
        
        modules = [
            Module(
                path="api/a.py",
                qualified_name="myapp.api.a",
                classes=[],
                functions=[],
                imports=[ImportRef("myapp.api.a", "myapp.api.b", 5)],
            ),
            Module(
                path="api/b.py",
                qualified_name="myapp.api.b",
                classes=[],
                functions=[],
                imports=[],
            )
        ]
        
        findings = check_layer_violations(modules, rules)
        assert len(findings) == 0

    def test_unmapped_modules_ignored(self) -> None:
        rules = [
            LayerRule(name="api", prefixes=["myapp.api"]),
        ]
        
        modules = [
            Module(
                path="tests/a.py",
                qualified_name="myapp.tests.a",
                classes=[],
                functions=[],
                imports=[ImportRef("myapp.tests.a", "myapp.api.b", 5)],
            ),
            Module(
                path="api/b.py",
                qualified_name="myapp.api.b",
                classes=[],
                functions=[],
                imports=[ImportRef("myapp.api.b", "myapp.tests.a", 10)],
            )
        ]
        
        findings = check_layer_violations(modules, rules)
        assert len(findings) == 0
