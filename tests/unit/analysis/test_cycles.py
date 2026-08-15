"""
Unit tests for analysis/cycles.py.
"""

from codebase_analyzer.analysis.cycles import find_cycles
from codebase_analyzer.core.model import FindingKind


class TestCycles:
    def test_empty_graph(self) -> None:
        graph: dict[str, set[str]] = {}
        findings = find_cycles(graph)
        assert len(findings) == 0

    def test_two_node_cycle(self) -> None:
        graph = {
            "myapp.a": {"myapp.b"},
            "myapp.b": {"myapp.a"},
        }
        findings = find_cycles(graph)
        assert len(findings) == 1
        f = findings[0]
        assert f.kind == FindingKind.IMPORT_CYCLE
        assert "myapp.a" in f.message
        assert "myapp.b" in f.message

    def test_three_node_cycle(self) -> None:
        graph = {
            "myapp.a": {"myapp.b"},
            "myapp.b": {"myapp.c"},
            "myapp.c": {"myapp.a"},
        }
        findings = find_cycles(graph)
        assert len(findings) == 1
        assert "myapp.a" in findings[0].message
        assert "myapp.b" in findings[0].message
        assert "myapp.c" in findings[0].message

    def test_two_independent_cycles(self) -> None:
        graph = {
            "myapp.a": {"myapp.b"},
            "myapp.b": {"myapp.a"},
            "myapp.x": {"myapp.y"},
            "myapp.y": {"myapp.x"},
        }
        findings = find_cycles(graph)
        assert len(findings) == 2

    def test_linear_chain(self) -> None:
        graph = {
            "myapp.a": {"myapp.b"},
            "myapp.b": {"myapp.c"},
            "myapp.c": set(),
        }
        findings = find_cycles(graph)
        assert len(findings) == 0

    def test_self_loop(self) -> None:
        graph = {
            "myapp.a": {"myapp.a"},
        }
        findings = find_cycles(graph)
        assert len(findings) == 1
        assert "myapp.a" in findings[0].message
