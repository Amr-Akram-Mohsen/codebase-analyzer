# codebase-analyzer — Architecture

## Purpose and non-goals

This tool analyzes Python codebases and reports structural and architectural findings: module
structure, import dependencies, circular imports, name collisions, and layer violations.

It is not a linter, type checker, style enforcer, or semantic code analysis tool. It does not
execute code. It does not integrate with version control, databases, web services, or AI systems.

**Explicitly excluded from v0.1:**
- Web frontend or backend
- Database of any kind
- AI or LLM integration
- VS Code or editor extension
- JavaScript or Java language support
- GitHub / VCS integration
- Historical / trend analysis
- Plugin or extension system
- PyPI publishing infrastructure
- Content-based or semantic code duplication detection
- Abstract language parser interface

---

## System overview

The system is a pipeline. Python source files enter at the top; structured findings emerge at the
bottom. Each stage has one responsibility and is not aware of what comes before or after it.

```
Files on disk
    │
    ▼  python/discovery.py     — locate .py files
    │
    ▼  python/parser.py        — ast → IR (language boundary)
    │
    ▼  core/model.py           — IR and output types (shared foundation)
    │
    ▼  analysis/*              — engines: IR in, Findings out
    │
    ▼  core/analyzer.py        — orchestrator: sequences the pipeline
    │
    ▼  reporting/*             — formatters: AnalysisResult → string or dict
    │
    ▼  cli/main.py             — entry point: args, config, exit codes
```

---

## Dependency direction rules

The following direction is strictly enforced and must not be violated:

```
cli/
  └─► core/analyzer.py
        ├─► python/             (IR production — only Python-specific code)
        ├─► core/model.py       (IR and output types)
        ├─► analysis/           (engines: consume IR, produce Findings)
        └─► reporting/          (formatters: consume AnalysisResult)

analysis/*  ──► core/model.py  (only)
reporting/* ──► core/model.py  (only)
python/*    ──► core/model.py  + stdlib ast
core/model.py ──► nothing
```

### Forbidden dependencies (explicit violations)

| Rule | Rationale |
|------|-----------|
| `analysis/*` must NOT import `python/*` | Analysis must remain language-neutral |
| `analysis/*` must NOT import `cli/*` | Analysis must not know about the CLI |
| `analysis/*` must NOT import `reporting/*` | Analysis produces findings, not output |
| `analysis/*` must NOT import each other | Engines are independent; orchestrator coordinates |
| `reporting/*` must NOT import `analysis/*` | Reporters consume results, do not re-run analysis |
| `reporting/*` must NOT import `python/*` | Reporters are language-neutral |
| `reporting/*` must NOT import `cli/*` | Reporters are not CLI-aware |
| `python/*` must NOT import `analysis/*` | Parser produces IR, does not analyze it |
| `core/model.py` must NOT import anything outside stdlib | It is the foundation |
| `core/analyzer.py` must NOT import `cli/*` | Orchestration must not depend on its driver |
| `core/analyzer.py` must NOT import `reporting/*` | Orchestration returns a result; it does not format it |

---

## Component reference

### `python/discovery.py`
Walks a directory tree and returns paths of all `.py` files to be analyzed. Skips:
`.git`, `__pycache__`, `.venv`, `venv`, `env`, `node_modules`.
Must NOT do any parsing or analysis.

### `python/parser.py`
Reads a `.py` file, invokes `ast.parse()`, walks the AST, and translates the result into
`core.model` IR objects. This is the language boundary — AST objects are discarded here.
Must NOT do any analysis, produce findings about violations, or touch file discovery.

### `core/model.py`
Defines all shared data objects: the language-neutral IR, the analysis output types, and
analysis configuration. Contains only dataclass/enum definitions. No logic. No I/O.

### `core/analyzer.py`
Sequences the pipeline: discover → parse → build dependency graph → run analysis engines →
collect findings → return `AnalysisResult`. Its role is coordination, not judgment. Any
`if` statement that makes an analytical decision about findings belongs in an engine instead.

### `analysis/dependencies.py`
Given `list[Module]`, constructs a `dict[str, set[str]]` dependency graph. Includes only
project-internal import edges (target module is a known module in the project).

### `analysis/cycles.py`
Given a dependency graph, detects circular import chains (SCCs of size > 1). Returns
`list[Finding]` with `kind=IMPORT_CYCLE`.

### `analysis/naming.py`
Detects top-level name collisions across modules: same class name or same function name
appearing in more than one module. Does NOT detect method-level collisions. Returns
`list[Finding]` with `kind=NAME_COLLISION`. Finding messages must make clear this is a
name collision, not necessarily code duplication.

### `analysis/layers.py`
Given a dependency graph and `list[LayerRule]`, detects architectural layer violations using
prefix matching. Modules not matching any layer are silently ignored. Returns
`list[Finding]` with `kind=LAYER_VIOLATION`.

### `reporting/terminal.py`
Accepts `AnalysisResult` and `use_color: bool`, returns a formatted `str` for terminal
output. Does not write to any stream.

