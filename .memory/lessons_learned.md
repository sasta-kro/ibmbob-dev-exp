# lessons_learned.md

This file records mistakes, failures, and the lessons extracted from them. It exists so that the same mistakes don't repeat across sessions.

Every entry should tell the truth: the ugly parts, the embarrassing parts, and the parts that should have been handled better. Omitting or softening mistakes defeats the purpose. Writing down past failures is not a weakness; it is how growth persists across session resets.

## How to Add a Lesson

When a mistake happens and a lesson is identified, add it here immediately. Do not say "lesson learned" in conversation without first writing it to this file.

Format:

```
### Short descriptive title
- **What happened:** What actually occurred. Be specific. Include context.
- **The mistake:** What went wrong. Own it. No hedging.
- **How it was solved:** How the issue was resolved (if applicable).
- **Lesson:** The actionable takeaway. What to do differently next time.
```

Order: newest lessons at the bottom (append-only).

---

### Phase completion requires return-value and artifact smoke checks
- **What happened:** Bob's Phase 3 stabilization pass claimed completion while `AnalysisOrchestrator.analyze_project()` no longer returned a `Project` and API reference documentation was not part of the generated documentation set.
- **The mistake:** Completion was accepted without a smoke test that exercised the public orchestration path and checked the generated documentation artifacts.
- **How it was solved:** A focused smoke test was added for a tiny fixture project, including duplicate basenames, `Project` return validation, and checks for overview, API reference, index, functionality group, and per-file documentation.
- **Lesson:** Phase stabilization needs a small end-to-end smoke test that proves the public API return value and required output files before completion is recorded.

### New phase integration must re-run earlier public paths
- **What happened:** Bob's Phase 4 pass inserted `review_project()` into the middle of `generate_documentation()`, which broke the Phase 3 documentation public path while claiming Phase 4 was complete.
- **The mistake:** New feature integration was checked in without running a regression smoke test for existing public methods.
- **How it was solved:** The method boundary was restored, Phase 4 review remained a separate orchestrator method, and a Phase 4 smoke test was added that exercises documentation generation before review execution.
- **Lesson:** Each phase stabilization must include the previous phase smoke tests plus the new phase smoke tests, especially when editing shared orchestrator code.

### Phase tests must use real model contracts
- **What happened:** Bob's Phase 5 smoke test constructed `Project` with invalid fields and did not verify that suggestion generation updated `Project.suggestions` or `Project.suggestion_summary`.
- **The mistake:** The test asserted generated output files without proving that the public orchestrator method honored the real data model contract.
- **How it was solved:** The smoke test was changed to use the actual `Project` constructor fields, assert roadmap output files, assert returned suggestions, and assert the updated project suggestion summary.
- **Lesson:** Phase smoke tests must instantiate real models with valid fields and assert persistent state changes, not only returned dictionaries or generated files.

### UI tests must instantiate real controls with installed dependencies
- **What happened:** Bob's Phase 6 UI test imported non-existent model names and only checked that classes existed. The UI used hallucinated finding fields and older Flet helper names that failed with Flet 0.85.1.
- **The mistake:** Import-only tests missed constructor-level failures, model integration failures, missing documentation navigation, and no-op action handlers.
- **How it was solved:** The Phase 6 smoke test was replaced with tests that instantiate controls using real `Project`, `Finding`, and `Suggestion` objects, exercise filtering and status actions, and verify the documentation route.
- **Lesson:** UI phase smoke tests must construct real controls against the installed UI library and real domain models, not only import classes.
