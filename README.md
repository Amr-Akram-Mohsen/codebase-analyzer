# AI Codebase Architect

**AI Codebase Architect** is the planned evolution of the existing **Codebase Analyzer** project: a developer tool intended to help people understand a software project’s structure, dependencies, architecture, and potential improvement opportunities.

**Status:** Early development. The current implementation is primarily Python-focused; the broader product vision includes selected relationships across Python backend code and web frontend resources, followed by optional AI-assisted explanations and a graphical interface in later stages.

## Current implementation

Based on the existing README and preliminary project overview, the tool is intended to:
- Discover Python source files.
- Extract modules, classes, functions, and imports.
- Build a module-import dependency graph.
- Detect circular imports and selected naming collisions.
- Check configured architectural layer rules.
- Report findings in terminal output and JSON.
- Generate Mermaid diagrams.
- Provide CLI analysis/fix/graph workflows.

These are documented capabilities, not a claim that every behavior is fully verified or correct. See [the existing-system assessment](docs/existing-system-assessment.md).

## Product direction

1. Verify and strengthen the existing Python analysis foundation.
2. Improve finding reliability, evidence, configuration, and reporting.
3. Add selected Flask/Jinja2 and frontend-resource relationships incrementally.
4. Add optional AI explanations grounded in analysis evidence.
5. Consider a dedicated graphical interface after the analysis foundation is reliable.

The project will evolve from Codebase Analyzer where justified; a rewrite is not assumed.

## Installation

From the repository root, the existing README documents:

```bash
pip install -e ".[dev]"
```

This assumes `pyproject.toml` defines the development extra.

## Usage

Confirm the current syntax with the installed command's `--help`. Examples from the existing README:

```bash
codebase-analyzer /path/to/project
codebase-analyzer --format json /path/to/project
codebase-analyzer --config /path/to/codebase-analyzer.toml /path/to/project
```

The project overview also describes `analyze`, `fix`, and `graph` command paths; verify exact syntax before relying on any particular option.

## Python API

The existing README documents:

```python
from codebase_analyzer import analyze, AnalysisConfig

result = analyze("/path/to/project", AnalysisConfig(layer_rules=[]))
for finding in result.findings:
    print(finding.severity.name, finding.message)
```

The public API is early-development and is not yet declared stable.

## Limitations and planned capabilities

Do not assume the current implementation understands Flask routes, Jinja2 inheritance, HTML/CSS/JavaScript relationships, or frontend-to-backend flows. Those are planned capabilities and must be verified and implemented incrementally. AI assistance, persistent analysis history, a dedicated GUI, IDE integrations, and broad multi-language support are not presented as current capabilities.

## Documentation

- [Product requirements](docs/product/requirements.md)
- [Roadmap](docs/roadmap.md)
- [Existing-system assessment](docs/existing-system-assessment.md)
- [Current architecture](docs/architecture.md)
- [Proposed target architecture](docs/architecture/target-architecture.md)
- [Security and privacy](docs/security-privacy.md)
- [Testing strategy](docs/testing-strategy.md)
- [Requirements traceability](docs/traceability.md)
- [Architecture decision records](docs/adr/README.md)

## Project status

This is an evolving project. Treat requirements marked Proposed, Open, or Deferred as non-final. Static-analysis findings are evidence for investigation, not automatic proof of a runtime defect.