### `reporting/json_reporter.py`
Accepts `AnalysisResult`, returns a JSON-serializable `dict`. Does not write to any stream.
The CLI serializes and writes.

### `cli/main.py`
Parses arguments, loads configuration, calls `analyze()`, selects reporter, routes output,
sets exit code. Contains no analysis logic.

---

## Language boundary

The `python/` package is the sole owner of all Python-specific knowledge:
- `.py` file extension
- `ast` node types
- Python import semantics (relative imports, `__init__.py` as package markers)
- Package root detection

After `python/parser.py` translates source into IR objects, Python AST objects are discarded.
Nothing past this boundary ever imports `ast`.

### Import boundary: project-internal vs external imports

The parser records an `ImportRef` for **every** import statement encountered, regardless of
whether the target is internal or external (stdlib, third-party, or unresolvable).

`analysis/dependencies.py` filters to project-internal imports when constructing the dependency
graph. An import edge is internal if and only if `ImportRef.target_module` matches the
`qualified_name` of any `Module` in the parsed result.

This means:
- Dependency analysis, cycle detection, and layer checking operate only on project-internal edges
- External library names do not become nodes in the dependency graph
- External imports remain in `Module.imports` but are excluded from graph-based analyses

### Adding a second language (future)

When a second language is added:
1. Create a new sibling package (e.g., `javascript/`)
2. Implement discovery and parsing that produces the same `core.model` IR types
3. Extract a shared interface only if empirically justified
4. `core/analyzer.py` would need a small dispatch mechanism — not a plugin system

No `LanguageParser` ABC is created in v0.1.

---

## Domain model

All types live in `core/model.py`. All are plain data objects (`@dataclass(frozen=True)`).
No methods that compute things. No logic.

### IR types (source representation)

```
Module
  path: str                    # filesystem path relative to project root
  qualified_name: str          # e.g. "myproject.utils.helpers"
  classes: list[ClassDef]
  functions: list[FunctionDef] # top-level functions only
  imports: list[ImportRef]     # all imports, internal and external

ClassDef
  name: str
  line_number: int
  methods: list[FunctionDef]

FunctionDef
  name: str
  line_number: int

ImportRef
  source_module: str           # qualified name of the importing module
  target_module: str           # qualified name of what is imported (resolved)
  line_number: int
```

Note: `ImportRef.is_relative` is omitted. The parser resolves relative imports to absolute
qualified names before constructing IR. The `is_relative` flag is a parser-internal concern.

### Analysis output types

```
AnalysisResult
  project_root: str            # absolute path of the analyzed directory
  modules: list[Module]        # successfully parsed modules only
  findings: list[Finding]      # all findings from all engines + parser

Finding
  kind: FindingKind
  severity: Severity
  message: str
  location: Location | None

Location
  module: str                  # qualified module name
  line: int | None

FindingKind (enum)
  IMPORT_CYCLE
  NAME_COLLISION
  LAYER_VIOLATION
  PARSE_ERROR

Severity (enum)
  ERROR
  WARNING
  INFO

AnalysisConfig
  layer_rules: list[LayerRule] # empty list = layer analysis disabled
  # Contains ONLY fields that change analysis behavior.
  # Must NOT contain: output format, output path, config-file path,
  # CLI arguments, color settings, verbosity, or target project path.

LayerRule
  name: str
  prefixes: list[str]
```

---

## Public API

Re-exported from `codebase_analyzer/__init__.py`:

| Symbol | Status |
|--------|--------|
| `analyze()` | Primary public API — added in Phase 5 |
| `AnalysisResult` | Primary public API |
| `Finding` | Primary public API |
| `FindingKind` | Primary public API |
| `Severity` | Primary public API |
| `Location` | Primary public API |
| `AnalysisConfig` | Primary public API |
| `LayerRule` | Primary public API |
| `Module` | Accessible (in `AnalysisResult.modules`), not advertised as stable |
| `ClassDef` | Accessible (in `Module.classes`), not advertised as stable |
| `FunctionDef` | Accessible (in `Module.functions`, `ClassDef.methods`), not advertised as stable |
| `ImportRef` | Accessible (in `Module.imports`), not advertised as stable |

The IR types (`Module`, `ClassDef`, `FunctionDef`, `ImportRef`) are not hidden, but their
field set may grow as the parser extracts more information.

---

## Analysis engines

### Dependency graph

- **Type**: `dict[str, set[str]]` — maps module qualified name to the set it imports
- **Constructed by**: `analysis/dependencies.py`
- **Consumed by**: `analysis/cycles.py` and `analysis/layers.py`
- **Not part of public API** — intermediate computation, discarded after analysis

### Cycle detection

- Input: `dict[str, set[str]]` (dependency graph)
- Output: `list[Finding]` with `kind=IMPORT_CYCLE`, `severity=ERROR`
- Algorithm: Tarjan's SCC or equivalent, stdlib only
- One finding per cycle, listing all modules in the cycle

### Name-collision detection

- Input: `list[Module]`
- Output: `list[Finding]` with `kind=NAME_COLLISION`, `severity=WARNING`
- Detects: same top-level class name or function name in more than one module
- Does NOT detect: method collisions, content duplication, semantic similarity
- Finding messages must explicitly state this is a **name collision**, not code duplication

