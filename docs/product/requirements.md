# AI Codebase Architect — Product Definition and Requirements Baseline

- **Document ID:** PDA-001
- **Version:** 0.2
- **Status:** Draft for discussion
- **Reviewed:** 2026-10-24
- **Lineage:** Existing Codebase Analyzer project

## 1. Status labels

- **Established:** explicitly agreed direction or supported by available evidence.
- **Proposed:** recommended but not final.
- **Open:** requires a decision or more information.
- **Deferred:** intentionally outside the current delivery target.
- **Verified:** confirmed by source inspection and appropriate tests; never inferred from filenames alone.

## 2. Product vision

AI Codebase Architect is a developer tool intended to help users understand software structure, dependencies, architectural relationships, and improvement opportunities. It should provide traceable analysis and eventually optional AI-assisted explanations and recommendations.

The product should evolve from Codebase Analyzer where justified. Reuse, refactoring, replacement, or rebuilding must be decided after assessing actual behavior and suitability.

## 3. Principles

1. Evidence before claims; cite relevant files, symbols, relationships, or other evidence where feasible.
2. Keep deterministic analysis independent of AI.
3. Represent uncertainty explicitly.
4. Default to read-only analysis; make changes reviewable and authorized.
5. Add language and framework support in testable slices.
6. Assess existing components before replacing them.
7. Keep analysis logic reusable across interfaces.
8. Protect source code and secrets; make external AI data transfer clear and configurable.
9. Keep documentation aligned with implemented behavior.
10. Do not claim static analysis guarantees runtime behavior.

## 4. Intended users

Individual developers, beginner/intermediate developers learning architecture, maintainers of unfamiliar or growing codebases, small teams seeking repeatable reports, and developers using AI coding tools. Initial deployment is intended to be local; hosted multi-user operation is deferred.

## 5. Use cases

- **UC-01:** Analyze a project and produce structured results.
- **UC-02:** Explore modules, components, and relationships.
- **UC-03:** Investigate a finding and review its evidence.
- **UC-04:** Understand dependencies and selected architecture relationships.
- **UC-05:** Ask questions answered from project evidence (future).
- **UC-06:** Plan and prioritize improvements.
- **UC-07:** Review proposed changes before application (future).
- **UC-08:** Validate changes with analysis/tests (future).
- **UC-09:** Produce reports and architecture documentation.
- **UC-10:** Configure paths, exclusions, rules, thresholds, and outputs.

## 6. Scope and sequencing

### 6.1 Existing foundation

The existing implementation is Python-focused and has documented parsing, dependency analysis, findings, reporting, and CLI concepts. Exact coverage and reliability remain subject to `docs/existing-system-assessment.md`.

### 6.2 Initial usable release — proposed

Prioritize a reliable CLI and reusable analysis engine over a graphical interface. The initial usable release should:
- Discover supported Python files with predictable exclusions.
- Produce a structured representation of supported constructs.
- Build/report module-import dependencies.
- Run a limited, tested set of architecture and code-quality checks.
- Produce evidence-rich terminal and machine-readable results.
- Support configuration and explain limitations.
- Include focused tests and documentation.
- Keep ordinary analysis read-only.

Whether optional AI explanations belong in the first public release is **Open** and must not block a dependable deterministic release.

### 6.3 Full-stack analysis — agreed direction, staged implementation

Add frontend source analysis incrementally, potentially alongside Python improvements when dependencies permit. Initial focus: selected relationships in Python web applications, especially Flask and Jinja2 where feasible:
- Flask route declarations and handler functions.
- Statically identifiable route-to-template relationships.
- Jinja2 inheritance, include, and import references.
- HTML references to CSS and JavaScript assets.
- Selected JavaScript-to-backend endpoint references where static evidence supports them.
- Cross-resource links with evidence and uncertainty.

These are planned capabilities, not verified current features.

### 6.4 Product GUI — later

