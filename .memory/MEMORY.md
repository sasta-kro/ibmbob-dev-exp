# MEMORY.md

## Project Overview

**Project Name:** Codebase Analyzer  
**Type:** Python Desktop Application (Flet-based)  
**Purpose:** AI-powered codebase analysis, documentation generation, code review, and improvement suggestions  
**Current Phase:** Phase 4 Complete (Code Review Engine) - Ready for Phase 5
**Current Phase:** Phase 3 Stabilization Fix Applied (Documentation Generator) - Runtime smoke verification pending dependency install
**Last Updated:** 2026-05-16

---

## Recent Stabilization Notes

- 2026-05-16: Bob's Phase 3 stabilization pass regressed `AnalysisOrchestrator.analyze_project()` by moving `return project` out of the method. The follow-up fix restored the return, removed the unreachable documentation return, connected API reference generation to the documentation flow, and added a smoke test for analysis plus documentation output. Runtime smoke execution is blocked until the project dependency stack is installed.

---

## Architecture Summary

### Core Design Pattern
**Modular Pipeline Architecture** with clear separation of concerns:
- **Scanner** → **Analyzer** → **Grouper** → **Orchestrator**
- Services layer for external integrations (Watson AI, Cache)
- Pydantic models for type-safe data structures
- Configuration-driven behavior

### Technology Stack
- **UI:** Flet (Flutter-based, Material Design)
- **AI:** IBM Watson AI (watsonx.ai) with granite-code model
- **Analysis:** Python AST, tree-sitter (planned for JS/TS)
- **Storage:** SQLite for caching
- **Config:** YAML + environment variables
- **Logging:** Loguru with file rotation

---

## Key Components

### 1. Data Models (`src/models/`)
**Status:** Complete and production-ready

**FileInfo Model:**
- Comprehensive file metadata (path, size, timestamps, encoding)
- Code structure (imports, exports, code elements)
- Metrics (LOC, complexity, maintainability index)
- AI-generated insights (summary, purpose)
- Helper methods for filtering (get_functions, get_classes, get_public_api)

**Finding Model:**
- Code review findings with severity levels (critical → info)
- Classification by type (bug, security, performance, style, etc.)
- Location tracking with code snippets
- Remediation recommendations
- Status tracking (resolved, false positive)

**Suggestion Model:**
- Improvement suggestions with effort/impact analysis
- Priority scoring algorithm
- Implementation steps and guidance
- Status tracking (pending → completed)
- Quick win identification (low effort, high impact)

**FunctionalityGroup Model:**
- Groups related files by purpose
- Dependency tracking between groups
- Complexity scoring
- Entry point identification

**Project Model:**
- Central aggregation of all analysis results
- Metrics rollup (total files, lines, complexity)
- Status tracking for analysis pipeline
- Save/load to JSON

### 2. Core Engines (`src/core/`)

**Scanner (`scanner.py` - 482 lines):**
- Recursive directory traversal with gitignore-style patterns
- 20+ language detection via file extensions
- Framework detection (React, Vue, Django, Flask, Express, Next.js, Spring)
- Binary file filtering and large file handling (10MB limit)
- Encoding detection with chardet fallback
- Progress callback support for UI updates

**Analyzer (`analyzer.py` - 551 lines):**
- Python AST parsing with full code element extraction
- Cyclomatic complexity calculation
- Import/export analysis
- Language feature detection (async/await, type hints, decorators, f-strings, etc.)
- JavaScript/TypeScript basic analysis (regex-based, can be enhanced)
- Parallel processing with ThreadPoolExecutor
- Dependency graph building

**Grouper (`grouper.py` - 491 lines):**
- Multi-strategy grouping:
  1. Directory structure analysis
  2. Pattern-based detection (15 predefined patterns)
  3. Dependency graph analysis
  4. Semantic understanding (AI-enhanced)
- Cross-group dependency tracking
- Entry point identification
- Complexity scoring per group
- Categories: Authentication, Database, API, UI, Testing, Configuration, Utilities, Security, Payment, Notification, Analytics, Admin, User, Search, Storage

**Orchestrator (`orchestrator.py` - 387 lines):**
- Unified analysis pipeline coordinator
- Smart file selection for AI (top 50 important files based on complexity, size, entry points)
- Cache integration throughout pipeline
- Progress tracking with callbacks
- Graceful degradation when AI unavailable
- Project object creation and metadata caching

### 3. Services (`src/services/`)

**Watson Service (`watson_service.py` - 454 lines):**
- IBM watsonx.ai REST API integration
- Token-based authentication with auto-refresh (5min safety margin)
- Multiple model support (granite-code, codellama, mixtral)
- Retry logic with exponential backoff
- Response caching (SHA256-based keys)
- Three analysis modes:
  1. Code analysis (summary, purpose, functionality)
  2. Bug detection (logic errors, security issues)
  3. Improvement suggestions (performance, quality, security)