### Layer violation detection

- Input: `dict[str, set[str]]` (dependency graph), `list[LayerRule]`
- Output: `list[Finding]` with `kind=LAYER_VIOLATION`, `severity=ERROR`
- Layer assignment: prefix matching on `qualified_name`
- Valid direction: module in layer N imports from layer M where M ≤ N
- Violation: module in lower-index layer imports from higher-index layer
- Modules matching no layer: silently ignored

**Layer configuration format** (`codebase-analyzer.toml`):
```toml
[[layers]]
name = "models"
prefixes = ["myapp.models"]

[[layers]]
name = "services"
prefixes = ["myapp.services"]

[[layers]]
name = "api"
prefixes = ["myapp.api"]
```

---

## Error handling

**Category A — User/input errors**: Wrong arguments, invalid path, malformed config.
- Owner: CLI
- Behavior: print error to stderr, exit 2

**Category B — Analyzable source problems**: Syntax errors or unreadable files in analyzed code.
- Owner: Parser
- Behavior: emit `PARSE_ERROR` finding, continue analysis; file excluded from dependency analysis

**Category C — Internal tool errors**: Unexpected exceptions (bugs in the tool).
- Owner: CLI top-level handler
- Behavior: print minimal error to stderr, exit 2

---

## Configuration

`AnalysisConfig` accepts only fields that change analysis behavior:
- `layer_rules: list[LayerRule]` — empty list disables layer analysis

Three-way distinction:
| Concern | Owner |
|---------|-------|
| Analysis behavior (layer rules) | `AnalysisConfig` |
| CLI behavior (format, output file, config path, target path) | CLI-local variables |
| Reporter behavior (color, verbosity) | Passed as arguments to reporters |

---

## JSON output schema

Every JSON output includes `"schema_version": "0.1"`. Schema changes that remove or rename
fields require incrementing this version. Adding new optional fields is not a breaking change.

```json
{
  "schema_version": "0.1",
  "analyzed_path": "/absolute/path",
  "summary": {
    "modules": 12,
    "classes": 34,
    "functions": 89,
    "findings": { "error": 2, "warning": 5, "info": 0 }
  },
  "modules": [
    {
      "path": "myapp/models.py",
      "qualified_name": "myapp.models",
      "classes": [{ "name": "User", "line": 10 }],
      "functions": [{ "name": "get_user", "line": 45 }]
    }
  ],
  "findings": [
    {
      "kind": "IMPORT_CYCLE",
      "severity": "ERROR",
      "message": "Circular import: myapp.a → myapp.b → myapp.a",
      "location": { "module": "myapp.a", "line": 3 }
    }
  ]
}
```

---

## Testing approach

**Unit tests** (`tests/unit/`): No filesystem, no parser. Analysis engines are tested against
hand-crafted IR objects. Fast, isolated.

**Integration tests** (`tests/integration/`): Parser + analysis integration. Tests use in-memory
source strings or temporary files — not the fixture projects.

**Fixture projects** (`tests/fixtures/`): Minimal hand-crafted Python projects for end-to-end
pipeline tests via `analyze()`.

| Fixture | Purpose |
|---------|---------|
| `simple_project/` | Clean project — zero findings expected |
| `cyclic_project/` | Known A→B→A cycle — one `IMPORT_CYCLE` finding expected |
| `named_collision_project/` | Same function name in two modules — one `NAME_COLLISION` warning |
| `layered_project/` | Layer config + known violation — one `LAYER_VIOLATION` finding |

---

## Development conventions

### Docstrings
- Module: brief statement of responsibility and what the module does not do
- Class: what it represents, primary responsibility, important invariants
- Function: what it does, important constraints, return value if non-obvious
- Proportional to complexity — a one-line docstring is often correct
- Do not document obvious code or repeat implementation in prose

### Type annotations
- All functions and methods must have type annotations
- Use `X | None` (not `Optional[X]`)
- Use `list[X]`, `dict[K, V]` (not `List`, `Dict`)
- Do not use `Any` without a concrete, documented reason

### Code quality
- Explicit types; clear names; small focused functions; single responsibilities
- Frozen dataclasses for IR types; `list[X]` for collection fields
- Standard-library solutions when sufficient
- No `utils/`, `helpers/`, or generic dumping ground modules
- No speculative extension points or premature abstractions

---

## IR validation status

- [x] Phase 2: parser implemented
- [x] Phase 3: IR validated against real parser output

*(Updated after Phase 3 gate. The IR proved sufficient for the planned analysis engines without further modification).*

---

## Change policy

**Adding a field to `core/model.py`**: Requires a concrete justification from an analysis engine
that needs the field. Justify by identifying which analysis requires it and whether it is
expressible in a language-neutral way.

**New analysis engine**: Warrants a new file in `analysis/` if it has an independent algorithm
and independent test suite. Should not be merged into an existing engine unless responsibilities
genuinely overlap.

**Dependency rule exception**: Requires explicit architectural justification and documentation
here. The default answer is no.
