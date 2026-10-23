# Testing Strategy

**Status:** Proposed baseline.

## Unit tests

Test isolated algorithms and contracts:
- Parser extraction and locations.
- Import resolution and graph construction.
- Cycle detection and individual rules.
- Configuration validation.
- Report serialization and escaping.
- Fixer transformations in temporary fixtures.

## Integration tests

Test end-to-end workflows:
- Discover and analyze a small project.
- Handle malformed Python.
- Produce terminal and JSON output.
- Load valid/invalid configuration.
- Generate diagrams.
- Exercise supported CLI commands.

## Fixtures

Maintain small fixtures with expected results:
- Clean project.
- Known import cycles.
- Layer-rule violations.
- Relative imports and package initializers.
- Nested functions and class methods.
- Dynamic/ambiguous references that should not be overclaimed.
- Flask routes and Jinja2 relationships when implemented.
- HTML/CSS/JavaScript references when implemented.

## Safety tests

- Ordinary analysis does not modify source files.
- Fixer previews and authorization are tested.
- File deletion is explicit and covered.
- Malformed inputs cannot escape the selected project scope.
- Secrets do not appear in ordinary logs or example reports.

## Regression and evidence

Give confirmed bugs focused regression tests where practical. For significant features, record commands, environment, results, skips, fixture names, and known limitations. Code coverage is a diagnostic aid, not proof of correctness.

## Performance

Do not set a fixed runtime target until a representative benchmark and reference environment are defined. Measure runtime and memory separately from optional AI calls and network latency.
