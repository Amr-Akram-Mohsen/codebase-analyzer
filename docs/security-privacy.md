# Security and Privacy Considerations

**Status:** Initial planning checklist; not a completed security audit.

## Principles

1. Treat repository contents as untrusted input.
2. Read-only analysis is the default.
3. Do not execute analyzed project code by default.
4. Never commit API keys, credentials, tokens, private test data, or user repositories.
5. Do not send project content to external AI without clear disclosure and suitable user control.
6. Separate AI interpretation from deterministic findings.
7. Require explicit authorization for project changes.
8. Make destructive behavior visible, reviewable, and testable.

## Threats to assess

- Malformed source causing crashes or excessive resource use.
- Repository text attempting to manipulate AI prompts.
- Secrets/source code leaking through logs, reports, crash traces, or AI requests.
- Unsafe fixer operations deleting or corrupting files.
- Unsafe path handling in future file operations.
- Dependency/supply-chain risks.
- Sensitive excerpts in exported reports.
- Unsafe command execution in future integrations.

## Safeguards to plan

- Bound file sizes and handle parse errors.
- Use explicit inclusion/exclusion rules.
- Avoid executing repository code during static analysis.
- Avoid logging secrets.
- Treat repository text as data, not instructions, when preparing AI context.
- Provide clear controls for external AI use.
- Preview edits and require confirmation.
- Provide backups or a rollback approach for destructive changes.
- Avoid telemetry by default unless explicitly designed and disclosed.
- Document report contents and storage locations.

## Open decisions

AI provider/local inference; source-snippet retention; secret storage; report redaction; sandboxing for any future command-running feature.

This document identifies design work; it does not certify the product as secure.
