"""
Unit tests for the God Object metrics engine.
"""

from codebase_analyzer.analysis.metrics import detect_god_objects
from codebase_analyzer.core.model import FindingKind, Module


class TestMetricsEngine:
    def test_no_god_objects(self) -> None:
        modules = [
            Module(path="a.py", qualified_name="a", classes=[], functions=[], imports=[]),
            Module(path="b.py", qualified_name="b", classes=[], functions=[], imports=[]),
        ]
        
        # a -> b
        graph = {"a": ["b"]}
        
        findings = detect_god_objects(modules, graph, max_fan_out=2)
        assert len(findings) == 0

    def test_detects_high_fan_out(self) -> None:
        modules = [
            Module(path="god.py", qualified_name="god", classes=[], functions=[], imports=[]),
        ]
        
        # god imports 3 modules
        graph = {"god": ["a", "b", "c"]}
        
        findings = detect_god_objects(modules, graph, max_fan_out=2)
        assert len(findings) == 1
        
        f = findings[0]
        assert f.kind == FindingKind.GOD_OBJECT
        assert "'god' (Fan-Out: 3, Fan-In: 0, Instability: 1.00)" == f.message

    def test_detects_danger_zone(self) -> None:
        modules = [
            Module(path="god.py", qualified_name="god", classes=[], functions=[], imports=[]),
        ]
        
        # god imports 3 modules (Fan-Out = 3)
        # 6 other modules import god (Fan-In = 6)
        graph = {
            "god": ["a", "b", "c"],
            "d": ["god"],
            "e": ["god"],
            "f": ["god"],
            "g": ["god"],
            "h": ["god"],
            "i": ["god"],
        }
        
        findings = detect_god_objects(modules, graph, max_fan_out=2)
        assert len(findings) == 1
        
        f = findings[0]
        assert f.kind == FindingKind.GOD_OBJECT
        assert "'god' (Fan-Out: 3, Fan-In: 6, Instability: 0.33)" == f.message
