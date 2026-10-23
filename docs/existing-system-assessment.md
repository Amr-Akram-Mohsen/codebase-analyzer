# Existing-System Assessment — Codebase Analyzer

**Status:** Preliminary; verification required. This is not a completed audit.

## 1. Purpose

Understand the existing Codebase Analyzer before deciding what to retain, improve, refactor, replace, or defer. The intended product is AI Codebase Architect; a rewrite is not assumed.

## 2. Reported structure

```text
src/codebase_analyzer/
├── cli/main.py
├── core/analyzer.py
├── core/model.py
├── python/discovery.py
├── python/parser.py
├── analysis/
│   ├── dependencies.py
│   ├── cycles.py
│   ├── layers.py
│   ├── encapsulation.py
│   ├── naming.py
│   ├── dead_code.py
│   ├── comments.py
│   └── metrics.py
├── fixer/safe_fixer.py
└── reporting/
    ├── terminal.py
    ├── json_reporter.py
    └── mermaid.py
```

The previously shared overview reports `tests/fixtures`, `tests/unit`, and `tests/integration`. Confirm the current tree before treating this inventory as authoritative.

## 3. Preliminary capability inventory

| Capability | Preliminary status | Evidence / next verification |
|---|---|---|
| Python file discovery | Reported implemented | `python/discovery.py`; test exclusions, unreadable paths, symlinks. |
| Python AST parsing | Reported implemented | `python/parser.py`; test syntax errors, nested symbols, decorators, locations. |
| Structured model | Reported implemented | `core/model.py`; verify invariants and future relationship needs. |
| Import dependency graph | Reported implemented | `analysis/dependencies.py`; test relative imports, packages, unresolved imports. |
| Cycle detection | Reported implemented | `analysis/cycles.py`; test cycle and package initializer cases. |
| Layer rules | Reported implemented | `analysis/layers.py`; test config semantics and false positives. |
| Encapsulation checks | Reported implemented | `analysis/encapsulation.py`; review public API/dynamic references. |
| Naming collisions | Reported implemented | `analysis/naming.py`; test scope and exported symbols. |
| Dead-code heuristics | Reported implemented | `analysis/dead_code.py`; high priority: runtime entry points, decorators, templates, dynamic references. |
| Complexity/metrics | Reported implemented | `analysis/metrics.py`; verify definitions and edge cases. |
| Terminal/JSON/Mermaid reporting | Reported implemented | `reporting/`; verify correctness, escaping, and output schema. |
| Fixer | Reported implemented | `fixer/safe_fixer.py`; review every transformation and deletion path. |
| CLI/configuration | Partially documented | `cli/main.py`; verify `--help`, argument parsing, `fix`/`graph`, malformed config. |
| Flask-specific analysis | Not established | Search for route and handler analysis plus tests. |
| Jinja2 relationships | Not established | Search for inheritance/include/import analysis and fixtures. |
| HTML/CSS/JavaScript analysis | Not established | Original scope was Python-focused; confirm no partial support exists. |
| AI Q&A/recommendations | Not established; planned | Do not assume implementation. |
| GUI/history/database | Deferred/open | Original architecture excluded these; revisit only when requirements justify them. |

## 4. Questions raised by limited source inspection

These are questions to verify, not confirmed defects:
- Are class methods also included in the module-level function collection?
- Do nested functions lose their scope in the model?
- Does name/reference extraction preserve enough context for dead-symbol analysis?
- Does `__main__` detection verify the full comparison?
- Does qualified-name generation assume a `src/` layout?
- Does import resolution correctly handle relative imports and package initializers?
- Can CLI parsing accept a path-only invocation before compatibility handling?
- Are fixer operations safe, previewable, and appropriately authorized?

Record confirmed issues with tests or reproducible examples before changing code.

## 5. Bounded verification procedure

1. Confirm current tree and package metadata.
2. Run existing tests and record exact command/result.
3. Check CLI `--help` and analyze a small fixture.
4. Inspect representative code for each major capability.
5. Test potentially destructive fixer paths in temporary fixtures.
6. Use Nexora as a validation sample; inspect each reported finding before classifying it as a true defect.
7. Update this document with source/test evidence.

## 6. Decision categories

For each subsystem, recommend:
- **Retain** — suitable as-is.
- **Improve** — keep design, fix specific limitations.
- **Refactor** — behavior is useful but boundaries need work.
- **Replace** — evidence shows it is unsuitable or too costly to repair.
- **Defer** — not needed for the next release.

Do not recommend a full rewrite without concrete evidence.
