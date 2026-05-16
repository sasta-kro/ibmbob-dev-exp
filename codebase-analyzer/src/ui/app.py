"""
Main Application

Flet-based desktop application for codebase analysis.
"""

from typing import Optional
import flet as ft
from ..core.orchestrator import AnalysisOrchestrator
from ..models.project import Project
from ..utils.config import Config
from .theme import AppTheme
from .pages import (
    HomePage,
    ScanPage,
    OverviewPage,
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
        self.current_page = "home"
        
        # Configure page
        self.page.title = "Codebase Analyzer"
        self.page.theme = AppTheme.get_light_theme()
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        
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
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Home"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SEARCH_OUTLINED,
                    selected_icon=ft.icons.SEARCH,
                    label="Scan"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Overview"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.BUG_REPORT_OUTLINED,
                    selected_icon=ft.icons.BUG_REPORT,
                    label="Findings"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.LIGHTBULB_OUTLINED,
                    selected_icon=ft.icons.LIGHTBULB,
                    label="Suggestions"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
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
        pages = ["home", "scan", "overview", "findings", "suggestions", "settings"]
        selected_index = e.control.selected_index
        
        if selected_index < len(pages):
            self.current_page = pages[selected_index]
            self.content_area.content = self._get_page_content(self.current_page)
            self.page.update()
    
    def _get_page_content(self, page_name: str) -> ft.Control:
        """Get content for a specific page"""
        if page_name == "home":
            return HomePage(
                on_new_analysis=self._start_new_analysis
            )
        
        elif page_name == "scan":
            return ScanPage(
                on_start_scan=self._perform_scan,
                on_cancel=self._cancel_scan
            )
        
        elif page_name == "overview":
            return OverviewPage(
                project=self.current_project,
                on_view_docs=lambda: self._navigate_to("docs"),
                on_view_findings=lambda: self._navigate_to("findings"),
                on_view_suggestions=lambda: self._navigate_to("suggestions")
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
        pages = ["home", "scan", "overview", "findings", "suggestions", "settings"]
        if page_name in pages:
            self.nav_rail.selected_index = pages.index(page_name)
            self.current_page = page_name
            self.content_area.content = self._get_page_content(page_name)
            self.page.update()
    
    def _start_new_analysis(self):
        """Start a new analysis"""
        self._navigate_to("scan")
    
    def _perform_scan(self, paths: list):
        """Perform codebase scan and analysis"""
        try:
            # This would integrate with the orchestrator
            # For now, just show a message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Starting analysis of {len(paths)} folder(s)..."),
                bgcolor=AppTheme.PRIMARY
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # TODO: Integrate with orchestrator
            # self.current_project = self.orchestrator.analyze_project(paths[0])
            
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                bgcolor=AppTheme.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
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
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Finding marked as resolved"),
            bgcolor=AppTheme.SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _ignore_finding(self, finding):
        """Ignore a finding"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Finding ignored"),
            bgcolor=AppTheme.INFO
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _accept_suggestion(self, suggestion):
        """Accept a suggestion"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Suggestion accepted"),
            bgcolor=AppTheme.SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _dismiss_suggestion(self, suggestion):
        """Dismiss a suggestion"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Suggestion dismissed"),
            bgcolor=AppTheme.INFO
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _save_settings(self, settings: dict):
        """Save application settings"""
        # TODO: Persist settings to config
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Settings saved successfully"),
            bgcolor=AppTheme.SUCCESS
        )
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    """Main entry point for Flet application"""
    CodebaseAnalyzerApp(page)


if __name__ == "__main__":
    ft.app(target=main)

# Made with Bob
