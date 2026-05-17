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
from ..services.scan_history import ScanHistoryService
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
        self.scan_history = ScanHistoryService()
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
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = '#FFFFFF'
        self.page.padding = 0

        # Folder picker service
        self.folder_picker = ft.FilePicker()
        self.page.services.append(self.folder_picker)

        # Initialize UI
        self._setup_ui()

    def _show_snackbar(self, message: str, color: str = None):
        """Show a snackbar notification."""
        color = color or AppTheme.PRIMARY
        snackbar = ft.SnackBar(content=ft.Text(message, color="#FFFFFF"), bgcolor=color)
        self.page.show_dialog(snackbar)

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

    @property
    def _config_missing(self) -> bool:
        return not self.config.watson_api_key or not self.config.watson_project_id

    def _build_config_missing_page(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=AppTheme.WARNING, size=64),
                    ft.Container(height=16),
                    ft.Text(
                        "Configuration Required",
                        size=AppTheme.FONT_SIZE_TITLE,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "Watson API Key and Project ID must be configured before using the analyzer.",
                        size=AppTheme.FONT_SIZE_NORMAL,
                        color=AppTheme.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=24),
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SETTINGS, color=AppTheme.TEXT_ON_PRIMARY),
                                ft.Text("Go to Settings"),
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=lambda _: self._navigate_to("settings"),
                        style=ft.ButtonStyle(
                            bgcolor=AppTheme.PRIMARY,
                            color=AppTheme.TEXT_ON_PRIMARY,
                            padding=ft.Padding(left=32, right=32, top=16, bottom=16),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            expand=True,
        )

    def _get_page_content(self, page_name: str) -> ft.Control:
        """Get content for a specific page"""
        if page_name != "settings" and self._config_missing:
            return self._build_config_missing_page()

        if page_name == "home":
            return HomePage(
                on_new_analysis=self._start_new_analysis,
                recent_projects=self.scan_history.list_scans(),
                on_open_project=self._open_history_project
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
                config=self.config,
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

    def _open_history_project(self, project_data: dict):
        """Load a project from scan history and show overview."""
        project = self.scan_history.load_scan(project_data["id"])
        if project:
            self.current_project = project
            if project.output_path:
                self.documentation_path = project.output_path
            self._navigate_to("overview")
        else:
            self._show_snackbar("Could not load scan history", AppTheme.ERROR)

    async def _select_folder(self):
        """Open native folder picker dialog."""
        path = await self.folder_picker.get_directory_path(dialog_title="Select project folder")
        if path and self.active_scan_page:
            self.active_scan_page.add_path(path)

    def _perform_scan(self, paths: list, options: Optional[dict] = None):
        """Perform codebase scan and analysis"""
        options = options or self.settings
        try:
            self._show_snackbar(f"Starting analysis of {len(paths)} folder(s)...", AppTheme.PRIMARY)

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

            try:
                self.scan_history.save_scan(self.current_project)
            except Exception as save_err:
                print(f"[HISTORY] Failed to save scan: {save_err}")

            if self.active_scan_page:
                self.active_scan_page.is_scanning = False
                self.active_scan_page.update_progress("reviewing", 100, 100, "Complete")

            self._navigate_to("overview")

        except Exception as e:
            self._show_snackbar(f"Error: {str(e)}", AppTheme.ERROR)
            if self.active_scan_page:
                self.active_scan_page.is_scanning = False
                self.active_scan_page.content = self.active_scan_page._build_content()
                self.active_scan_page.update()

    def _handle_analysis_progress(self, message: str, current: int, total: int):
        """Route analysis progress to the scan page."""
        if not self.active_scan_page:
            return

        normalized = message.lower()
        if any(k in normalized for k in ("scan", "found", "exploring", "discover")):
            stage = "scanning"
        elif any(k in normalized for k in ("document", "writing doc", "api reference", "generating doc")):
            stage = "documenting"
        elif any(k in normalized for k in ("review", "bug", "vulnerabilit", "static analysis", "finding")):
            stage = "reviewing"
        else:
            stage = "analyzing"

        self.active_scan_page.update_progress(stage, current, total, message)

    def _cancel_scan(self):
        """Cancel ongoing scan"""
        self._show_snackbar("Scan cancelled", AppTheme.WARNING)

    def _resolve_finding(self, finding):
        """Mark finding as resolved"""
        finding.is_resolved = True
        if self.current_project:
            self.current_project._update_finding_summary()
            self._refresh_current_page()
        self._show_snackbar("Finding marked as resolved", AppTheme.SUCCESS)

    def _ignore_finding(self, finding):
        """Ignore a finding"""
        finding.is_false_positive = True
        if self.current_project:
            self.current_project._update_finding_summary()
            self._refresh_current_page()
        self._show_snackbar("Finding ignored", AppTheme.INFO)

    def _accept_suggestion(self, suggestion):
        """Accept a suggestion"""
        suggestion.status = SuggestionStatus.IN_PROGRESS
        if self.current_project:
            self.current_project._update_suggestion_summary()
            self._refresh_current_page()
        self._show_snackbar("Suggestion accepted", AppTheme.SUCCESS)

    def _dismiss_suggestion(self, suggestion):
        """Dismiss a suggestion"""
        suggestion.status = SuggestionStatus.REJECTED
        if self.current_project:
            self.current_project._update_suggestion_summary()
            self._refresh_current_page()
        self._show_snackbar("Suggestion dismissed", AppTheme.INFO)

    def _save_settings(self, settings: dict):
        """Save application settings"""
        self.settings.update({
            "enable_ai": settings.get("enable_ai", True),
            "generate_docs": settings.get("generate_docs", True),
            "perform_review": settings.get("perform_review", True),
            "generate_suggestions": settings.get("generate_suggestions", True),
            "theme": settings.get("theme", "light"),
        })
        self._show_snackbar("Settings saved successfully", AppTheme.SUCCESS)

    def _refresh_current_page(self):
        """Refresh the active page content."""
        self.content_area.content = self._get_page_content(self.current_page)
        self.page.update()


def main(page: ft.Page):
    """Main entry point for Flet application"""
    CodebaseAnalyzerApp(page)


def run_app(config=None):
    """Run the Flet application."""
    ft.run(main)


if __name__ == "__main__":
    ft.run(main)

# Made with Bob
