# Codebase Analyzer

A powerful Python desktop application that analyzes project codebases, generates AI-optimized documentation, performs intelligent code reviews, and provides actionable improvement suggestions.

## Features

- 🔍 **Smart Code Scanning** - Recursively scans codebases with intelligent ignore patterns
- 🤖 **AI-Powered Analysis** - Leverages IBM Watson AI for deep code understanding
- 📚 **Documentation Generation** - Creates comprehensive Markdown documentation
- 🔒 **Security Review** - Identifies security vulnerabilities and best practice violations
- 💡 **Improvement Suggestions** - Provides prioritized, actionable recommendations
- 📊 **Interactive Dashboard** - Modern Flet-based UI with charts and visualizations
- 🎯 **Functionality Grouping** - Intelligently groups related code by purpose
- ⚡ **Performance Metrics** - Tracks complexity, maintainability, and code quality

## Supported Languages

- Python (.py)
- JavaScript (.js, .jsx, .mjs)
- TypeScript (.ts, .tsx)

## Technology Stack

- **UI Framework**: Flet (Flutter-based, Material Design)
- **AI Integration**: IBM Watson AI (watsonx.ai)
- **Static Analysis**: pylint, bandit, radon, mypy
- **Code Parsing**: Python AST, tree-sitter
- **Documentation**: Jinja2, Markdown
- **Data Models**: Pydantic
- **Visualization**: Plotly

## Installation

### Prerequisites

- Python 3.10 or higher
- IBM Watson AI API credentials (for AI-powered features)

### Setup

1. **Clone or download the project**

2. **Create a virtual environment**
   ```bash
   cd codebase-analyzer
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your IBM Watson credentials:
   ```
   WATSON_API_KEY=your_api_key_here
   WATSON_URL=https://us-south.ml.cloud.ibm.com
   WATSON_PROJECT_ID=your_project_id_here
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- **IBM Watson AI**: API key, URL, project ID, model settings
- **Application**: Name, version, log level
- **Cache**: Enable/disable, TTL settings
- **Analysis**: Max file size, worker threads, AI analysis toggle
- **UI**: Theme, window dimensions

### Configuration File

Edit `config/config.yaml` to customize:

- Ignore patterns (gitignore-style)
- Supported languages and extensions
- Code review severity levels
- Documentation settings
- Cache configuration

## Project Structure

```
codebase-analyzer/
├── src/
│   ├── core/              # Core business logic
│   ├── services/          # External services (Watson AI, file system)
│   ├── models/            # Pydantic data models
│   ├── ui/                # Flet UI components
│   ├── utils/             # Utility functions
│   └── templates/         # Documentation templates
├── config/                # Configuration files
├── tests/                 # Test suite
├── docs/                  # Project documentation
└── requirements.txt       # Python dependencies
```

## Data Models

### Core Models

- **FileInfo**: Complete file metadata, code structure, and metrics
- **Finding**: Code review findings with severity and classification
- **Suggestion**: Improvement suggestions with effort/impact analysis
- **FunctionalityGroup**: Related files grouped by purpose
- **Project**: Complete project analysis results

## Usage

### Basic Workflow

1. **Select Folders**: Choose one or more project directories to analyze
2. **Scan & Analyze**: The app scans files, parses code, and analyzes structure
3. **AI Enhancement**: Watson AI provides semantic understanding and insights
4. **Review Results**: View findings, suggestions, and documentation
5. **Export**: Save results as JSON or Markdown reports

### Features

#### Code Scanning
- Recursive directory traversal
- Gitignore-style pattern matching
- Language detection
- Dependency graph building

#### Code Analysis
- AST parsing for Python and JavaScript/TypeScript
- Complexity metrics (cyclomatic complexity, maintainability index)
- Import/export relationship tracking
- Framework and pattern detection

#### Code Review
- Static analysis (pylint, bandit, radon, mypy)
- AI-powered deep analysis
- Security vulnerability detection
- Best practice violations
- Finding classification by severity and type

#### Improvement Suggestions
- AI-generated recommendations
- Effort and impact estimation
- Priority scoring
- Implementation guidance
- Quick wins identification

#### Documentation
- Per-file documentation
- Functionality group documentation
- Index page with navigation
- AI-generated descriptions
- Code metrics and statistics

## Development Status

### ✅ Completed (Phase 2)

- [x] Project structure and configuration
- [x] Data models (Pydantic)
- [x] Configuration management
- [x] Logging system
- [x] Environment setup
- [x] File scanner engine
- [x] IBM Watson AI integration
- [x] AST parsers
- [x] UI components


### 📋 Planned

- [ ] Code review engine
- [ ] Suggestion engine
- [ ] Documentation generator
- [ ] Complete UI dashboard
- [ ] Testing suite
- [ ] Performance optimization

## Contributing

This project is under active development. Contributions, issues, and feature requests are welcome!

## License

[Add your license here]

## Acknowledgments

- IBM Watson AI for intelligent code analysis
- Flet framework for the modern UI
- All open-source libraries used in this project

---

**Version**: 1.0.0 (In Development)  
**Last Updated**: 2026-05-16