A dedicated graphical interface for AI Codebase Architect comes after the analysis foundation and core workflows. A local web dashboard or another UI is possible; technology is **Open**. Keep analysis services reusable so a later UI does not duplicate analysis logic.

### 6.5 Deferred unless requirements change

Universal language support; all frontend frameworks; unrestricted autonomous rewriting; guaranteed dead-code/runtime detection; mandatory cloud operation; enterprise multi-tenancy; mandatory vector database or AI service; IDE replacement/plugin marketplace; history analytics before persistence needs are established.

## 7. Functional requirements

Priorities: **P0** foundation, **P1** important early capability, **P2** later capability, **P3** future/conditional.

| ID | Requirement | Priority | Status |
|---|---|---:|---|
| FR-001 | Discover project files using documented inclusion/exclusion rules. | P0 | Proposed |
| FR-002 | Parse supported Python and report parse failures. | P0 | Proposed |
| FR-003 | Represent modules, symbols, imports, and locations. | P0 | Existing foundation; verify |
| FR-004 | Build module-import dependency graph. | P0 | Existing foundation; verify |
| FR-005 | Keep analysis rules separate from presentation. | P0 | Proposed |
| FR-006 | Report severity, location, explanation, and evidence where available. | P0 | Existing foundation; verify |
| FR-007 | Provide terminal output. | P0 | Existing foundation; verify |
| FR-008 | Provide documented machine-readable output. | P0 | Existing foundation; verify |
| FR-009 | Provide predictable CLI help and errors. | P0 | Verify |
| FR-010 | Support configuration for applicable rules and thresholds. | P1 | Existing foundation; verify |
| FR-011 | Detect circular imports with tests. | P0 | Existing foundation; verify |
| FR-012 | Check configured architectural layer rules. | P1 | Existing foundation; verify |
| FR-013 | Detect selected naming/encapsulation issues with evidence. | P1 | Existing foundation; verify |
| FR-014 | Distinguish heuristics from certainty and document limitations. | P0 | Proposed |
| FR-015 | Provide a component/project inventory. | P1 | Proposed |
| FR-016 | Generate dependency/architecture diagrams where supported. | P1 | Existing foundation; verify |
| FR-017 | Let users investigate finding evidence. | P1 | Proposed |
| FR-018 | Support generic Python without requiring Flask. | P0 | Proposed |
| FR-019 | Detect selected Flask route/handler relationships. | P1 | Planned |
| FR-020 | Detect selected route-to-Jinja2-template relationships. | P1 | Planned |
| FR-021 | Detect Jinja2 inheritance/include/import relationships. | P1 | Planned |
| FR-022 | Detect HTML references to CSS/JS resources. | P1 | Planned |
| FR-023 | Represent selected cross-resource relationships in a shared model. | P1 | Planned |
| FR-024 | Preserve evidence and uncertainty for relationships. | P1 | Proposed |
| FR-025 | Answer project questions from retrieved evidence. | P2 | Planned; provider open |
| FR-026 | Distinguish AI interpretation from deterministic facts. | P2 | Proposed |
| FR-027 | Recommend improvements with rationale, risks, and evidence. | P2 | Planned |
| FR-028 | Propose changes without automatically applying them. | P2 | Planned |
| FR-029 | Require explicit authorization before modifications. | P2 | Proposed safety requirement |
| FR-030 | Validate applied changes with analysis/tests where possible. | P2 | Planned |
| FR-031 | Produce traceable reports and architecture documentation. | P1 | Proposed |
| FR-032 | Support history/comparison after persistence requirements are defined. | P3 | Deferred |
| FR-033 | Keep analysis reusable by future interfaces. | P0 | Proposed |
| FR-034 | Provide a dedicated graphical interface. | P3 | Deferred |
| FR-035 | Add other language analyzers after evaluation. | P3 | Deferred |
| FR-036 | Safely exclude generated, vendored, and irrelevant paths. | P0 | Proposed |
| FR-037 | Report unreadable, malformed, and unsupported files. | P0 | Proposed |
| FR-038 | Document Python API stability if it remains public. | P1 | Open |
| FR-039 | Keep destructive fixer behavior separate from read-only analysis and make it reviewable. | P0 | Fixer needs safety review |
| FR-040 | Record tool/config metadata sufficient to explain a report. | P1 | Proposed |

