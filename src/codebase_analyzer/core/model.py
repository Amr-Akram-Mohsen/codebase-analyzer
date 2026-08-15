"""
Shared data contracts for codebase-analyzer.

Defines two groups of types:
  - IR types (source representation): Module, ClassDef, FunctionDef, ImportRef
  - Analysis output types: Finding, FindingKind, Severity, Location,
    AnalysisResult, AnalysisConfig, LayerRule

All types are plain frozen dataclasses or enums. No logic. No I/O.
This file must not import anything outside the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FindingKind(Enum):
    """Classification of an analysis finding."""

    IMPORT_CYCLE = "IMPORT_CYCLE"
    NAME_COLLISION = "NAME_COLLISION"
    LAYER_VIOLATION = "LAYER_VIOLATION"
    ENCAPSULATION_VIOLATION = "ENCAPSULATION_VIOLATION"
    COMMENTED_CODE = "COMMENTED_CODE"
    DEAD_CODE = "DEAD_CODE"
    PARSE_ERROR = "PARSE_ERROR"


class Severity(Enum):
    """Severity level of a finding."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


# ---------------------------------------------------------------------------
# Group A — IR (Source Representation)
#
# These types represent what was extracted from source files.
# They are produced by python/parser.py and consumed by the analysis engines.
# They may grow as the parser extracts more information or new analyses
# require additional source data.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FunctionDef:
    """A function or method definition extracted from source."""

    name: str
    line_number: int
    end_line_number: int | None = None


@dataclass(frozen=True)
class ClassDef:
    """A class definition extracted from source."""

    name: str
    line_number: int
    methods: list[FunctionDef]
    end_line_number: int | None = None


@dataclass(frozen=True)
class ImportRef:
    """
    A single import statement extracted from source.

    Both project-internal and external imports are recorded.
    Filtering to project-internal edges is the responsibility of
    analysis/dependencies.py, not the parser.

    target_module is always a fully qualified dotted name. Relative imports
    are resolved to absolute names by the parser before constructing this object.
    """

    source_module: str
    target_module: str
    line_number: int


@dataclass(frozen=True)
class Module:
    """
    Language-neutral representation of a single source file.

    Produced by the Python parser after AST translation. All downstream
    analysis stages operate on this type; none of them import `ast`.

    `modules` contains only successfully parsed modules — files with syntax
    errors appear in AnalysisResult.findings as PARSE_ERROR findings instead.
    """

    path: str
    qualified_name: str
    classes: list[ClassDef]
    functions: list[FunctionDef]
    imports: list[ImportRef]


# ---------------------------------------------------------------------------
# Group B — Analysis Output and Configuration
#
# These types represent what the analysis layer produces and what it accepts
# as input. They change when new analyses are added or the output contract
# evolves.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Location:
    """Points to a specific module and optional line number in a finding."""

    module: str
    line: int | None
    end_line: int | None = None


@dataclass(frozen=True)
class Finding:
    """
    A single analysis finding produced by an analysis engine or the parser.

    All engines return list[Finding]. Reporters consume Finding objects
    without knowing which engine produced them.
    """

    kind: FindingKind
    severity: Severity
    message: str
    location: Location | None


@dataclass(frozen=True)
class AnalysisResult:
    """
    The value returned from analyze().

    modules: successfully parsed modules only. Files with syntax errors
    are excluded here and represented as PARSE_ERROR findings instead.
    findings: all findings from the parser and all analysis engines.
    """

    project_root: str
    modules: list[Module]
    findings: list[Finding]


@dataclass(frozen=True)
class LayerRule:
    """
    A single layer in an architectural layer configuration.

    A module is assigned to this layer if its qualified_name starts with
    any of the strings in prefixes. Layer order is significant: lower-index
    layers may not import from higher-index layers.
    """

    name: str
    prefixes: list[str]


@dataclass(frozen=True)
class AnalysisConfig:
    """
    Configuration that controls analysis behavior.

    Contains only fields that change what the analysis pipeline does.
    Must NOT contain: output format, output path, config-file path, CLI
    arguments, color settings, verbosity, or the target project path.
    Those concerns belong to the CLI and reporters respectively.

    layer_rules: ordered list of layer definitions. Empty list disables
    layer analysis entirely.
    """

    layer_rules: list[LayerRule]
    encapsulation_boundaries: list[str] = field(default_factory=list)
    encapsulation_public_apis: dict[str, list[str]] = field(default_factory=dict)
    dead_code_entry_points: list[str] = field(default_factory=list)
