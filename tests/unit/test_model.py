"""
Unit tests for core/model.py.

Verifies that all domain types can be constructed, that frozen dataclasses
reject field reassignment, that enums have the expected members, and that
all types are importable from the package root.

No analysis logic, no filesystem access, no parser invocation.
"""

import dataclasses
import pytest

from codebase_analyzer import (
    AnalysisConfig,
    AnalysisResult,
    ClassDef,
    Finding,
    FindingKind,
    FunctionDef,
    ImportRef,
    LayerRule,
    Location,
    Module,
    Severity,
)


# ---------------------------------------------------------------------------
# Helpers — minimal valid instances for use across tests
# ---------------------------------------------------------------------------


def make_function_def() -> FunctionDef:
    return FunctionDef(name="my_func", line_number=10)


def make_class_def() -> ClassDef:
    return ClassDef(name="MyClass", line_number=5, methods=[make_function_def()])


def make_import_ref() -> ImportRef:
    return ImportRef(
        source_module="myapp.services",
        target_module="myapp.models",
        line_number=3,
    )


def make_module() -> Module:
    return Module(
        path="myapp/services.py",
        qualified_name="myapp.services",
        classes=[make_class_def()],
        functions=[make_function_def()],
        imports=[make_import_ref()],
    )


def make_location() -> Location:
    return Location(module="myapp.services", line=3)


def make_finding() -> Finding:
    return Finding(
        kind=FindingKind.IMPORT_CYCLE,
        severity=Severity.ERROR,
        message="Circular import: myapp.a → myapp.b → myapp.a",
        location=make_location(),
    )


def make_layer_rule() -> LayerRule:
    return LayerRule(name="models", prefixes=["myapp.models"])


def make_analysis_config() -> AnalysisConfig:
    return AnalysisConfig(layer_rules=[make_layer_rule()])


def make_analysis_result() -> AnalysisResult:
    return AnalysisResult(
        project_root="/path/to/project",
        modules=[make_module()],
        findings=[make_finding()],
    )


# ---------------------------------------------------------------------------
# Construction tests
# ---------------------------------------------------------------------------


class TestConstruction:
    """All model types can be constructed with valid arguments."""

    def test_function_def(self) -> None:
        fd = make_function_def()
        assert fd.name == "my_func"
        assert fd.line_number == 10

    def test_class_def(self) -> None:
        cd = make_class_def()
        assert cd.name == "MyClass"
        assert cd.line_number == 5
        assert len(cd.methods) == 1
        assert cd.methods[0].name == "my_func"

    def test_import_ref(self) -> None:
        ir = make_import_ref()
        assert ir.source_module == "myapp.services"
        assert ir.target_module == "myapp.models"
        assert ir.line_number == 3

    def test_module(self) -> None:
        m = make_module()
        assert m.qualified_name == "myapp.services"
        assert m.path == "myapp/services.py"
        assert len(m.classes) == 1
        assert len(m.functions) == 1
        assert len(m.imports) == 1

    def test_location_with_line(self) -> None:
        loc = Location(module="myapp.a", line=5)
        assert loc.module == "myapp.a"
        assert loc.line == 5

    def test_location_without_line(self) -> None:
        loc = Location(module="myapp.a", line=None)
        assert loc.line is None

    def test_finding_with_location(self) -> None:
        f = make_finding()
        assert f.kind == FindingKind.IMPORT_CYCLE
        assert f.severity == Severity.ERROR
        assert f.location is not None

    def test_finding_without_location(self) -> None:
        f = Finding(
            kind=FindingKind.NAME_COLLISION,
            severity=Severity.WARNING,
            message="Name collision: function 'validate'",
            location=None,
        )
        assert f.location is None

    def test_layer_rule(self) -> None:
        lr = make_layer_rule()
        assert lr.name == "models"
        assert lr.prefixes == ["myapp.models"]

    def test_analysis_config_with_rules(self) -> None:
        config = make_analysis_config()
        assert len(config.layer_rules) == 1

    def test_analysis_config_empty(self) -> None:
        config = AnalysisConfig(layer_rules=[])
        assert config.layer_rules == []

    def test_analysis_result(self) -> None:
        result = make_analysis_result()
        assert result.project_root == "/path/to/project"
        assert len(result.modules) == 1
        assert len(result.findings) == 1


# ---------------------------------------------------------------------------
# Immutability tests
# ---------------------------------------------------------------------------


class TestImmutability:
    """Frozen dataclasses reject field reassignment."""

    def test_function_def_is_frozen(self) -> None:
        fd = make_function_def()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            fd.name = "other"  # type: ignore[misc]

    def test_class_def_is_frozen(self) -> None:
        cd = make_class_def()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            cd.name = "Other"  # type: ignore[misc]

    def test_import_ref_is_frozen(self) -> None:
        ir = make_import_ref()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            ir.target_module = "something_else"  # type: ignore[misc]

    def test_module_is_frozen(self) -> None:
        m = make_module()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            m.qualified_name = "other.module"  # type: ignore[misc]

    def test_finding_is_frozen(self) -> None:
        f = make_finding()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            f.message = "changed"  # type: ignore[misc]

    def test_location_is_frozen(self) -> None:
        loc = make_location()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            loc.line = 999  # type: ignore[misc]

    def test_analysis_result_is_frozen(self) -> None:
        result = make_analysis_result()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            result.project_root = "/other"  # type: ignore[misc]

    def test_analysis_config_is_frozen(self) -> None:
        config = make_analysis_config()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            config.layer_rules = []  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestEnums:
    """Enums contain the expected members."""

    def test_finding_kind_members(self) -> None:
        kinds = {k.value for k in FindingKind}
        assert kinds == {
            "IMPORT_CYCLE", 
            "NAME_COLLISION", 
            "LAYER_VIOLATION", 
            "PARSE_ERROR",
            "ENCAPSULATION_VIOLATION",
            "COMMENTED_CODE",
            "DEAD_CODE",
        }

    def test_severity_members(self) -> None:
        severities = {s.value for s in Severity}
        assert severities == {"ERROR", "WARNING", "INFO"}

    def test_finding_kind_by_name(self) -> None:
        assert FindingKind.IMPORT_CYCLE.value == "IMPORT_CYCLE"
        assert FindingKind.NAME_COLLISION.value == "NAME_COLLISION"
        assert FindingKind.LAYER_VIOLATION.value == "LAYER_VIOLATION"
        assert FindingKind.PARSE_ERROR.value == "PARSE_ERROR"

    def test_severity_ordering_by_name(self) -> None:
        assert Severity.ERROR.value == "ERROR"
        assert Severity.WARNING.value == "WARNING"
        assert Severity.INFO.value == "INFO"


# ---------------------------------------------------------------------------
# Package-root importability test
# ---------------------------------------------------------------------------


class TestPackageImports:
    """All model types are importable from the codebase_analyzer package root."""

    def test_all_types_importable(self) -> None:
        # This test will fail at import time if any symbol is missing from
        # codebase_analyzer/__init__.py — which is the intended behavior.
        import codebase_analyzer

        expected = [
            "AnalysisConfig",
            "AnalysisResult",
            "ClassDef",
            "Finding",
            "FindingKind",
            "FunctionDef",
            "ImportRef",
            "LayerRule",
            "Location",
            "Module",
            "Severity",
        ]
        for name in expected:
            assert hasattr(codebase_analyzer, name), f"Missing from package root: {name}"

    def test_analyze_is_exported(self) -> None:
        # verify that importing analyze works
        import codebase_analyzer
        assert hasattr(codebase_analyzer, "analyze"), "analyze() should be exported"