- JSON response parsing with fallback to text parsing

**Cache Service (`cache_service.py` - 529 lines):**
- SQLite-based persistent storage
- Three cache tables:
  1. file_analysis (content hash-based)
  2. ai_responses (prompt hash-based)
  3. project_metadata (project path-based)
- TTL-based expiration (7 days default)
- Automatic cleanup of expired entries
- Thread-safe operations with context managers
- Database optimization (VACUUM)
- Statistics tracking

### 4. Utilities (`src/utils/`)

**Config (`config.py` - 247 lines):**
- YAML-based configuration with environment variable overrides
- Dot-notation access (e.g., 'app.name')
- Property-based convenience accessors
- Default configuration fallback
- Global singleton pattern

**Logger (`logger.py` - 67 lines):**
- Loguru-based logging
- Console output with colors
- File output with rotation (10MB) and retention (7 days)
- Compression of old logs (zip)
- Module-specific logger binding

---

## Design Patterns Used

1. **Pipeline Pattern:** Scanner → Analyzer → Grouper → Orchestrator
2. **Strategy Pattern:** Multiple grouping strategies in Grouper
3. **Factory Pattern:** Model creation methods
4. **Singleton Pattern:** Global config instance
5. **Observer Pattern:** Progress callbacks
6. **Repository Pattern:** Cache service as data access layer
7. **Dependency Injection:** Config passed to all components

---

## Code Quality Observations

### Strengths
- Comprehensive docstrings on all classes and methods
- Type hints throughout (Python 3.10+ style)
- Descriptive variable and function names
- Self-documenting code structure
- Proper error handling with logging
- Modular and reusable components
- Clear separation of concerns
- Consistent "Made with Bob" signature

### Areas for Enhancement
1. **JavaScript/TypeScript Analysis:** Currently regex-based, could use proper AST parser (esprima/babel)
2. **Test Coverage:** No tests yet (scheduled for Phase 7)
3. **UI Components:** Not yet implemented (Phase 6)
4. **Documentation Generator:** Next phase (Phase 3)
5. **Code Review Engine:** Not yet implemented (Phase 4)
6. **Suggestion Engine:** Not yet implemented (Phase 5)

---

## Configuration System

### Environment Variables (`.env`)
- Watson AI credentials (API key, project ID, model)
- Cache settings (TTL, enabled/disabled)
- Analysis settings (max workers, file size limit)
- UI settings (theme, window dimensions)

### Config File (`config/config.yaml`)
- Ignore patterns (gitignore-style)
- Language configurations
- Review severity levels
- Documentation settings
- Export formats

### Ignore Patterns
Comprehensive default ignore list including:
- Version control (.git, .svn, .hg)
- Dependencies (node_modules, venv, vendor)
- Build outputs (dist, build, target)
- IDE files (.vscode, .idea)
- Compiled files (*.pyc, *.class, *.o)
- Minified files (*.min.js, *.bundle.js)
- Lock files (package-lock.json, poetry.lock)
- Logs and temp files
- Large media files

---

## Data Flow

1. **Input:** Project path(s)
2. **Scanning:** Discover files, filter by patterns, extract metadata
3. **Analysis:** Parse code, extract structure, calculate metrics
4. **AI Enhancement:** Semantic analysis on important files (optional)
5. **Grouping:** Organize files by functionality
6. **Framework Detection:** Identify technologies used
7. **Project Creation:** Aggregate all results
8. **Caching:** Store results for future runs
9. **Output:** Project object with complete analysis

---

## Performance Optimizations

1. **Parallel Processing:** ThreadPoolExecutor for file analysis
2. **Smart AI Selection:** Only analyze top 50 important files
3. **Content-based Caching:** SHA256 hashes prevent re-analysis
4. **Lazy Loading:** Read files only when needed
5. **Database Indexing:** Optimized SQLite queries
6. **Progress Callbacks:** Non-blocking UI updates

---

## Error Handling Strategy

- Try-except blocks at component boundaries
- Graceful degradation (AI optional, cache optional)
- Comprehensive logging at all levels
- User-friendly error messages
- Continue on file-level errors, collect in error list
- Timeout handling for long operations

---

## Integration Points

### Watson AI Integration
- REST API with Bearer token authentication
- Token refresh before expiry
- Configurable models and parameters
- Fallback when unavailable

### Cache Integration
- Transparent to callers
- Content hash-based invalidation
- Automatic cleanup
- Statistics for monitoring

### UI Integration (Planned)
- Progress callbacks for real-time updates
- Async operations for responsiveness
- Status tracking in Project model

---

## Current Limitations

