<img width="1920" height="1080" alt="IBM BOB Hackathon Slides" src="https://github.com/user-attachments/assets/a7b94b51-1e19-48fa-bd4c-9dcd26070926" /># Codebase Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-Desktop%20UI-009DFF?style=flat)](https://flet.dev/)
[![Pydantic](https://img.shields.io/badge/Pydantic-Data%20Models-E92063?style=flat)](https://docs.pydantic.dev/)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-052FAD?style=flat&logo=ibm&logoColor=white)](https://www.ibm.com/products/watsonx-ai)
[![SQLite](https://img.shields.io/badge/SQLite-Cache-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Markdown](https://img.shields.io/badge/Markdown-Docs-000000?style=flat&logo=markdown&logoColor=white)](https://www.markdownguide.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

<img width="1920" height="1080" alt="IBM BOB Hackathon Slides" src="https://github.com/user-attachments/assets/e92181b0-fb5c-4988-8184-ee8eb4a53f08" />

Codebase Analyzer is a desktop app that turns a repository into an organized code intelligence workspace. The app scans a codebase, maps repository structure, groups related files, generates Markdown documentation, finds risky code patterns, and turns review results into prioritized improvement plans.

The goal is simple. Make an unfamiliar codebase feel readable, searchable, and ready for action from one place.

Built for the IBM Bob Hackathon, the project focuses on the theme of turning idea into impact faster. The app highlights how repository-aware AI workflows can reduce repetitive engineering work, speed up onboarding, and help builders move from scattered source files to clear next steps.

## Why This Matters

Modern repositories become hard to understand fast. Important logic gets spread across folders, documentation falls behind, review notes live outside the project, and improvement work becomes difficult to prioritize.

Codebase Analyzer brings the first-pass workflow into one app.

- See the project shape without manually reading every file
- Generate useful Markdown docs from the real codebase
- Review security, quality, complexity, and maintainability risks
- Convert findings into ranked suggestions with effort and impact
- Browse docs, findings, suggestions, and metrics in a clean modern desktop dashboard
- Use IBM watsonx.ai for optional AI-assisted code understanding

## Core Features

### Modern Desktop Workspace

- Sleek left-rail navigation for Home, Scan, Overview, Docs, Findings, Suggestions, and Settings
- Card-based overview with large project metrics, framework chips, and readable donut charts
- Search-first documentation browser with grouped navigation and built-in Markdown rendering
- Focused findings and suggestions queues with severity badges, priority scores, and fast filtering
- Smooth scan progress screen with stage tracking, current file activity, and recent file history
- Calm settings panel for Watson credentials, model settings, and analysis toggles

### Repository Scan

- Recursive project scanning with ignore rules for dependencies, build outputs, caches, binary files, logs, and environment files
- File type detection for Python, JavaScript, TypeScript, JSON, YAML, Markdown, text, and unknown files
- Safe handling for large files and unreadable files
- SHA256 content hashes for cache-aware repeat analysis
- Framework detection for React, Vue, Angular, Express, Next.js, Django, Flask, FastAPI, and Spring

### Code Structure Analysis

- Python AST parsing for imports, functions, classes, decorators, parameters, return types, and docstrings
- Complexity metrics for Python functions and files
- Language feature detection for async code, type hints, decorators, context managers, generators, comprehensions, f-strings, and dataclass-style patterns
- Basic JavaScript and TypeScript import extraction
- JavaScript framework pattern detection for React, Vue, Angular, Express, and Next.js

### Functionality Grouping

- Automatic grouping by folder structure, naming patterns, and import relationships
- Built-in domain categories such as authentication, database, API, UI, testing, configuration, utilities, security, payment, notification, analytics, admin, user, search, and storage
- Group-level metrics for files, lines of code, complexity, dependencies, and entry points
- Documentation organized around functional areas instead of only raw file paths

### Documentation Generator

The app creates Markdown output that is useful for humans and AI coding agents.

- `PROJECT_OVERVIEW.md`
- `INDEX.md`
- `API_REFERENCE.md`
- per-file documentation
- functionality group documentation

Generated docs include metrics, public APIs, classes, functions, imports, dependencies, language features, parse warnings, and AI summaries when Watson analysis is enabled.

### Code Review Engine

Static analysis and custom checks detect practical issues.

- hardcoded passwords and API keys
- SQL injection patterns
- `eval` and `exec` usage
- bare `except` blocks
- empty `except: pass` blocks
- mutable default arguments
- high cyclomatic complexity
- Pylint code quality findings
- Bandit security findings
- common Python style and reliability patterns

Review output files

- `review-findings.json`
- `REVIEW_REPORT.md`

### Improvement Suggestions

Findings become actionable suggestions with ranking data and implementation context.

- priority score
- effort level
- impact level
- affected files
- related finding IDs
- rationale
- benefits
- considerations
- risks
- implementation steps
- estimated time

Roadmap output files

- `improvement-suggestions.json`
- `IMPROVEMENT_ROADMAP.md`

### Desktop Dashboard

The Flet UI provides a single workspace for the whole flow.

- Home page with recent scan history
- Scan page with folder selection, analysis options, smooth progress stages, and recent file activity
- Overview page with metric cards, distribution charts, and quick navigation
- Documentation browser with search, grouped folders, compact metric pills, and Markdown rendering
- Findings page with searchable review results and severity badges
- Suggestions page with searchable priority-ranked improvements and effort-impact tags
- Settings page for Watson credentials, model settings, and analysis options

## IBM Bob Hackathon Fit

This project is designed around real developer workflow acceleration.

- Full repository context instead of isolated code snippets
- Fast project understanding for unfamiliar codebases
- Automated documentation generation from actual source structure
- Review findings converted into implementation-ready improvement plans
- Practical AI-assisted development that keeps code, docs, review, and next actions in one place

The strongest pitch framing is convenience with substance. One workflow for understanding, documenting, reviewing, and improving a codebase.

## Current Language Support

| Language or File Type | Current Support |
|---|---|
| Python | AST parsing, imports, functions, classes, metrics, static review, security review |
| JavaScript | file detection, import extraction, basic framework detection, metrics |
| TypeScript | file detection, import extraction, basic framework detection, metrics |
| JSON | file detection and documentation coverage |
| YAML | file detection and documentation coverage |
| Markdown | file detection and documentation coverage |
| Text | file detection and documentation coverage |

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop UI | Flet |
| Core language | Python 3.10+ |
| Data models | Pydantic |
| AI integration | IBM watsonx.ai API |
| Static analysis | Python AST, Pylint, Bandit |
| Documentation | Jinja2, Markdown |
| Cache | SQLite |
| Config | YAML, dotenv, JSON user config |
| Charts | Flet chart components and SVG-rendered chart assets |

## Architecture

```text
Flet Desktop UI
  Home, Scan, Overview, Docs, Findings, Suggestions, Settings

Analysis Orchestrator
  Scanner -> Analyzer -> Watson Service -> Grouper

Review Pipeline
  Static Analyzer -> AI Reviewer -> Finding Classifier

Suggestion Pipeline
  Suggestion Generator -> Prioritizer -> Roadmap Generator

Output Layer
  Markdown docs, JSON reports, review report, improvement roadmap

Storage
  SQLite cache, local scan history, project output folder
```

## Generated Output

After a scan, project artifacts are written into the analyzed project under this folder.

```text
.codebase-analyzer/
  docs/
    PROJECT_OVERVIEW.md
    INDEX.md
    API_REFERENCE.md
    files/
    functionality_groups/
  review/
    review-findings.json
    REVIEW_REPORT.md
  suggestions/
    improvement-suggestions.json
    IMPROVEMENT_ROADMAP.md
```

Recent scan history is stored locally under this folder.

```text
~/.codebase-analyzer/history/
```

## Setup

### Requirements

- Python 3.10 or newer
- IBM watsonx.ai API key and project ID for AI features
- macOS, Linux, or Windows with Python desktop app support

### Install

```bash
cd codebase-analyzer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows activation

```bash
.venv\Scripts\activate
```

### Configure Watson

Create an environment file.

```bash
cp .env.example .env
```

Set the required values.

```env
WATSON_API_KEY=replace_with_api_key
WATSON_URL=https://us-south.ml.cloud.ibm.com
WATSON_PROJECT_ID=replace_with_project_id
WATSON_MODEL_ID=openai/gpt-oss-120b
WATSON_MAX_TOKENS=2000
WATSON_TEMPERATURE=0
```

Credentials can also be entered through the app settings screen. User settings are saved to this file.

```text
codebase-analyzer/config/user_config.json
```

That file is ignored by git.

## Run

```bash
cd codebase-analyzer
source .venv/bin/activate
python run_ui.py
```

Windows

```bash
cd codebase-analyzer
.venv\Scripts\activate
python run_ui.py
```

## App Workflow

1. Open the app.
2. Enter Watson credentials in Settings when AI features are needed.
3. Start a new analysis.
4. Select or paste a project folder path.
5. Choose analysis options.
   - AI-powered analysis
   - documentation generation
   - code review
   - improvement suggestions
6. Run the scan.
7. Review the Overview dashboard.
8. Browse generated docs, findings, and suggestions.

## Future Roadmap

### Broader Language Intelligence

Planned language expansion includes deeper support for the most common production stacks.

- Java
- C#
- Go
- Rust
- PHP
- Ruby
- Kotlin
- Swift
- C
- C++
- Scala
- SQL
- HTML and CSS

Future versions should add full AST parsing, framework-specific conventions, public API extraction, dependency mapping, and code review rules for these ecosystems.

### Swappable AI Backend

The current implementation integrates IBM watsonx.ai. A future provider adapter layer should make the AI backend swappable, so each team can choose a preferred model stack.

Planned backend options include the following.

- IBM watsonx.ai models
- IBM Granite code models
- OpenAI models
- Anthropic Claude models
- Google Gemini models
- local models through Ollama or compatible OpenAI-style endpoints
- custom enterprise AI gateways

The target design is a simple provider interface for code summaries, review findings, grouping hints, and improvement suggestions.

### More Agent-Friendly Output

Future documentation output can become even more useful for AI coding agents.

- compact repository maps
- task-ready context packs
- change impact summaries
- generated test plans
- architecture decision summaries
- onboarding briefs for new contributors

### Smarter Review And Planning

Planned upgrades include the following.

- deeper cross-file bug detection
- duplicate logic detection
- dead code detection
- dependency risk scoring
- test coverage awareness
- security policy presets
- CI-ready quality gates
- direct GitHub issue export
- suggested pull request breakdowns

### Team And Workflow Features

Potential goals include the following.

- project comparison across scans
- trend charts across time
- shared team reports
- exportable executive summaries
- PDF and HTML report export
- repository health score
- saved filters and triage status
- integration with GitHub, GitLab, Jira, Linear, and Slack

## Project Status

The current app is a hackathon-ready proof of concept with a working desktop workflow, real repository scanning, generated documentation, static review, suggestion generation, local cache, scan history, and a dashboard UI.

The clearest next step is deeper language intelligence and a formal AI provider adapter layer.

## License

MIT License. See [LICENSE](LICENSE).
