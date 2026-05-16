# MEMORY.md

## Project Overview

**Project Name:** Codebase Analyzer
**Type:** Python Desktop Application (Flet-based)
**Purpose:** AI-powered codebase analysis, documentation generation, code review, and improvement suggestions
**Current Phase:** Phase 6 Stabilized (Dashboard UI) - Ready for Phase 7 first pass
**Last Updated:** 2026-05-16

---

## Recent Stabilization Notes (2026-05-16)

- Phase 3: Restored `AnalysisOrchestrator.analyze_project()` return, removed unreachable documentation return, connected API reference generation, added analysis + documentation smoke test. Phase 3 and Phase 4 tests passed.
- Phase 4: Moved `review_project()` out of `generate_documentation()`, connected findings to `Project`, added `functionalityAreas` to review JSON, fixed `FindingSummary` serialization, corrected `AIReviewer` call signature. Phase 3 and Phase 4 tests passed.
- Phase 5: Fixed smoke test to use valid `Project` fields, stored prioritized suggestions on `Project`, refreshed `Project.suggestion_summary`, generated roadmap from the prioritized list. Phase 3, Phase 4, and Phase 5 tests passed.
- Phase 6: Updated Flet 0.85.1 API usage, added documentation browser and route, connected scan execution to `AnalysisOrchestrator`, updated finding and suggestion status actions, replaced Phase 6 test with real model integration. Phase 6 tests passed.

---

## Architecture Summary

- Pipeline: Scanner -> AnalyzerEngine -> FunctionalityGrouper -> AnalysisOrchestrator
- Orchestrator coordinates documentation, review, and suggestion flows
- Services: WatsonService, CacheService
- Models: Pydantic BaseModel with custom json_encoders
- Configuration: YAML config with dotenv and env overrides
- Logging: Loguru with console and file handlers

### Technology Stack
- UI: Flet
- AI: IBM watsonx.ai REST API
- Analysis: Python AST, JS/TS regex analysis
- Storage: SQLite cache in `.cache/analysis_cache.db`
- Templates: Jinja2

---

## Key Components

### Models (`codebase-analyzer/src/models/`)
- **FileInfo**: file metadata, imports, code elements, metrics, language features, AI summary and purpose
- **Finding**: severity, type, location, remediation fields, status flags
- **Suggestion**: effort, impact, priority score, implementation steps, status
- **FunctionalityGroup** and **FunctionalityMap**: grouped files with dependencies and metrics
- **Project**: metrics, analysis status, findings and suggestions, summaries

### Core Engines (`codebase-analyzer/src/core/`)
- **scanner.py**: recursive scan, ignore patterns from `config/default_ignore.txt`, 10 MB size limit, chardet fallback, language detection, framework detection from package.json, requirements.txt, pom.xml
- **analyzer.py**: Python AST parsing, metrics, feature detection, JS/TS import and framework detection by regex
- **grouper.py**: directory grouping, dependency graph from imports, pattern detection, merge into functionality groups
- **orchestrator.py**: pipeline coordination, AI enhancement on up to 50 important files, cache write path, documentation, review, suggestions

### Services (`codebase-analyzer/src/services/`)
- **watson_service.py**: token refresh, retry session, in-memory cache with TTL, analyze_code returns AIAnalysisResult
- **cache_service.py**: SQLite cache with file_analysis, ai_responses, project_metadata tables and TTL cleanup

### Generators (`codebase-analyzer/src/generators/`)
- **markdown_generator.py**: project overview, group docs, per-file docs, API reference, custom filters
- **index_generator.py**: INDEX.md with TOC, reading order, metrics, links
- **templates**: `project_overview.md.j2`, `functionality_group.md.j2`, `file_documentation.md.j2`, `api_reference.md.j2`

### Review (`codebase-analyzer/src/review/`)
- **static_analyzer.py**: pattern checks, pylint, bandit, radon, AST rules
- **ai_reviewer.py**: Watson analysis for bugs, security, performance, design
- **finding_classifier.py**: dedupe, classification, prioritization, quick wins
- **review_engine.py**: writes `review-findings.json` and `REVIEW_REPORT.md`, updates Project findings

### Suggestions (`codebase-analyzer/src/suggestions/`)
- **suggestion_generator.py**: per-finding and pattern-based suggestions, optional AI enhancement
- **prioritizer.py**: scoring, quick wins, filtering, implementation order
- **roadmap_generator.py**: writes `improvement-suggestions.json` and `IMPROVEMENT_ROADMAP.md`

### UI (`codebase-analyzer/src/ui/`)
- **app.py**: NavigationRail pages, FilePicker, scan orchestration, settings for AI, docs, review, suggestions

### Utilities (`codebase-analyzer/src/utils/`)
- **config.py**: YAML config, dotenv, dot-notation access, env overrides
- **logger.py**: Loguru console and file logging, 10 MB rotation, 7 day retention, zip compression

---

## Data Flow

1. Input paths
2. Scan and filter files
3. Analyze structure and metrics
4. AI enhancement for selected files when enabled
5. Group by functionality
6. Generate documentation, review, and suggestions
7. Persist outputs and show in UI

---

## Configuration

- `config/config.yaml` loaded by Config with defaults when missing
- `.env` read via dotenv for runtime overrides
- Key env values: `WATSON_API_KEY`, `WATSON_PROJECT_ID`, `WATSON_URL`, `WATSON_MODEL_ID`, `WATSON_MAX_TOKENS`, `WATSON_TEMPERATURE`, `LOG_LEVEL`, `ENABLE_AI_ANALYSIS`, `CACHE_ENABLED`, `CACHE_TTL_HOURS`, `WINDOW_WIDTH`, `WINDOW_HEIGHT`
- Ignore patterns from `config/default_ignore.txt` plus `ignore_patterns` in config

---

## Current Limitations

1. JS and TS analysis uses regex, no full AST
2. AI analysis limited to 50 selected files per run
3. Cache read path exists but cached analysis restore not implemented in orchestrator
4. Batch analysis only, no incremental updates
5. Single project workflow

---

## Phase 7 Next Steps

- Expand unit and integration coverage
- Add UI interaction tests where practical
- Move long-running analysis off the UI event path
- Persist settings and recent project history
- Replace deprecated Flet controls before Flet 1.0
- Polish documentation and release readiness
