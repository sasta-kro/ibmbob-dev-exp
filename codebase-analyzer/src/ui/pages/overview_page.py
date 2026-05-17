"""
Overview Page - project metrics, statistics, and charts.
"""

import math
from typing import Callable, Dict, Optional
import flet as ft
from ...models.project import Project
from ..theme import AppTheme
from ..components import MetricCard, PieChart
from ..utils import format_number, create_empty_state

SEVERITY_COLORS = {
    "critical": AppTheme.CRITICAL, "high": AppTheme.HIGH, "medium": AppTheme.MEDIUM,
    "low": AppTheme.LOW, "info": AppTheme.INFO_SEVERITY,
}
IMPACT_COLORS = {
    "high": "#7E57C2",
    "medium": "#42A5F5",
    "low": "#BDBDBD",
}
FINDING_TYPE_COLORS = {
    "Bug": "#EF5350",
    "Security": "#AB47BC",
    "Performance": "#29B6F6",
    "Style": "#FFA726",
    "Maintainability": "#66BB6A",
    "Documentation": "#8D6E63",
    "Complexity": "#5C6BC0",
    "Duplication": "#EC407A",
    "Best practice": "#26A69A",
}
SUGGESTION_TYPE_COLORS = {
    "Refactoring": "#42A5F5",
    "Performance": "#26A69A",
    "Security": "#EF5350",
    "Maintainability": "#7E57C2",
    "Testing": "#FF7043",
    "Documentation": "#8D6E63",
    "Architecture": "#5C6BC0",
    "Code quality": "#66BB6A",
    "Best practices": "#FFA726",
}
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
    "Java": "#B07219", "Go": "#00ADD8", "Ruby": "#CC342D", "PHP": "#4F5D95",
    "C": "#555555", "C++": "#F34B7D", "Rust": "#DEA584", "Swift": "#FA7343",
    "HTML": "#E34F26", "CSS": "#1572B6", "SQL": "#336791", "Shell": "#4EAA25",
}
METRIC_CARD_HEIGHT = 120
CHART_CARD_BASE_HEIGHT = 280
CHART_CARD_LEGEND_ROW_HEIGHT = 24


