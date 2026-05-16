"""
Main Application

Flet-based desktop application for codebase analysis.
"""

from pathlib import Path
from typing import Optional
import flet as ft
from ..core.orchestrator import AnalysisOrchestrator
from ..models.project import Project
from ..models.suggestion import SuggestionStatus
from ..utils.config import Config
from .theme import AppTheme
from .pages import (
    HomePage,
    ScanPage,
    OverviewPage,
    DocumentationPage,
    FindingsPage,
    SuggestionsPage,
    SettingsPage
)


class CodebaseAnalyzerApp:
    """Main application class"""
    
    def __init__(self, page: ft.Page):
        """
        Initialize application
        
        Args:
            page: Flet page instance
        """
        self.page = page
        self.config = Config()
        self.orchestrator = AnalysisOrchestrator(self.config)
        self.current_project: Optional[Project] = None
        self.documentation_path: Optional[Path] = None
        self.current_page = "home"
        self.page_order = [
            "home",
            "scan",
            "overview",
            "docs",
            "findings",
            "suggestions",
            "settings"
        ]
        self.active_scan_page: Optional[ScanPage] = None
        self.settings = {
            "enable_ai": True,
            "generate_docs": True,
            "perform_review": True,
            "generate_suggestions": True,
            "theme": "light"
        }
        
        # Configure page
        self.page.title = "Codebase Analyzer"
        self.page.theme = AppTheme.get_light_theme()
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.folder_picker = ft.FilePicker()
        if hasattr(self.page, "overlay"):
            self.page.overlay.append(self.folder_picker)
        
        # Initialize UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout"""
        # Navigation rail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SEARCH_OUTLINED,
                    selected_icon=ft.Icons.SEARCH,
                    label="Scan"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Overview"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    selected_icon=ft.Icons.DESCRIPTION,
                    label="Docs"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BUG_REPORT_OUTLINED,
                    selected_icon=ft.Icons.BUG_REPORT,
                    label="Findings"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIGHTBULB_OUTLINED,
                    selected_icon=ft.Icons.LIGHTBULB,
                    label="Suggestions"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings"
                )
            ],
            on_change=self._on_nav_change
        )
        
        # Content area
        self.content_area = ft.Container(
            content=self._get_page_content("home"),
            expand=True
        )
        
        # Main layout
        main_layout = ft.Row(
            controls=[
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area
            ],
            spacing=0,
            expand=True
        )
        
        self.page.add(main_layout)
    
    def _on_nav_change(self, e):
        """Handle navigation changes"""
        selected_index = e.control.selected_index
        
        if selected_index < len(self.page_order):
            self.current_page = self.page_order[selected_index]
            self.content_area.content = self._get_page_content(self.current_page)
            self.page.update()
    
    def _get_page_content(self, page_name: str) -> ft.Control:
        """Get content for a specific page"""
        if page_name == "home":
            return HomePage(
                on_new_analysis=self._start_new_analysis
            )
        
        elif page_name == "scan":
            self.active_scan_page = ScanPage(
                on_start_scan=self._perform_scan,
                on_select_folder=self._select_folder,
                on_cancel=self._cancel_scan
            )
            self.active_scan_page.option_values.update(self.settings)
            return self.active_scan_page
        
        elif page_name == "overview":
            return OverviewPage(
                project=self.current_project,
                on_view_docs=lambda: self._navigate_to("docs"),
                on_view_findings=lambda: self._navigate_to("findings"),
                on_view_suggestions=lambda: self._navigate_to("suggestions")
            )
        
        elif page_name == "docs":
            return DocumentationPage(
                project=self.current_project,
                docs_dir=self.documentation_path
            )
        
        elif page_name == "findings":
            findings = self.current_project.findings if self.current_project else []
            return FindingsPage(
                findings=findings,
                on_resolve=self._resolve_finding,
                on_ignore=self._ignore_finding
            )
        
        elif page_name == "suggestions":
            suggestions = self.current_project.suggestions if self.current_project else []
            return SuggestionsPage(
                suggestions=suggestions,
                on_accept=self._accept_suggestion,
                on_dismiss=self._dismiss_suggestion
            )
        
        elif page_name == "settings":
            return SettingsPage(
                on_save=self._save_settings
            )
        
        return ft.Container()
    
    def _navigate_to(self, page_name: str):
        """Navigate to a specific page"""
        if page_name in self.page_order:
            self.nav_rail.selected_index = self.page_order.index(page_name)
            self.current_page = page_name
            self.content_area.content = self._get_page_content(page_name)
            self.page.update()
    
    def _start_new_analysis(self):
        """Start a new analysis"""
        self._navigate_to("scan")
    
    def _select_folder(self):
        """Open the folder picker."""
        selected_path = self.folder_picker.get_directory_path()
        if selected_path and self.active_scan_page:
            self.active_scan_page.add_path(selected_path)
    
    def _perform_scan(self, paths: list, options: Optional[dict] = None):
        """Perform codebase scan and analysis"""
        options = options or self.settings
        try:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Starting analysis of {len(paths)} folder(s)..."),
                bgcolor=AppTheme.PRIMARY
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            project_path = Path(paths[0])
            output_root = project_path / ".codebase-analyzer"
            output_root.mkdir(parents=True, exist_ok=True)
            
            self.orchestrator.set_progress_callback(self._handle_analysis_progress)
            self.current_project = self.orchestrator.analyze_project(
                str(project_path),
                use_ai=options.get("enable_ai", False)
            )
            
            if options.get("generate_docs", True):
                self.documentation_path = self.orchestrator.generate_documentation(
                    self.current_project,
                    output_dir=str(output_root / "docs")
                )
                self.current_project.output_path = self.documentation_path
            
            if options.get("perform_review", True):
                self.orchestrator.review_project(
                    self.current_project,
                    output_dir=str(output_root / "review"),
                    enable_ai=options.get("enable_ai", False)
                )
            
            if options.get("generate_suggestions", True) and self.current_project.findings:
                self.orchestrator.generate_suggestions(
                    self.current_project.findings,
                    self.current_project,
                    output_dir=str(output_root / "suggestions"),
                    use_ai=options.get("enable_ai", False)
                )
            
            if self.active_scan_page:
                self.active_scan_page.is_scanning = False
                self.active_scan_page.update_progress("reviewing", 100, 100, "Complete")
            
            self._navigate_to("overview")
            
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                bgcolor=AppTheme.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
            if self.active_scan_page:
                self.active_scan_page.is_scanning = False
                self.active_scan_page.content = self.active_scan_page._build_content()
                self.active_scan_page.update()
    
    def _handle_analysis_progress(self, message: str, current: int, total: int):
        """Route analysis progress to the scan page."""
        if not self.active_scan_page:
            return
        
        normalized_message = message.lower()
        if "scan" in normalized_message:
            stage = "scanning"
        elif "document" in normalized_message:
            stage = "documenting"
        elif "review" in normalized_message:
            stage = "reviewing"
        else:
            stage = "analyzing"
        
        self.active_scan_page.update_progress(stage, current, total, message)
    
    def _cancel_scan(self):
        """Cancel ongoing scan"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Scan cancelled"),
            bgcolor=AppTheme.WARNING
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _resolve_finding(self, finding):
        """Mark finding as resolved"""
        finding.is_resolved = True
        if self.current_project:
            self.current_project._update_finding_summary()
            self._refresh_current_page()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Finding marked as resolved"),
            bgcolor=AppTheme.SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _ignore_finding(self, finding):
        """Ignore a finding"""
        finding.is_false_positive = True
        if self.current_project:
            self.current_project._update_finding_summary()
            self._refresh_current_page()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Finding ignored"),
            bgcolor=AppTheme.INFO
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _accept_suggestion(self, suggestion):
        """Accept a suggestion"""
        suggestion.status = SuggestionStatus.IN_PROGRESS
        if self.current_project:
            self.current_project._update_suggestion_summary()
            self._refresh_current_page()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Suggestion accepted"),
            bgcolor=AppTheme.SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _dismiss_suggestion(self, suggestion):
        """Dismiss a suggestion"""
        suggestion.status = SuggestionStatus.REJECTED
        if self.current_project:
            self.current_project._update_suggestion_summary()
            self._refresh_current_page()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Suggestion dismissed"),
            bgcolor=AppTheme.INFO
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _save_settings(self, settings: dict):
        """Save application settings"""
        self.settings.update(settings)
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully"),
            bgcolor=AppTheme.SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _refresh_current_page(self):
        """Refresh the active page content."""
        self.content_area.content = self._get_page_content(self.current_page)


def main(page: ft.Page):
    """Main entry point for Flet application"""
    CodebaseAnalyzerApp(page)


if __name__ == "__main__":
    ft.app(target=main)

# Made with Bob
