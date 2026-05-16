from pathlib import Path

import flet as ft

from src.models.finding import CodeLocation, Finding, FindingType, Severity
from src.models.project import Project
from src.models.suggestion import (
    EffortLevel,
    ImpactLevel,
    ImplementationStep,
    Suggestion,
    SuggestionCategory,
    SuggestionStatus
)


class FakePage:
    def __init__(self):
        self.overlay = []
        self.controls = []
        self.update_count = 0

    def add(self, control):
        self.controls.append(control)

    def update(self):
        self.update_count += 1

    def show_dialog(self, dialog):
        pass


def make_finding() -> Finding:
    return Finding(
        id="finding-1",
        title="Unsafe query",
        description="User input is used in a SQL query",
        severity=Severity.HIGH,
        finding_type=FindingType.SECURITY,
        confidence=0.9,
        location=CodeLocation(
            file_path=Path("src/database.py"),
            line_start=12,
            line_end=12,
            code_snippet="cursor.execute(query)"
        ),
        message="Parameterized queries should be used",
        recommendation="Use query parameters",
        source="static_analyzer"
    )


def make_suggestion() -> Suggestion:
    return Suggestion(
        id="suggestion-1",
        title="Use parameterized queries",
        description="Replace string-built SQL with query parameters",
        category=SuggestionCategory.SECURITY,
        effort=EffortLevel.LOW,
        impact=ImpactLevel.HIGH,
        priority_score=90,
        related_files=[Path("src/database.py")],
        related_findings=["finding-1"],
        rationale="Parameterized queries reduce injection risk",
        benefits=["Reduced security risk"],
        implementation_steps=[
            ImplementationStep(
                order=1,
                description="Replace string interpolation with query parameters",
                estimated_time="30 minutes"
            )
        ],
        source="static_analyzer",
        confidence=0.9
    )


def make_project() -> Project:
    project = Project(
        id="project-1",
        name="Test Project",
        root_paths=[Path("/tmp/test-project")]
    )
    project.metrics.languages = {"python": 3}
    project.findings = [make_finding()]
    project.suggestions = [make_suggestion()]
    project._update_finding_summary()
    project._update_suggestion_summary()
    return project


def test_ui_components_import_and_render_with_real_models():
    from src.ui.components import (
        BarChart,
        FindingCard,
        FilterPanel,
        MetricCard,
        PieChart,
        ProgressCard,
        ProgressRing,
        SearchBar,
        SortControl,
        SuggestionCard
    )
    from src.ui.theme import AppTheme
    from src.ui.utils import format_number, format_percentage
    
    assert AppTheme.get_severity_color("critical") == AppTheme.CRITICAL
    assert AppTheme.get_priority_color(90) == AppTheme.CRITICAL
    assert format_number(1000) == "1,000"
    assert format_percentage(75.5) == "75.5%"
    
    FindingCard(make_finding(), expanded=True)
    SuggestionCard(make_suggestion(), expanded=True)
    ProgressCard("Scan", current=1, total=2, status="Running")
    FilterPanel({"severity": ["high"]}, on_filter_change=lambda _: None)
    SortControl(["Severity"], on_sort_change=lambda *_: None)
    SearchBar(on_search=lambda _: None)
    PieChart("Languages", {"python": 3})
    BarChart("Findings", {"security": 1})
    MetricCard("Files", "3", ft.Icons.FOLDER)
    ProgressRing(50)


def test_ui_pages_import_and_render_with_real_project(tmp_path):
    from src.ui.pages import (
        DocumentationPage,
        FindingsPage,
        HomePage,
        OverviewPage,
        ScanPage,
        SettingsPage,
        SuggestionsPage
    )
    
    project = make_project()
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "PROJECT_OVERVIEW.md").write_text("# Project Overview\n", encoding="utf-8")
    
    HomePage(on_new_analysis=lambda: None)
    ScanPage(on_start_scan=lambda *_: None)
    OverviewPage(project=project)
    DocumentationPage(project=project, docs_dir=docs_dir)
    FindingsPage(findings=project.findings)
    SuggestionsPage(suggestions=project.suggestions)
    SettingsPage(on_save=lambda _: None)


def test_findings_and_suggestions_use_real_model_fields():
    from src.ui.pages import FindingsPage, SuggestionsPage
    
    findings_page = FindingsPage(findings=[make_finding()])
    findings_page.update = lambda: None
    findings_page._on_filter_change({"type": ["security"]})
    findings_page._on_search("database")
    findings_page._on_sort_change("File", ascending=True)
    assert len(findings_page.filtered_findings) == 1
    
    suggestions_page = SuggestionsPage(suggestions=[make_suggestion()])
    suggestions_page.update = lambda: None
    suggestions_page._on_filter_change({"category": ["security"], "effort": ["low"]})
    suggestions_page._on_search("parameterized")
    suggestions_page._on_sort_change("Priority", ascending=False)
    assert len(suggestions_page.filtered_suggestions) == 1


def test_app_has_documentation_route_and_status_actions():
    from src.ui.app import CodebaseAnalyzerApp
    
    fake_page = FakePage()
    app = CodebaseAnalyzerApp(fake_page)
    project = make_project()
    app.current_project = project
    
    assert "docs" in app.page_order
    app._navigate_to("docs")
    assert app.current_page == "docs"
    
    finding = project.findings[0]
    suggestion = project.suggestions[0]
    
    app._resolve_finding(finding)
    assert finding.is_resolved is True
    assert project.finding_summary.resolved_count == 1
    
    app._ignore_finding(finding)
    assert finding.is_false_positive is True
    assert project.finding_summary.false_positive_count == 1
    
    app._accept_suggestion(suggestion)
    assert suggestion.status == SuggestionStatus.IN_PROGRESS
    
    app._dismiss_suggestion(suggestion)
    assert suggestion.status == SuggestionStatus.REJECTED
    assert project.suggestion_summary.by_status[SuggestionStatus.REJECTED] == 1


def test_scan_page_tracks_paths_and_options():
    from src.ui.pages import ScanPage
    
    captured = {}
    page = ScanPage(
        on_start_scan=lambda paths, options: captured.update(
            {"paths": paths, "options": options}
        )
    )
    page.update = lambda: None
    page.add_path("/tmp/test-project")
    page._update_option("enable_ai", False)
    page._start_analysis(None)
    
    assert captured["paths"] == ["/tmp/test-project"]
    assert captured["options"]["enable_ai"] is False