1. **Language Support:** Full AST only for Python; JS/TS basic only
2. **AI Cost:** Limited to 50 files per analysis to control costs
3. **Cache Growth:** SQLite can grow large, needs periodic cleanup
4. **No Real-time:** Analysis is batch-based, not incremental
5. **Single Project:** No multi-project comparison yet

---

## Next Steps (Phase 3)

**Documentation Generator Implementation:**
- Markdown generator for project docs
- HTML generator with syntax highlighting
- Template system (Jinja2)
- API documentation extraction
- README generation
- Cross-reference linking

**Files to Create:**
- `src/generators/markdown_generator.py`
- `src/generators/html_generator.py`
- `src/generators/readme_generator.py`
- `src/templates/` directory with Jinja2 templates

---

## Important Notes

### For Future Development
1. All Phase 2 components are production-ready
2. Use Orchestrator as main entry point
3. Cache service auto-initializes
4. Watson AI gracefully degrades if not configured
5. Models are fully type-safe with Pydantic
6. Configuration is centralized and environment-aware

### Testing Strategy (Phase 7)
1. Create fixtures with sample projects
2. Mock Watson API to avoid costs
3. Use temporary directories for cache
4. Test with and without AI enabled
5. Test parallel processing edge cases

### Code Style Compliance
- No em-dashes ✓
- No emojis in code ✓
- No personal pronouns in docs ✓
- Descriptive names ✓
- Self-documenting code ✓
- Comments for 'why' not 'what' ✓

---

## References

- **Architecture:** `plan.md` (1283 lines, comprehensive technical plan)
- **Implementation Guide:** `IMPLEMENTATION_GUIDE.md` (320 lines, phase-by-phase guide)
- **Phase 2 Report:** `.memory/Implementation_progress/PHASE2_COMPLETION.md`
- **Requirements:** `codebase-analyzer/requirements.txt`
- **Config:** `codebase-analyzer/config/config.yaml`
- **Agent Rules:** `AGENTS.md`
### 5. Documentation Generators (`src/generators/`)

**Markdown Generator (`markdown_generator.py` - 429 lines):**
- Jinja2 template engine integration
- Custom filters (format_date, format_size, format_complexity, escape_markdown)
- Project overview documentation generation
- Functionality group documentation
- Per-file documentation with code structure
- API reference generation
- Fallback content when templates fail
- Safe cross-platform filename generation

**Index Generator (`index_generator.py` - 375 lines):**
- Main index page with navigation
- Table of contents generation
- Cross-reference linking
- Reading order suggestions based on dependencies
- Search keyword generation
- File grouping by directory
- Relative path calculation for links
- Statistics and metrics summary

**Jinja2 Templates (`src/templates/`):**
- `project_overview.md.j2` (152 lines) - Project summary, metrics, groups
- `functionality_group.md.j2` (197 lines) - Group details, files, components

### 6. Code Review Components (`src/review/`)

**Static Analyzer (`static_analyzer.py` - 697 lines):**
- Pattern-based detection (security, bugs, performance)
- Pylint integration for code quality
- Bandit integration for security scanning
- Complexity analysis
- AST-based analysis (bare except, mutable defaults)
- Finding deduplication
- Code snippet extraction with context
- 10 predefined detection patterns

**AI Reviewer (`ai_reviewer.py` - 524 lines):**
- IBM Watson AI integration for deep analysis
- Smart file selection (top 50 important files)
- Bug detection (logic errors, type mismatches, race conditions)
- Security vulnerability detection (SQL injection, XSS, auth issues)
- Performance issue detection (N+1 queries, inefficient algorithms)
- Design issue detection (SOLID violations, code duplication)
- AI response parsing into Finding objects
- Confidence scoring and code snippet extraction

**Finding Classifier (`finding_classifier.py` - 365 lines):**
- Multi-dimensional classification (severity, type, file, source)
- Priority scoring algorithm (severity + confidence + type + actionability)
- Finding deduplication with confidence-based selection
- Statistical analysis and metrics calculation
- Filtering by severity, type, confidence
- Quick wins identification (low effort, high impact)
- High priority finding detection
- Grouping and aggregation

**Review Engine (`review_engine.py` - 378 lines):**
- Main coordinator for all review activities
- Static analysis orchestration
- AI review orchestration (optional)
- Finding classification and prioritization
- JSON report generation (review-findings.json)
- Markdown report generation (REVIEW_REPORT.md)
- Comprehensive statistics and summaries
- Integration with Project model

**Orchestrator Integration:**
- ReviewEngine initialized in AnalysisOrchestrator
- New `review_project()` method for code reviews
- Seamless integration with analysis pipeline
- Optional AI-powered review
- Configurable output directory

- `file_documentation.md.j2` (280 lines) - File structure, API, metrics
- `api_reference.md.j2` (137 lines) - Public API reference
