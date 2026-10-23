# Requirements Traceability

**Status:** Starter template.

Connect requirements to design elements and verification evidence. Do not mark a requirement complete merely because a related source file exists.

| Requirement | Design/component | Verification evidence | Status |
|---|---|---|---|
| FR-001 — Project discovery | Python discovery | Inclusion/exclusion and unreadable-path tests | To verify |
| FR-002 — Python parsing | Python parser/shared model | Parser fixtures, including syntax errors | To verify |
| FR-004 — Dependency graph | Dependency analysis | Import-resolution and graph tests | To verify |
| FR-006 — Evidence-rich findings | Finding model/reporters | Rule tests and report assertions | To verify |
| FR-008 — JSON output | JSON reporter | Schema and serialization tests | To verify |
| FR-011 — Circular imports | Cycle analysis | Known-cycle/no-cycle fixtures | To verify |
| FR-019 — Flask route relationships | Flask analyzer | Route fixture tests | Planned |
| FR-020 — Route-to-template links | Flask/Jinja2 analysis | Static and ambiguous-reference fixtures | Planned |
| FR-021 — Jinja2 relationships | Template analyzer | Inheritance/include/import fixtures | Planned |
| FR-022 — HTML asset references | HTML/resource analyzer | CSS/JS reference fixtures | Planned |
| FR-025 — Evidence-based AI Q&A | AI context/application service | Grounded-answer evaluation set | Planned |
| FR-029 — Authorized modifications | Change workflow | Tests confirming no edits before approval | Planned |

Add rows for active requirements and link to exact test names, code locations, or report artifacts where practical.