## 8. Non-functional requirements

| ID | Requirement | Initial direction | Status |
|---|---|---|---|
| NFR-001 | Evidence accuracy | Findings identify rule and available evidence. | Proposed |
| NFR-002 | Repeatability | Same inputs/config/version yield materially consistent deterministic results. | Proposed |
| NFR-003 | Robustness | Parse failures are reported without unexplained total failure. | Proposed |
| NFR-004 | Safe defaults | Analysis is read-only. | Proposed |
| NFR-005 | Performance | Benchmark before setting release target. | Open |
| NFR-006 | Resource use | Measure runtime and memory on representative projects. | Proposed |
| NFR-007 | Security | Do not execute analyzed code by default. | Proposed |
| NFR-008 | Privacy | Disclose/configure external AI data transfer. | Proposed |
| NFR-009 | Secret handling | Avoid logging secrets; treat source as untrusted. | Proposed |
| NFR-010 | AI safety | Keep suggestions reviewable and separate from verified facts. | Proposed |
| NFR-011 | Modularity | New analyzers should not require rewriting CLI/unrelated engines. | Proposed |
| NFR-012 | Extensibility | Add abstractions when justified by requirements. | Proposed |
| NFR-013 | Testability | Focused unit and end-to-end tests for supported behavior. | Proposed |
| NFR-014 | Documentation | Docs match actual behavior and limitations. | Proposed |
| NFR-015 | Usability | Actionable findings/errors for intended users. | Proposed |
| NFR-016 | Output stability | Document schemas and consider compatibility. | Proposed |
| NFR-017 | Portability | Declare supported OS/Python versions after verification. | Open |
| NFR-018 | Accessibility | Define for GUI if approved. | Deferred |
| NFR-019 | Maintainability | Cohesive modules; avoid speculative abstractions. | Proposed |
| NFR-020 | Diagnostics | Explain skipped files/errors without leaking secrets. | Proposed |

A previous draft mentioned 60 seconds for a cold analysis of around 10,000 files. **That is not adopted as a requirement** until reference hardware, memory, included work, and representative fixtures are defined.

## 9. Acceptance criteria examples

- **AC-001:** A syntax error is reported while valid files are still analyzed where feasible.
- **AC-002:** A known import-cycle fixture produces the expected cycle finding.
- **AC-003:** A configured layer violation is reported with source evidence.
- **AC-004:** Deterministic analysis is repeatable for the same inputs, configuration, and version.
- **AC-005:** Ordinary analysis does not modify project files.
- **AC-006:** Dynamic frontend references are marked unresolved/uncertain rather than guessed.
- **AC-007:** AI explanations distinguish evidence from inference and never claim an unapplied change was made.

Convert these into tests as the relevant features are implemented.

## 10. Open decisions

1. AI provider: external API, local model, both, or optional provider interface.
2. Persistence: what must survive between runs; whether report files suffice initially.
3. GUI technology: CLI-first initially; future UI remains open.
4. Change application, backup, and rollback policy.
5. Supported operating systems and Python versions.
6. Whether the public Python API is a stable contract.
7. Release/performance targets after baseline measurements.
8. Exact first subset of Flask/Jinja2/frontend relationships.

## 11. Data and persistence

Do not design a database schema yet. First determine what must be retained and for how long: reports, configuration snapshots, tool versions, project identifiers, and comparisons. In-memory results and user-requested report files may be sufficient initially. A database is not required merely because the application has structured data.

## 12. Related documents

See `README.md`, `docs/roadmap.md`, `docs/existing-system-assessment.md`, `docs/architecture.md`, `docs/architecture/target-architecture.md`, `docs/security-privacy.md`, `docs/testing-strategy.md`, `docs/traceability.md`, and `docs/adr/`.
