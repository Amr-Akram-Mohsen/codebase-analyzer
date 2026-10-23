# AI Codebase Architect — Development Roadmap

**Status:** Proposed roadmap, not a deadline commitment.

## Principles

- Verify existing behavior before replacing it.
- Keep deterministic analysis useful without AI.
- Deliver testable slices with acceptance criteria.
- Frontend analysis is an agreed direction and may overlap with backend work when dependencies allow.
- A graphical interface for the product itself comes later than the analysis foundation.
- Phase numbers do not require strictly sequential work in every case.

## Stage 0 — Product baseline

Agree on product scope, terminology, requirements, and acceptance criteria. Distinguish current, proposed, open, and deferred capabilities.

**Exit:** Initial release scope is testable and no planned feature is presented as existing.

## Stage 1 — Existing-system verification

Review repository structure, packaging, CLI, core models, parser, analysis engines, reporting, fixer, and tests. Run focused existing tests and safe examples. Classify capabilities as verified, partial, not found, or uncertain. Review destructive fixer behavior separately. Use Nexora as a validation sample, but treat reported findings as hypotheses until checked against source context.

**Deliverables:** Updated `docs/existing-system-assessment.md`, accurate README/current architecture, list of reusable components and gaps.

**Exit:** Important capabilities have evidence or are explicitly marked uncertain.

## Stage 2 — Analysis foundation and reliability

Subject to Stage 1 findings, improve discovery/exclusions, parser behavior, import resolution, graph correctness, analysis rules, finding evidence, diagnostics, terminal/JSON output, configuration, and fixer safeguards.

**Exit:** Acceptance tests cover supported behavior, limitations are documented, and ordinary analysis is read-only.

## Stage 3 — Full-stack awareness

Add small, testable slices:
1. Flask route and handler recognition.
2. Statically identifiable route-to-Jinja2-template relationships.
3. Jinja2 inheritance/include/import references.
4. HTML references to CSS and JavaScript assets.
5. Shared representation of these relationships.
6. Selected JavaScript endpoint references if feasible.

Work may overlap with Stage 2 when foundations are stable. Do not attempt every frontend framework at once.

**Exit:** Each relationship type has positive, negative, and ambiguous/dynamic fixtures; uncertainty is explicit; Python regression tests remain green.

## Stage 4 — Architecture exploration and reporting

Improve component inventory, relationship diagrams, finding details/source navigation, grouping/prioritization, report metadata, and architecture summaries. Verify which capabilities already exist before implementing duplicates.

## Stage 5 — Evidence-grounded AI assistance

Prepare bounded context from analysis results; support project questions, explanations, and recommendations with rationale and evidence. Clearly label AI interpretation and uncertainty. Decide provider, privacy, cost, and local-inference strategy before implementation.

**Exit:** AI is optional; deterministic analysis still works independently; evaluations check grounding and unsupported claims.

## Stage 6 — Interaction and graphical interface

Consider interactive terminal workflows and a local web dashboard or other GUI. Choose the technology through a documented decision. Keep presentation separate from application/analysis services.

## Stage 7 — Controlled change workflows

If justified, add change-impact explanations, diff previews, explicit authorization, backups/rollback, and post-change tests/analysis. Do not make broad autonomous rewriting the default.

## Stage 8 — Release hardening

Verify clean installation, supported OS/Python matrix, security/privacy, benchmark performance, report compatibility, docs, contribution guidance, and release packaging.

## Later possibilities

Additional languages/frameworks, persistent history/trends, CI/CD and IDE integrations, hosted collaboration, and a plugin ecosystem are deferred until concrete requirements justify them.

## Governance

Update requirements and traceability after each stage. A stage is complete only when exit criteria have evidence from tests, review, or reproducible demonstrations—not merely because code exists.
