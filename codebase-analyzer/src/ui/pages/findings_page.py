"""
Findings Page

Display and filter code review findings.
"""

from typing import List, Optional, Callable
import flet as ft
from ...models.finding import Finding
from ..theme import AppTheme
from ..components import FindingCard, FilterPanel, SortControl
from ..utils import create_empty_state


class FindingsPage(ft.Container):
    """Findings page component"""
    
    def __init__(
        self,
        findings: Optional[List[Finding]] = None,
        on_resolve: Optional[Callable] = None,
        on_ignore: Optional[Callable] = None
    ):
        """
        Initialize findings page
        
        Args:
            findings: List of findings to display
            on_resolve: Callback when finding is resolved
            on_ignore: Callback when finding is ignored
        """
        self.all_findings = findings or []
        self.filtered_findings = self.all_findings.copy()
        self.on_resolve = on_resolve
        self.on_ignore = on_ignore
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _build_content(self) -> ft.Row:
        """Build findings page content"""
        if not self.all_findings:
            return ft.Row(
                controls=[
                    create_empty_state(
                        icon=ft.Icons.CHECK_CIRCLE,
                        title="No Findings",
                        description="No code review findings to display"
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        
        # Filter panel
        filter_options = {
            "severity": ["critical", "high", "medium", "low", "info"],
            "type": ["bug", "security", "performance", "style", "maintainability", "documentation"]
        }
        
        filter_panel = FilterPanel(
            filters=filter_options,
            on_filter_change=self._on_filter_change,
            search_enabled=True,
            on_search=self._on_search
        )
        
        # Main content area
        main_content = self._build_findings_list()
        
        return ft.Row(
            controls=[
                ft.Container(
                    content=filter_panel,
                    width=300
                ),
                ft.VerticalDivider(width=1, color=AppTheme.DIVIDER_COLOR),
                ft.Container(
                    content=main_content,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
    
    def _build_findings_list(self) -> ft.Column:
        """Build findings list"""
        # Header with count and sort
        header = ft.Row(
            controls=[
                ft.Text(
                    f"Findings ({len(self.filtered_findings)})",
                    size=AppTheme.FONT_SIZE_TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    expand=True
                ),
                SortControl(
                    options=["Severity", "Category", "File"],
                    on_sort_change=self._on_sort_change,
                    default_option="Severity"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Findings cards
        if not self.filtered_findings:
            findings_content = create_empty_state(
                icon=ft.Icons.FILTER_ALT_OFF,
                title="No Matching Findings",
                description="Adjust filters to broaden the result set"
            )
        else:
            finding_cards = [
                FindingCard(
                    finding=finding,
                    on_resolve=self.on_resolve,
                    on_ignore=self.on_ignore
                )
                for finding in self.filtered_findings
            ]
            
            findings_content = ft.ListView(
                controls=finding_cards,
                spacing=12,
                padding=AppTheme.SPACING_MEDIUM,
                expand=True
            )
        
        return ft.Column(
            controls=[
                header,
                ft.Container(height=AppTheme.SPACING_LARGE),
                findings_content
            ],
            spacing=0,
            expand=True
        )
    
    def _on_filter_change(self, filters: dict):
        """Handle filter changes"""
        self.filtered_findings = self.all_findings.copy()
        
        if filters.get("severity"):
            self.filtered_findings = [
                f for f in self.filtered_findings
                if f.severity.value in filters["severity"]
            ]
        
        if filters.get("type"):
            self.filtered_findings = [
                f for f in self.filtered_findings
                if f.finding_type.value in filters["type"]
            ]
        
        self.content = self._build_content()
        self.update()
    
    def _on_search(self, query: str):
        """Handle search query"""
        if not query:
            self.filtered_findings = self.all_findings.copy()
        else:
            query_lower = query.lower()
            self.filtered_findings = [
                f for f in self.all_findings
                if query_lower in f.title.lower() or
                   query_lower in f.description.lower() or
                   query_lower in str(f.location.file_path).lower()
            ]
        
        self.content = self._build_content()
        self.update()
    
    def _on_sort_change(self, option: str, ascending: bool):
        """Handle sort changes"""
        if option == "Severity":
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            self.filtered_findings.sort(
                key=lambda f: severity_order.get(f.severity.value, 5),
                reverse=not ascending
            )
        elif option == "Category":
            self.filtered_findings.sort(
                key=lambda f: f.finding_type.value,
                reverse=not ascending
            )
        elif option == "File":
            self.filtered_findings.sort(
                key=lambda f: str(f.location.file_path),
                reverse=not ascending
            )
        
        self.content = self._build_content()
        self.update()
    
    def refresh(self, findings: List[Finding]):
        """Refresh with new findings"""
        self.all_findings = findings
        self.filtered_findings = findings.copy()
        self.content = self._build_content()
        self.update()

# Made with Bob
