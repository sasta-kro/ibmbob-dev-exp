"""
Overview Page

Project overview with metrics, statistics, and charts.
"""

from typing import Optional
import flet as ft
from ...models.project import Project
from ..theme import AppTheme
from ..components import MetricCard, PieChart, BarChart
from ..utils import format_number, create_empty_state


class OverviewPage(ft.Container):
    """Overview page component"""
    
    def __init__(
        self,
        project: Optional[Project] = None,
        on_view_docs: Optional[callable] = None,
        on_view_findings: Optional[callable] = None,
        on_view_suggestions: Optional[callable] = None
    ):
        """
        Initialize overview page
        
        Args:
            project: Project data to display
            on_view_docs: Callback to view documentation
            on_view_findings: Callback to view findings
            on_view_suggestions: Callback to view suggestions
        """
        self.project = project
        self.on_view_docs = on_view_docs
        self.on_view_findings = on_view_findings
        self.on_view_suggestions = on_view_suggestions
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _build_content(self) -> ft.Column:
        """Build overview page content"""
        if not self.project:
            return ft.Column(
                controls=[
                    create_empty_state(
                        icon=ft.Icons.ANALYTICS,
                        title="No Project Loaded",
                        description="Start a new analysis to see project overview"
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        
        # Header
        header = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            self.project.name,
                            size=AppTheme.FONT_SIZE_TITLE,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        ft.Text(
                            f"Analyzed: {len(self.project.root_paths)} folder(s)",
                            size=AppTheme.FONT_SIZE_NORMAL,
                            color=AppTheme.TEXT_SECONDARY
                        )
                    ],
                    spacing=4,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Re-analyze",
                    icon_size=24
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        metrics_row = self._build_metrics_section()
        charts_section = self._build_charts_section()
        actions_section = self._build_actions_section()
        
        return ft.Column(
            controls=[
                header,
                ft.Container(height=AppTheme.SPACING_LARGE),
                metrics_row,
                ft.Container(height=AppTheme.SPACING_LARGE),
                charts_section,
                ft.Container(height=AppTheme.SPACING_LARGE),
                actions_section
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _build_metrics_section(self) -> ft.Row:
        """Build metrics cards section"""
        total_files = len(self.project.files)
        total_findings = len(self.project.findings) if self.project.findings else 0
        total_suggestions = len(self.project.suggestions) if self.project.suggestions else 0
        functionality_groups = (
            len(self.project.functionality_map.groups)
            if self.project.functionality_map
            else 0
        )
        
        critical_findings = sum(
            1 for f in (self.project.findings or [])
            if f.severity.value == "critical"
        )
        
        high_priority_suggestions = sum(
            1 for s in (self.project.suggestions or [])
            if s.priority_score >= 70
        )
        
        metrics = [
            MetricCard(
                title="Total Files",
                value=format_number(total_files),
                icon=ft.Icons.FOLDER,
                color=AppTheme.PRIMARY,
                subtitle=f"{functionality_groups} functionality groups"
            ),
            MetricCard(
                title="Code Findings",
                value=format_number(total_findings),
                icon=ft.Icons.BUG_REPORT,
                color=AppTheme.ERROR if critical_findings > 0 else AppTheme.WARNING,
                subtitle=f"{critical_findings} critical"
            ),
            MetricCard(
                title="Suggestions",
                value=format_number(total_suggestions),
                icon=ft.Icons.LIGHTBULB,
                color=AppTheme.SUCCESS,
                subtitle=f"{high_priority_suggestions} high priority"
            ),
            MetricCard(
                title="Languages",
                value=str(len(self.project.metrics.languages)),
                icon=ft.Icons.CODE,
                color=AppTheme.SECONDARY
            )
        ]
        
        return ft.Row(
            controls=metrics,
            spacing=16,
            wrap=True
        )
    
    def _build_charts_section(self) -> ft.Column:
        """Build charts section"""
        charts = []
        
        if self.project.metrics.languages:
            lang_chart = PieChart(
                title="Language Distribution",
                data=self.project.metrics.languages,
                colors={
                    "Python": AppTheme.PRIMARY,
                    "JavaScript": "#F7DF1E",
                    "TypeScript": "#3178C6",
                    "Java": "#007396",
                    "Go": "#00ADD8"
                }
            )
            charts.append(
                ft.Card(
                    content=lang_chart,
                    elevation=2
                )
            )
        
        if self.project.findings:
            severity_counts = {}
            for finding in self.project.findings:
                severity = finding.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            severity_chart = BarChart(
                title="Findings by Severity",
                data=severity_counts,
                color=AppTheme.ERROR
            )
            charts.append(
                ft.Card(
                    content=severity_chart,
                    elevation=2
                )
            )
        
        if self.project.findings:
            type_counts = {}
            for finding in self.project.findings:
                finding_type = finding.finding_type.value
                type_counts[finding_type] = type_counts.get(finding_type, 0) + 1
            
            type_chart = BarChart(
                title="Findings by Type",
                data=type_counts,
                color=AppTheme.WARNING
            )
            charts.append(
                ft.Card(
                    content=type_chart,
                    elevation=2
                )
            )
        
        if not charts:
            return ft.Container()
        
        return ft.Column(
            controls=[
                ft.Text(
                    "Analytics",
                    size=AppTheme.FONT_SIZE_XLARGE,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=charts,
                    spacing=16,
                    wrap=True
                )
            ],
            spacing=0
        )
    
    def _build_actions_section(self) -> ft.Column:
        """Build quick actions section"""
        actions = []
        
        if self.on_view_docs:
            actions.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.DESCRIPTION),
                            ft.Text("View Documentation")
                        ],
                        spacing=8
                    ),
                    on_click=lambda _: self.on_view_docs(),
                    style=ft.ButtonStyle(
                        padding=ft.Padding(
                            left=AppTheme.SPACING_LARGE,
                            right=AppTheme.SPACING_LARGE,
                            top=AppTheme.SPACING_MEDIUM,
                            bottom=AppTheme.SPACING_MEDIUM
                        )
                    )
                )
            )
        
        if self.on_view_findings:
            actions.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.BUG_REPORT),
                            ft.Text("View Findings")
                        ],
                        spacing=8
                    ),
                    on_click=lambda _: self.on_view_findings(),
                    style=ft.ButtonStyle(
                        padding=ft.Padding(
                            left=AppTheme.SPACING_LARGE,
                            right=AppTheme.SPACING_LARGE,
                            top=AppTheme.SPACING_MEDIUM,
                            bottom=AppTheme.SPACING_MEDIUM
                        )
                    )
                )
            )
        
        if self.on_view_suggestions:
            actions.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LIGHTBULB),
                            ft.Text("View Suggestions")
                        ],
                        spacing=8
                    ),
                    on_click=lambda _: self.on_view_suggestions(),
                    style=ft.ButtonStyle(
                        padding=ft.Padding(
                            left=AppTheme.SPACING_LARGE,
                            right=AppTheme.SPACING_LARGE,
                            top=AppTheme.SPACING_MEDIUM,
                            bottom=AppTheme.SPACING_MEDIUM
                        )
                    )
                )
            )
        
        if not actions:
            return ft.Container()
        
        return ft.Column(
            controls=[
                ft.Text(
                    "Quick Actions",
                    size=AppTheme.FONT_SIZE_XLARGE,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=actions,
                    spacing=16,
                    wrap=True
                )
            ],
            spacing=0
        )
    
    def refresh(self, project: Project):
        """Refresh the page with updated project data"""
        self.project = project
        self.content = self._build_content()
        self.update()

# Made with Bob
