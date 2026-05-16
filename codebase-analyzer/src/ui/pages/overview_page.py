"""
Overview Page — project metrics, statistics, and charts.
"""

from typing import Optional
import flet as ft
from ...models.project import Project
from ..theme import AppTheme
from ..components import MetricCard, PieChart, BarChart
from ..utils import format_number, create_empty_state, create_stacked_bar

SEVERITY_COLORS = {
    "critical": AppTheme.CRITICAL, "high": AppTheme.HIGH, "medium": AppTheme.MEDIUM,
    "low": AppTheme.LOW, "info": AppTheme.INFO_SEVERITY,
}
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
    "Java": "#B07219", "Go": "#00ADD8", "Ruby": "#CC342D", "PHP": "#4F5D95",
    "C": "#555555", "C++": "#F34B7D", "Rust": "#DEA584", "Swift": "#FA7343",
    "HTML": "#E34F26", "CSS": "#1572B6", "SQL": "#336791", "Shell": "#4EAA25",
}


class OverviewPage(ft.Container):

    def __init__(
        self,
        project: Optional[Project] = None,
        on_view_docs: Optional[callable] = None,
        on_view_findings: Optional[callable] = None,
        on_view_suggestions: Optional[callable] = None
    ):
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
        if not self.project:
            return ft.Column(controls=[
                create_empty_state(icon=ft.Icons.ANALYTICS, title="No Project Loaded",
                                   description="Start a new analysis to see project overview")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        p = self.project
        m = p.metrics

        # Header
        header_items = [
            ft.Column(controls=[
                ft.Text(p.name, size=AppTheme.FONT_SIZE_TITLE, weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY),
                ft.Text(p.description or f"Analyzed: {len(p.root_paths)} folder(s)",
                        size=AppTheme.FONT_SIZE_NORMAL, color=AppTheme.TEXT_SECONDARY),
            ], spacing=4, expand=True),
        ]

        # Framework chips
        fw_chips = []
        if hasattr(m, 'frameworks') and m.frameworks:
            for fw in m.frameworks[:8]:
                fw_chips.append(ft.Container(
                    content=ft.Text(fw, size=11, color=AppTheme.PRIMARY, weight=ft.FontWeight.BOLD),
                    border=ft.Border.all(1, AppTheme.PRIMARY), border_radius=12,
                    padding=ft.Padding(left=10, right=10, top=3, bottom=3),
                ))

        header = ft.Column(controls=[
            ft.Row(controls=header_items, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(controls=fw_chips, spacing=6, wrap=True) if fw_chips else ft.Container(),
        ], spacing=8)

        # Metrics — two rows
        total_files = len(p.files)
        total_findings = len(p.findings) if p.findings else 0
        total_suggestions = len(p.suggestions) if p.suggestions else 0
        func_groups = len(p.functionality_map.groups) if p.functionality_map else 0

        critical = sum(1 for f in (p.findings or []) if f.severity.value == "critical")
        high_pri = sum(1 for s in (p.suggestions or []) if s.priority_score >= 70)
        quick_wins = sum(1 for s in (p.suggestions or [])
                         if s.effort.value == "low" and s.impact.value == "high")

        row1 = ft.Row(controls=[
            MetricCard(title="Files", value=format_number(total_files),
                       icon=ft.Icons.FOLDER, color=AppTheme.PRIMARY,
                       subtitle=f"{func_groups} groups"),
            MetricCard(title="Lines of Code", value=format_number(m.total_lines),
                       icon=ft.Icons.CODE, color="#6A1B9A"),
            MetricCard(title="Functions", value=format_number(m.total_functions),
                       icon=ft.Icons.FUNCTIONS, color="#00695C"),
            MetricCard(title="Classes", value=format_number(m.total_classes),
                       icon=ft.Icons.CLASS_, color="#E65100"),
        ], spacing=12, wrap=True)

        row2 = ft.Row(controls=[
            MetricCard(title="Findings", value=format_number(total_findings),
                       icon=ft.Icons.BUG_REPORT,
                       color=AppTheme.ERROR if critical > 0 else AppTheme.WARNING,
                       subtitle=f"{critical} critical"),
            MetricCard(title="Suggestions", value=format_number(total_suggestions),
                       icon=ft.Icons.LIGHTBULB, color=AppTheme.SUCCESS,
                       subtitle=f"{quick_wins} quick wins"),
            MetricCard(title="Languages", value=str(len(m.languages)),
                       icon=ft.Icons.LANGUAGE, color=AppTheme.SECONDARY),
            MetricCard(title="Avg Complexity",
                       value=f"{m.average_complexity:.1f}" if m.average_complexity else "N/A",
                       icon=ft.Icons.SPEED, color="#C62828"),
        ], spacing=12, wrap=True)

        # Severity breakdown bar
        severity_section = ft.Container()
        if p.findings:
            sev_counts = {}
            for f in p.findings:
                s = f.severity.value
                sev_counts[s] = sev_counts.get(s, 0) + 1

            labels = []
            for sev in ["critical", "high", "medium", "low", "info"]:
                c = sev_counts.get(sev, 0)
                if c > 0:
                    labels.append(ft.Row(controls=[
                        ft.Container(width=8, height=8, bgcolor=SEVERITY_COLORS.get(sev, "#999"),
                                     border_radius=4),
                        ft.Text(f"{sev.capitalize()} ({c})", size=11, color=AppTheme.TEXT_SECONDARY),
                    ], spacing=4))

            severity_section = ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Findings by Severity", size=14, weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY),
                    create_stacked_bar(sev_counts, SEVERITY_COLORS, height=12),
                    ft.Row(controls=labels, spacing=12, wrap=True),
                ], spacing=8),
                padding=ft.Padding(top=8, bottom=8, left=0, right=0),
            )

        # Charts
        charts_section = self._build_charts_section()

        # Quick actions
        actions = self._build_actions_section()

        return ft.Column(controls=[
            header,
            ft.Container(height=16),
            row1,
            ft.Container(height=8),
            row2,
            ft.Container(height=16),
            severity_section,
            ft.Container(height=8),
            charts_section,
            ft.Container(height=16),
            actions,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_charts_section(self) -> ft.Column:
        charts = []

        if self.project.metrics.languages:
            lang_chart = PieChart(
                title="Language Distribution",
                data=self.project.metrics.languages,
                colors=LANG_COLORS
            )
            charts.append(ft.Card(content=lang_chart, elevation=1))

        if self.project.findings:
            type_counts = {}
            for f in self.project.findings:
                t = f.finding_type.value.replace("_", " ").capitalize()
                type_counts[t] = type_counts.get(t, 0) + 1
            if type_counts:
                charts.append(ft.Card(content=BarChart(
                    title="Findings by Type", data=type_counts, color=AppTheme.WARNING
                ), elevation=1))

        if self.project.suggestions:
            cat_counts = {}
            for s in self.project.suggestions:
                c = s.category.value.replace("_", " ").capitalize()
                cat_counts[c] = cat_counts.get(c, 0) + 1
            if cat_counts:
                charts.append(ft.Card(content=BarChart(
                    title="Suggestions by Category", data=cat_counts, color=AppTheme.PRIMARY
                ), elevation=1))

        if not charts:
            return ft.Container()

        return ft.Column(controls=[
            ft.Text("Analytics", size=AppTheme.FONT_SIZE_XLARGE,
                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ft.Container(height=8),
            ft.Row(controls=charts, spacing=16, wrap=True),
        ], spacing=0)

    def _build_actions_section(self) -> ft.Column:
        actions = []
        btn_style = ft.ButtonStyle(
            padding=ft.Padding(left=20, right=20, top=12, bottom=12))

        if self.on_view_docs:
            actions.append(ft.ElevatedButton(
                content=ft.Row(controls=[ft.Icon(ft.Icons.DESCRIPTION), ft.Text("View Documentation")], spacing=8),
                on_click=lambda _: self.on_view_docs(), style=btn_style))

        if self.on_view_findings:
            actions.append(ft.ElevatedButton(
                content=ft.Row(controls=[ft.Icon(ft.Icons.BUG_REPORT), ft.Text("View Findings")], spacing=8),
                on_click=lambda _: self.on_view_findings(), style=btn_style))

        if self.on_view_suggestions:
            actions.append(ft.ElevatedButton(
                content=ft.Row(controls=[ft.Icon(ft.Icons.LIGHTBULB), ft.Text("View Suggestions")], spacing=8),
                on_click=lambda _: self.on_view_suggestions(), style=btn_style))

        if not actions:
            return ft.Container()

        return ft.Column(controls=[
            ft.Text("Quick Actions", size=AppTheme.FONT_SIZE_XLARGE,
                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ft.Container(height=8),
            ft.Row(controls=actions, spacing=12, wrap=True),
        ], spacing=0)

    def refresh(self, project: Project):
        self.project = project
        self.content = self._build_content()
        self.update()
