"""
codebase-analyzer public API.

Primary public API (stable):
    analyze()         — added in Phase 5 (core/analyzer.py)
    AnalysisResult
    AnalysisConfig
    LayerRule
    Finding
    FindingKind
    Severity
    Location

Accessible types (returned by analyze(), not advertised as stable):
    Module, ClassDef, FunctionDef, ImportRef
"""

from codebase_analyzer.core.analyzer import analyze
from codebase_analyzer.core.model import (
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

__all__ = [
    "analyze",
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
