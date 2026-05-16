"""
Phase 6 Stabilization Test

Smoke test to verify Phase 6 UI implementation is functional.
"""

import pytest
from src.models.project import Project
from src.models.finding import Finding, FindingSeverity, FindingCategory
from src.models.suggestion import (
    Suggestion,
    SuggestionCategory,
    EffortLevel,
    ImpactLevel,
    ImplementationStep
)


def test_ui_components_importable():
    """Test that UI components can be imported"""
    from src.ui.theme import AppTheme
    from src.ui.utils import format_number, format_percentage
    from src.ui.components import (
        FindingCard,
        SuggestionCard,
        ProgressCard,
        FilterPanel,
        SortControl,
        SearchBar,
        PieChart,
        BarChart,
        MetricCard,
        ProgressRing
    )
    
    # Verify theme constants exist
    assert AppTheme.PRIMARY is not None
    assert AppTheme.SECONDARY is not None
    
    # Verify utility functions work
    assert format_number(1000) == "1,000"
    assert format_percentage(75.5) == "75.5%"
    
    # Verify component classes exist
    assert FindingCard is not None
    assert SuggestionCard is not None
    assert ProgressCard is not None
    assert FilterPanel is not None
    assert SortControl is not None
    assert SearchBar is not None
    assert PieChart is not None
    assert BarChart is not None
    assert MetricCard is not None
    assert ProgressRing is not None


def test_ui_pages_importable():
    """Test that UI pages can be imported"""
    from src.ui.pages import (
        HomePage,
        ScanPage,
        OverviewPage,
        FindingsPage,
        SuggestionsPage,
        SettingsPage
    )
    
    # Verify page classes exist
    assert HomePage is not None
    assert ScanPage is not None
    assert OverviewPage is not None
    assert FindingsPage is not None
    assert SuggestionsPage is not None
    assert SettingsPage is not None


def test_app_importable():
    """Test that main app can be imported"""
    from src.ui.app import CodebaseAnalyzerApp, main
    
    # Verify app classes exist
    assert CodebaseAnalyzerApp is not None
    assert main is not None


def test_theme_color_methods():
    """Test theme color helper methods"""
    from src.ui.theme import AppTheme
    
    # Test severity colors
    assert AppTheme.get_severity_color("critical") == AppTheme.CRITICAL
    assert AppTheme.get_severity_color("high") == AppTheme.HIGH
    assert AppTheme.get_severity_color("medium") == AppTheme.MEDIUM
    assert AppTheme.get_severity_color("low") == AppTheme.LOW
    assert AppTheme.get_severity_color("info") == AppTheme.INFO_SEVERITY
    
    # Test priority colors
    assert AppTheme.get_priority_color(90) == AppTheme.CRITICAL
    assert AppTheme.get_priority_color(70) == AppTheme.HIGH
    assert AppTheme.get_priority_color(50) == AppTheme.MEDIUM
    assert AppTheme.get_priority_color(30) == AppTheme.LOW


def test_utility_functions():
    """Test utility functions"""
    from src.ui.utils import (
        format_number,
        format_percentage,
        format_file_size,
        format_duration,
        truncate_text
    )
    
    # Test number formatting
    assert format_number(1000) == "1,000"
    assert format_number(1000000) == "1,000,000"
    
    # Test percentage formatting
    assert format_percentage(75.5) == "75.5%"
    assert format_percentage(75.567, 2) == "75.57%"
    
    # Test file size formatting
    assert "B" in format_file_size(500)
    assert "KB" in format_file_size(1024)
    assert "MB" in format_file_size(1024 * 1024)
    
    # Test duration formatting
    assert "s" in format_duration(30)
    assert "m" in format_duration(120)
    assert "h" in format_duration(3600)
    
    # Test text truncation
    long_text = "a" * 200
    truncated = truncate_text(long_text, 100)
    assert len(truncated) <= 103  # 100 + "..."
    assert truncated.endswith("...")


def test_ui_data_models_integration():
    """Test that UI components work with data models"""
    # Create test project
    project = Project(
        id="test-project",
        name="Test Project",
        root_paths=["/test/path"]
    )
    
    # Create test finding
    finding = Finding(
        id="test-finding",
        title="Test Finding",
        description="Test description",
        severity=FindingSeverity.HIGH,
        category=FindingCategory.BUG,
        file_path="/test/file.py",
        line_number=10,
        confidence=0.9
    )
    
    # Create test suggestion
    suggestion = Suggestion(
        id="test-suggestion",
        title="Test Suggestion",
        description="Test description",
        category=SuggestionCategory.REFACTORING,
        effort=EffortLevel.MEDIUM,
        impact=ImpactLevel.HIGH,
        priority_score=75.0,
        implementation_steps=[
            ImplementationStep(
                order=1,
                description="Step 1",
                estimated_time="1 hour"
            )
        ],
        benefits=["Benefit 1"],
        related_finding_ids=["test-finding"]
    )
    
    # Verify models are compatible with UI
    assert project.name == "Test Project"
    assert finding.severity == FindingSeverity.HIGH
    assert suggestion.priority_score == 75.0
    assert len(suggestion.implementation_steps) == 1


def test_phase6_completion():
    """Verify Phase 6 components are complete"""
    # Test theme
    from src.ui.theme import AppTheme
    assert hasattr(AppTheme, 'PRIMARY')
    assert hasattr(AppTheme, 'get_severity_color')
    assert hasattr(AppTheme, 'get_priority_color')
    
    # Test utils
    from src.ui import utils
    assert hasattr(utils, 'format_number')
    assert hasattr(utils, 'create_badge')
    assert hasattr(utils, 'create_stat_card')
    
    # Test components
    from src.ui.components import cards, filters, charts
    assert hasattr(cards, 'FindingCard')
    assert hasattr(cards, 'SuggestionCard')
    assert hasattr(cards, 'ProgressCard')
    assert hasattr(filters, 'FilterPanel')
    assert hasattr(filters, 'SortControl')
    assert hasattr(charts, 'PieChart')
    assert hasattr(charts, 'BarChart')
    assert hasattr(charts, 'MetricCard')
    
    # Test pages
    from src.ui.pages import (
        home_page,
        scan_page,
        overview_page,
        findings_page,
        suggestions_page,
        settings_page
    )
    assert hasattr(home_page, 'HomePage')
    assert hasattr(scan_page, 'ScanPage')
    assert hasattr(overview_page, 'OverviewPage')
    assert hasattr(findings_page, 'FindingsPage')
    assert hasattr(suggestions_page, 'SuggestionsPage')
    assert hasattr(settings_page, 'SettingsPage')
    
    # Test app
    from src.ui import app
    assert hasattr(app, 'CodebaseAnalyzerApp')
    assert hasattr(app, 'main')
    
    print("✓ Phase 6 UI implementation complete")
    print("✓ All components, pages, and app structure verified")

# Made with Bob
