import tempfile
from pathlib import Path

from src.core.orchestrator import AnalysisOrchestrator
from src.models.finding import Finding, Severity, FindingType, CodeLocation
from src.models.project import Project
from src.utils.config import Config


def test_phase5_suggestion_generation_updates_project_and_writes_roadmap():
    config = Config(Path("missing-config.yaml"))
    orchestrator = AnalysisOrchestrator(config)
    project_root = Path("/tmp/test-project")
    project = Project(
        id="test-project",
        name="test-project",
        root_paths=[project_root],
        description="Test project for Phase 5"
    )
    findings = [
        Finding(
            id="FIND-001",
            title="Hardcoded API key detected",
            description="API key found in source code",
            severity=Severity.CRITICAL,
            finding_type=FindingType.SECURITY,
            confidence=0.95,
            location=CodeLocation(
                file_path=Path("src/config.py"),
                line_start=10,
                line_end=10,
                code_snippet='API_KEY = "sk-1234567890"'
            ),
            message="Hardcoded credentials pose security risk",
            explanation="API keys should be stored in environment variables",
            recommendation="Move API key to environment variable",
            source="static_analyzer"
        ),
        Finding(
            id="FIND-002",
            title="Potential None dereference",
            description="Variable may be None when accessed",
            severity=Severity.HIGH,
            finding_type=FindingType.BUG,
            confidence=0.85,
            location=CodeLocation(
                file_path=Path("src/utils.py"),
                line_start=25,
                line_end=25,
                code_snippet="result = data.get('value').upper()"
            ),
            message="Potential AttributeError if 'value' key is missing",
            recommendation="Add None check before calling .upper()",
            source="static_analyzer"
        ),
        Finding(
            id="FIND-003",
            title="Inefficient list comprehension in loop",
            description="List comprehension inside loop causes O(n²) complexity",
            severity=Severity.MEDIUM,
            finding_type=FindingType.PERFORMANCE,
            confidence=0.80,
            location=CodeLocation(
                file_path=Path("src/processor.py"),
                line_start=45,
                line_end=47,
                code_snippet="for item in items:\n    results = [x for x in data if x.id == item.id]"
            ),
            message="Nested iteration causes performance issues",
            recommendation="Use dictionary lookup or set operations",
            source="static_analyzer"
        ),
        Finding(
            id="FIND-004",
            title="Missing docstring",
            description="Function lacks documentation",
            severity=Severity.LOW,
            finding_type=FindingType.DOCUMENTATION,
            confidence=0.90,
            location=CodeLocation(
                file_path=Path("src/helpers.py"),
                line_start=15,
                line_end=15
            ),
            message="Public function should have docstring",
            recommendation="Add docstring describing function purpose and parameters",
            source="pylint"
        ),
        Finding(
            id="FIND-005",
            title="SQL injection vulnerability",
            description="User input used directly in SQL query",
            severity=Severity.CRITICAL,
            finding_type=FindingType.SECURITY,
            confidence=0.92,
            location=CodeLocation(
                file_path=Path("src/database.py"),
                line_start=30,
                line_end=30,
                code_snippet=f'query = f"SELECT * FROM users WHERE id = {{user_id}}"'
            ),
            message="Unsanitized user input in SQL query",
            recommendation="Use parameterized queries",
            source="bandit"
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        result = orchestrator.generate_suggestions(
            findings=findings,
            project=project,
            output_dir=tmpdir,
            use_ai=False
        )

        output_path = Path(result['output_dir'])
        json_file = output_path / 'improvement-suggestions.json'
        md_file = output_path / 'IMPROVEMENT_ROADMAP.md'

        assert json_file.exists()
        assert md_file.exists()
        assert result['total_suggestions'] > 0
        assert project.suggestions == result['suggestions']
        assert project.suggestion_summary is not None
        assert project.suggestion_summary.total_suggestions == result['total_suggestions']

        roadmap = result['roadmap']
        assert roadmap['projectName'] == project.name
        assert 'summary' in roadmap
        assert 'recommendations' in roadmap
        assert 'allSuggestions' in roadmap
