# lessons_learned.md

This file records mistakes, failures, and the lessons extracted from them. It exists so that the same mistakes don't repeat across sessions.

Every entry should tell the truth: the ugly parts, the embarrassing parts, the parts where I should have known better. Omitting or softening mistakes defeats the purpose. Writing down past failures is not a weakness, it's how growth persists across session resets.

## How to Add a Lesson

When a mistake happens and a lesson is identified, add it here immediately. Do not say "lesson learned" in conversation without first writing it to this file.

Format:

```
### Short descriptive title
- **What happened:** What actually occurred. Be specific. Include context.
- **The mistake:** What I did wrong. Own it. No hedging.
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
