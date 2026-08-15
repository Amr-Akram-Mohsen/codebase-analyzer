# codebase-analyzer

A developer tool and Python package for analyzing Python codebases.

## What it does

- Discovers all Python source files in a project
- Extracts modules, classes, functions, and imports
- Builds a dependency graph and detects circular imports
- Detects name collisions across modules
- Detects architectural layer violations (given a configuration)
- Reports findings in human-readable terminal output or machine-readable JSON

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Analyze a project directory
codebase-analyzer /path/to/project

# Output as JSON
codebase-analyzer --format json /path/to/project

# Use a specific config file
codebase-analyzer --config /path/to/codebase-analyzer.toml /path/to/project
```

## Python API

```python
from codebase_analyzer import analyze, AnalysisConfig

result = analyze("/path/to/project", AnalysisConfig(layer_rules=[]))
for finding in result.findings:
    print(finding.severity.name, finding.message)
```

## Status

Early development — v0.1.
