"""
Tests for the dead code (orphaned module) detection engine.
"""

from codebase_analyzer.analysis.dead_code import detect_dead_code
from codebase_analyzer.core.model import FindingKind, Module


class TestDeadCode:
    def test_detects_orphaned_module(self) -> None:
        modules = [
            Module(
                path="myapp/used.py",
                qualified_name="myapp.used",
                classes=[],
                functions=[],
                imports=[],
            ),
            Module(
                path="myapp/orphan.py",
                qualified_name="myapp.orphan",
                classes=[],
                functions=[],
                imports=[],
            ),
        ]
        
        # used.py is imported by someone, orphan.py is not
        graph = {
            "myapp.other": ["myapp.used"]
        }
        
        findings = detect_dead_code(modules, graph, entry_points=[])
        
        assert len(findings) == 1
        assert findings[0].kind == FindingKind.DEAD_CODE
        assert findings[0].location.module == "myapp.orphan"

    def test_ignores_entry_points(self) -> None:
        modules = [
            Module(
                path="myapp/cli.py",
                qualified_name="myapp.cli",
                classes=[],
                functions=[],
                imports=[],
            )
        ]
        
        graph = {}
        
        # Without whitelist, it's flagged
        findings1 = detect_dead_code(modules, graph, entry_points=[])
        assert len(findings1) == 1
        
        # With whitelist, it's ignored
        findings2 = detect_dead_code(modules, graph, entry_points=["myapp.cli"])
        assert len(findings2) == 0

    def test_ignores_standard_files(self) -> None:
        modules = [
            Module(
                path="myapp/__init__.py",
                qualified_name="myapp.__init__",
                classes=[],
                functions=[],
                imports=[],
            ),
            Module(
                path="myapp/__main__.py",
                qualified_name="myapp.__main__",
                classes=[],
                functions=[],
                imports=[],
            ),
            Module(
                path="tests/test_foo.py",
                qualified_name="tests.test_foo",
                classes=[],
                functions=[],
                imports=[],
            ),
        ]
        
        graph = {}
        findings = detect_dead_code(modules, graph, entry_points=[])
        
        # None of these should be flagged as orphaned
        assert len(findings) == 0

    def test_ignores_default_ubiquitous_entry_points(self) -> None:
        modules = [
            Module(
                path="migrations/env.py",
                qualified_name="migrations.env",
                classes=[],
                functions=[],
                imports=[],
            ),
            Module(
                path="scripts/seed.py",
                qualified_name="scripts.seed",
                classes=[],
                functions=[],
                imports=[],
            ),
            Module(
                path="manage.py",
                qualified_name="manage",
                classes=[],
                functions=[],
                imports=[],
            ),
        ]
        
        graph = {}
        findings = detect_dead_code(modules, graph, entry_points=[])
        
        # None of these should be flagged as orphaned because they are in DEFAULT_ENTRY_POINTS
        assert len(findings) == 0

    def test_dynamic_string_literals_boundary_precision(self) -> None:
        # Module named "myapp.utils"
        m1 = Module(
            path="myapp/utils.py",
            qualified_name="myapp.utils",
            classes=[],
            functions=[],
            imports=[],
            string_literals=["myapp.utils.helper", "my_utils_unrelated"],
        )
        # Module named "myapp.core"
        m2 = Module(
            path="myapp/core.py",
            qualified_name="myapp.core",
            classes=[],
            functions=[],
            imports=[],
            string_literals=["hardcore_processing"],
        )
        
        # m1 ("myapp.utils") is referenced as "myapp.utils.helper" -> should be ignored (dynamic)
        # m2 ("myapp.core") only has "hardcore_processing" (substring without dot) -> should NOT be ignored
        findings = detect_dead_code([m1, m2], graph={}, entry_points=[])
        
        assert len(findings) == 1
        assert findings[0].location.module == "myapp.core"
