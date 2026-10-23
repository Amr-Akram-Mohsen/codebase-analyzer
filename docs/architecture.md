# Current Architecture — Codebase Analyzer

**Status:** Preliminary description of the existing implementation; verify against the current branch. This is not the target architecture.

## 1. Purpose and scope

The existing project is a Python-focused developer tool/package intended to analyze Python codebases and report selected structural and architectural findings through a command-line workflow.

The existing README describes Python discovery, extraction of modules/classes/functions/imports, dependency graph construction, circular-import and naming-collision detection, configured layer checks, terminal/JSON output, and a Python API. The preliminary overview also lists encapsulation, dead-code heuristics, commented-out code checks, metrics, a fixer, and Mermaid output. Verify these capabilities against current source and tests; see [the existing-system assessment](existing-system-assessment.md).

The original v0.1 design excluded AI, database persistence, a web UI, editor integration, Git/VCS integration, JavaScript/Java analysis, history, plugins, and semantic duplication detection. Those were original scope boundaries, not permanent prohibitions for the future product.

## 2. Reported package structure

```text
src/codebase_analyzer/
├── __init__.py
├── __main__.py
├── cli/main.py
├── core/
│   ├── analyzer.py
│   └── model.py
├── python/
│   ├── discovery.py
│   └── parser.py
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

Confirm this tree against the repository.

## 3. High-level flow

```text
CLI arguments and configuration
              |
              v
       Project discovery
              |
              v
       Python AST parsing
              |
              v
      Structured core model
              |
              v
     Analysis and graph rules
              |
              v
       Analysis result model
              |
              v
 Terminal / JSON / Mermaid output
```

The exact call graph, error boundaries, and responsibilities require confirmation.

## 4. Reported responsibilities

- `cli/`: command-line arguments, configuration loading, command dispatch.
- `python/discovery.py`: locating Python files.
- `python/parser.py`: translating Python AST information into structured model objects.
- `core/model.py`: shared domain types for modules, symbols, findings, configuration, and results.
- `core/analyzer.py`: coordinating discovery, parsing, and analysis engines.
- `analysis/`: dependency graph and individual analysis checks.
- `fixer/`: targeted source transformations; destructive paths need special review.
- `reporting/`: terminal, JSON, and Mermaid output.

These reported responsibilities do not replace verification of imports, call sites, and tests.

## 5. Boundaries and limitations to assess

The original design separates parsing, a shared model, analysis engines, and reporting. How cleanly the current implementation enforces those boundaries—and whether the model can support richer cross-resource relationships—remains to be verified.

Static import graphs do not automatically represent function calls, runtime dispatch, dependency injection, or framework behavior. Dead-code heuristics can miss dynamic and implicit references, especially framework routes and template references. Directory names alone do not prove architectural roles. Static analysis cannot guarantee runtime behavior. Fixer operations require separate safety review.

## 6. Evolution policy

1. Avoid speculative abstractions.
2. Keep deterministic analysis independent from optional AI.
3. Separate presentation from analysis where practical.
4. Add framework/resource relationship types only with explicit semantics and tests.
5. Justify changes to shared model types and add regression tests.
6. Record durable decisions in `docs/adr/`.
7. Update this document when the verified implementation changes.

## 7. Related documents

- [Existing-system assessment](existing-system-assessment.md)
- [Proposed target architecture](architecture/target-architecture.md)
- [Product requirements](product/requirements.md)
- [Roadmap](roadmap.md)