class OverviewPage(ft.Container):

    def __init__(
        self,
        project: Optional[Project] = None,
        on_view_docs: Optional[Callable] = None,
        on_view_findings: Optional[Callable] = None,
        on_view_suggestions: Optional[Callable] = None
    ):
        self.project = project
        self.on_view_docs = on_view_docs
        self.on_view_findings = on_view_findings
        self.on_view_suggestions = on_view_suggestions
        self._mounted = False
        self._findings_chart_mode = "severity"
        self._suggestions_chart_mode = "severity"
        self._findings_chart_container = ft.Container()
        self._suggestions_chart_container = ft.Container()
        self._findings_switch_row = ft.Row(spacing=8)
        self._suggestions_switch_row = ft.Row(spacing=8)
        self._chart_card_height = self._calculate_chart_card_height()

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

        # Metrics
        total_files = len(p.files)
        total_findings = len(p.findings) if p.findings else 0
        total_suggestions = len(p.suggestions) if p.suggestions else 0
        func_groups = len(p.functionality_map.groups) if p.functionality_map else 0

        metrics_row = ft.ResponsiveRow(
            controls=[
                self._build_metric_card_container(
                    title="Files",
                    value=format_number(total_files),
                    icon=ft.Icons.FOLDER,
                    color=AppTheme.PRIMARY,
                    subtitle=f"{func_groups} groups",
                ),
                self._build_metric_card_container(
                    title="Lines of Code",
                    value=format_number(m.total_lines),
                    icon=ft.Icons.CODE,
                    color="#6A1B9A",
                ),
                self._build_metric_card_container(
                    title="Functions",
                    value=format_number(m.total_functions),
                    icon=ft.Icons.FUNCTIONS,
                    color="#00695C",
                ),
                self._build_metric_card_container(
                    title="Classes",
                    value=format_number(m.total_classes),
                    icon=ft.Icons.CLASS_,
                    color="#E65100",
                ),
            ],
            spacing=12,
            run_spacing=12,
        )

        # Charts
        charts_section = self._build_charts_section()

        # Quick actions
        actions = self._build_actions_section()

        return ft.Column(controls=[
            header,
            ft.Container(height=16),
            metrics_row,
            ft.Container(height=16),
            charts_section,
            ft.Container(height=16),
            actions,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_charts_section(self) -> ft.Control:
        chart_cards = []

        language_chart = self._build_language_chart_card(self._chart_card_height)
        findings_chart = self._build_findings_chart_card(self._chart_card_height)
        suggestions_chart = self._build_suggestions_chart_card(self._chart_card_height)

        if language_chart:
            chart_cards.append(language_chart)
        if findings_chart:
            chart_cards.append(findings_chart)
        if suggestions_chart:
            chart_cards.append(suggestions_chart)

        if not chart_cards:
            return ft.Container()

        return ft.ResponsiveRow(controls=chart_cards, spacing=16, run_spacing=16)

    def _build_metric_card_container(
        self,
        title: str,
        value: str,
        icon: str,
        color: str,
        subtitle: Optional[str] = None,
    ) -> ft.Container:
        return ft.Container(
            content=MetricCard(
                title=title,
                value=value,
                icon=icon,
                color=color,
                subtitle=subtitle,
            ),
            col={"xs": 12, "sm": 6, "md": 3},
            height=METRIC_CARD_HEIGHT,
        )

    def _build_language_chart_card(self, chart_card_height: int) -> Optional[ft.Card]:
        if not self.project.metrics.languages:
            return None

        normalized_language_counts = {}
        normalized_language_colors = {}
        for language_name, file_count in self.project.metrics.languages.items():
            chart_label = language_name.replace("_", " ").title()
            normalized_language_counts[chart_label] = file_count
            if chart_label in LANG_COLORS:
                normalized_language_colors[chart_label] = LANG_COLORS[chart_label]

        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            self._build_chart_header(
                                title="Languages",
                                value=format_number(len(self.project.metrics.languages)),
                            ),
                            ft.Container(height=12),
                            PieChart(
                                title="",
                                data=normalized_language_counts,
                                colors=normalized_language_colors,
                            ),
                        ],
                        spacing=0,
                    ),
                    expand=True,
                    padding=16,
                    height=chart_card_height,
                ),
                elevation=1,
            ),
            col={"xs": 12, "sm": 12, "md": 4},
        )

    def _build_findings_chart_card(self, chart_card_height: int) -> Optional[ft.Card]:
        if not self.project.findings:
            return None

        self._findings_chart_container.content = self._create_findings_chart()
        self._findings_switch_row.controls = [
            self._create_switch_button(
                label="Severity",
                is_selected=self._findings_chart_mode == "severity",
                on_click=self._show_findings_severity_chart,
            ),
            self._create_switch_button(
                label="Type",
                is_selected=self._findings_chart_mode == "type",
                on_click=self._show_findings_type_chart,
            ),
        ]

        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self._build_chart_header(
                                        title="Findings",
                                        value=format_number(len(self.project.findings)),
                                    ),
                                    self._findings_switch_row,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(height=12),
                            self._findings_chart_container,
                        ],
                        spacing=0,
                    ),
                    padding=16,
                    expand=True,
                    height=chart_card_height,
                ),
                elevation=1,
            ),
            col={"xs": 12, "sm": 12, "md": 4},
        )

    def _build_suggestions_chart_card(self, chart_card_height: int) -> Optional[ft.Card]:
        if not self.project.suggestions:
            return None

        self._suggestions_chart_container.content = self._create_suggestions_chart()
        self._suggestions_switch_row.controls = [
            self._create_switch_button(
                label="Severity",
                is_selected=self._suggestions_chart_mode == "severity",
                on_click=self._show_suggestions_severity_chart,
            ),
            self._create_switch_button(
                label="Type",
                is_selected=self._suggestions_chart_mode == "type",
                on_click=self._show_suggestions_type_chart,
            ),
        ]

        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self._build_chart_header(
                                        title="Suggestions",
                                        value=format_number(len(self.project.suggestions)),
                                    ),
                                    self._suggestions_switch_row,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(height=12),
                            self._suggestions_chart_container,
                        ],
                        spacing=0,
                    ),
                    padding=16,
                    expand=True,
                    height=chart_card_height,
                ),
                elevation=1,
            ),
            col={"xs": 12, "sm": 12, "md": 4},
        )

    def _create_switch_button(
        self,
        label: str,
        is_selected: bool,
        on_click: Callable,
    ) -> ft.Control:
        button_style = ft.ButtonStyle(
            bgcolor=AppTheme.PRIMARY if is_selected else AppTheme.BG_PRIMARY,
            color=AppTheme.TEXT_ON_PRIMARY if is_selected else AppTheme.TEXT_SECONDARY,
            side=ft.BorderSide(1, AppTheme.PRIMARY if is_selected else AppTheme.BORDER_COLOR),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            shape=ft.RoundedRectangleBorder(radius=8),
        )
        return ft.TextButton(
            content=ft.Text(label),
            on_click=on_click,
            style=button_style,
        )

    def _build_chart_header(self, title: str, value: str) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                ),
                ft.Text(
                    value,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                ),
            ],
            spacing=8,
            tight=True,
        )

    def _create_findings_chart(self) -> ft.Control:
        if self._findings_chart_mode == "type":
            return PieChart(
                title="",
                data=self._get_finding_type_counts(),
                colors=FINDING_TYPE_COLORS,
            )

        return PieChart(
            title="",
            data=self._get_finding_severity_counts(),
            colors={severity.title(): color for severity, color in SEVERITY_COLORS.items()},
        )

    def _create_suggestions_chart(self) -> ft.Control:
        if self._suggestions_chart_mode == "type":
            return PieChart(
                title="",
                data=self._get_suggestion_type_counts(),
                colors=SUGGESTION_TYPE_COLORS,
            )

        return PieChart(
            title="",
            data=self._get_suggestion_severity_counts(),
            colors={impact.title(): color for impact, color in IMPACT_COLORS.items()},
        )

    def _get_finding_severity_counts(self) -> Dict[str, int]:
        severity_counts: Dict[str, int] = {}
        for finding in self.project.findings:
            chart_label = finding.severity.value.title()
            severity_counts[chart_label] = severity_counts.get(chart_label, 0) + 1
        return severity_counts

    def _get_finding_type_counts(self) -> Dict[str, int]:
        type_counts: Dict[str, int] = {}
        for finding in self.project.findings:
            chart_label = finding.finding_type.value.replace("_", " ").capitalize()
            type_counts[chart_label] = type_counts.get(chart_label, 0) + 1
        return type_counts

    def _get_suggestion_severity_counts(self) -> Dict[str, int]:
        severity_counts: Dict[str, int] = {}
        for suggestion in self.project.suggestions:
            chart_label = suggestion.impact.value.title()
            severity_counts[chart_label] = severity_counts.get(chart_label, 0) + 1
        return severity_counts

    def _get_suggestion_type_counts(self) -> Dict[str, int]:
        type_counts: Dict[str, int] = {}
        for suggestion in self.project.suggestions:
            chart_label = suggestion.category.value.replace("_", " ").capitalize()
            type_counts[chart_label] = type_counts.get(chart_label, 0) + 1
        return type_counts

    def _calculate_chart_card_height(self) -> int:
        if not self.project:
            return CHART_CARD_BASE_HEIGHT

        all_category_counts = []

        if self.project.metrics.languages:
            all_category_counts.append(len(self.project.metrics.languages))

        if self.project.findings:
            all_category_counts.append(len(self._get_finding_severity_counts()))
            all_category_counts.append(len(self._get_finding_type_counts()))

        if self.project.suggestions:
            all_category_counts.append(len(self._get_suggestion_severity_counts()))
            all_category_counts.append(len(self._get_suggestion_type_counts()))

        if not all_category_counts:
            return CHART_CARD_BASE_HEIGHT

        tallest_category_count = max(all_category_counts)
        legend_row_count = max(1, math.ceil(tallest_category_count / 2))
        return CHART_CARD_BASE_HEIGHT + (legend_row_count * CHART_CARD_LEGEND_ROW_HEIGHT)

    def _show_findings_severity_chart(self, _):
        self._findings_chart_mode = "severity"
        self._refresh_findings_chart_card()

    def _show_findings_type_chart(self, _):
        self._findings_chart_mode = "type"
        self._refresh_findings_chart_card()

    def _show_suggestions_severity_chart(self, _):
        self._suggestions_chart_mode = "severity"
        self._refresh_suggestions_chart_card()

    def _show_suggestions_type_chart(self, _):
        self._suggestions_chart_mode = "type"
        self._refresh_suggestions_chart_card()

    def _refresh_findings_chart_card(self):
        self._findings_chart_container.content = self._create_findings_chart()
        self._findings_switch_row.controls = [
            self._create_switch_button(
                label="Severity",
                is_selected=self._findings_chart_mode == "severity",
                on_click=self._show_findings_severity_chart,
            ),
            self._create_switch_button(
                label="Type",
                is_selected=self._findings_chart_mode == "type",
                on_click=self._show_findings_type_chart,
            ),
        ]
        self._request_update()

    def _refresh_suggestions_chart_card(self):
        self._suggestions_chart_container.content = self._create_suggestions_chart()
        self._suggestions_switch_row.controls = [
            self._create_switch_button(
                label="Severity",
                is_selected=self._suggestions_chart_mode == "severity",
                on_click=self._show_suggestions_severity_chart,
            ),
            self._create_switch_button(
                label="Type",
                is_selected=self._suggestions_chart_mode == "type",
                on_click=self._show_suggestions_type_chart,
            ),
        ]
        self._request_update()

    def _build_actions_section(self) -> ft.Column:
        actions = []
        btn_style = ft.ButtonStyle(
            padding=ft.Padding(left=20, right=20, top=12, bottom=12))

        if self.on_view_docs:
            actions.append(
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            controls=[ft.Icon(ft.Icons.DESCRIPTION), ft.Text("View Documentation")],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=lambda _: self.on_view_docs(),
                        style=btn_style,
                        width=float("inf"),
                    ),
                    expand=True,
                )
            )

        if self.on_view_findings:
            actions.append(
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            controls=[ft.Icon(ft.Icons.BUG_REPORT), ft.Text("View Findings")],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=lambda _: self.on_view_findings(),
                        style=btn_style,
                        width=float("inf"),
                    ),
                    expand=True,
                )
            )

        if self.on_view_suggestions:
            actions.append(
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            controls=[ft.Icon(ft.Icons.LIGHTBULB), ft.Text("View Suggestions")],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=lambda _: self.on_view_suggestions(),
                        style=btn_style,
                        width=float("inf"),
                    ),
                    expand=True,
                )
            )

        if not actions:
            return ft.Container()

        return ft.Column(controls=[
            ft.Text("Quick Actions", size=AppTheme.FONT_SIZE_XLARGE,
                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ft.Container(height=8),
            ft.Row(
                controls=actions,
                spacing=12,
                wrap=False,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ], spacing=0)

    def refresh(self, project: Project):
        self.project = project
        self._findings_chart_mode = "severity"
        self._suggestions_chart_mode = "severity"
        self._chart_card_height = self._calculate_chart_card_height()
        self.content = self._build_content()
        self._request_update()

    def _request_update(self):
        if self._mounted:
            self.update()

    def did_mount(self):
        self._mounted = True

    def did_unmount(self):
        self._mounted = False
