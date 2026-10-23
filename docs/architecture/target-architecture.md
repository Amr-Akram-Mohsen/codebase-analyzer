# Target Architecture — AI Codebase Architect

**Status:** Proposed conceptual architecture; not yet an implementation specification.

## 1. Goals

- Reuse existing Codebase Analyzer components where justified.
- Keep deterministic analysis independent of AI.
- Support generic Python before requiring framework-specific knowledge.
- Add Flask/Jinja2 and selected frontend relationships incrementally.
- Represent findings and relationships with evidence and uncertainty.
- Allow future interfaces to reuse application services.
- Avoid selecting a database, AI provider, or GUI framework before requirements justify it.

## 2. Conceptual layers

```text
CLI (initial interface)                 Future graphical interface
          |                                          |
          +-------------------+----------------------+
                              |
                    Application services
                              |
               Analysis orchestration / queries
                              |
              Shared project and result model
                              |
       +----------------------+-----------------------+
       |                      |                       |
 Generic Python         Flask/Jinja2          Frontend resource
    analysis               analysis              analysis
       |                      |                       |
       +----------------------+-----------------------+
                              |
                Relationship and dependency model
                              |
                   Deterministic analysis rules
                              |
              Findings, evidence, reports, diagrams
                              |
                Optional AI interpretation layer
```

This is conceptual. It does not assert that these components already exist or that every box must become a separate package.

## 3. Responsibilities

- **Project discovery:** identify relevant files, apply explicit exclusions, report unreadable/skipped resources, and never execute project code.
- **Generic Python analyzer:** parse supported syntax and extract modules, symbols, imports, decorators, and useful static facts.
- **Flask-aware analysis:** identify statically recognizable route declarations and handler relationships.
- **Jinja2 analysis:** identify inheritance, includes, imports, and references where statically discoverable.
- **Frontend resource analysis:** identify HTML asset references and selected CSS/JavaScript relationships.
- **Shared project model:** represent files, symbols, components, and typed relationships without premature complexity.
- **Analysis rules:** run deterministic checks; findings identify rule, severity, evidence, and limitations where practical.
- **Application services:** expose reusable operations such as project analysis, finding queries, graph construction, and report export.
- **Reporting:** render terminal and file outputs; future GUI can reuse services rather than duplicate analysis logic.
- **Optional AI services:** use bounded relevant context; separate AI interpretation from deterministic facts.

Framework-specific analyzers should reuse generic Python facts rather than duplicate the entire parser.

## 4. Possible relationship types

- Python module imports Python module.
- Flask route is handled by Python function.
- Flask route renders Jinja2 template.
- Jinja2 template extends/includes/imports another template.
- HTML document references CSS or JavaScript.
- JavaScript may call a backend endpoint when static evidence is sufficient.
- Component depends on another component.

Record evidence for edges where practical. Omit unresolved relationships or mark them uncertain rather than inventing them.

## 5. Persistence

No database is selected. Initially, in-memory results and user-requested report files may suffice. Consider persistence after requirements for history, comparison, sessions, multi-project management, or indexing are defined. If added, define lifecycle, migrations, source-code retention, and deletion behavior first.

## 6. Security and trust boundaries

- Treat repository content as untrusted input, including comments and documentation.
- Do not execute analyzed source code during ordinary analysis.
- Do not send secrets to AI providers.
- Make external AI data transfer explicit and configurable.
- Do not apply edits without explicit authorization.
- Keep destructive operations isolated and testable.
- Avoid unnecessary source-code logging.

See `docs/security-privacy.md`.

## 7. Decisions left open

Persistence technology; AI provider/local-model support; GUI framework and deployment style; public application-service interfaces; plugin mechanism; languages beyond Python and selected web resources.

## 8. Validation

Map current modules and dependencies; identify existing boundaries; prototype a small Flask-to-Jinja2 relationship; test whether the current model represents it cleanly; record lasting decisions in an ADR; revise this proposal after evidence is available.
