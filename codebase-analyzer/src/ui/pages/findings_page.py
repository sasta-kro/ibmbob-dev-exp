"""
Findings Page — display and filter code review findings.
"""

from typing import List, Optional, Callable
import flet as ft
from ...models.finding import Finding
from ..theme import AppTheme
from ..components import FindingCard, ChipFilterRow, SortControl
from ..utils import create_empty_state, create_badge, create_stacked_bar

SEVERITY_COLORS = {
    "critical": AppTheme.CRITICAL,
    "high": AppTheme.HIGH,
    "medium": AppTheme.MEDIUM,
    "low": AppTheme.LOW,
    "info": AppTheme.INFO_SEVERITY,
}

TYPE_COLORS = {
    "bug": "#D32F2F",
    "security": "#7B1FA2",
    "performance": "#F57C00",
    "style": "#0288D1",
    "maintainability": "#00796B",
    "documentation": "#5D4037",
    "complexity": "#C62828",
    "duplication": "#AD1457",
    "best_practice": "#1565C0",
}


class FindingsPage(ft.Container):

    def __init__(
        self,
        findings: Optional[List[Finding]] = None,
        on_resolve: Optional[Callable] = None,
        on_ignore: Optional[Callable] = None
    ):
        self.all_findings = findings or []
        self.filtered_findings = self.all_findings.copy()
        self.on_resolve = on_resolve
        self.on_ignore = on_ignore
        self._severity_filter: List[str] = []
        self._type_filter: List[str] = []
        self._search_query = ""
        self._sort_option = "Severity"
        self._sort_asc = True

        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )

    def _build_content(self) -> ft.Column:
        if not self.all_findings:
            return ft.Column(controls=[
                create_empty_state(
                    icon=ft.Icons.CHECK_CIRCLE,
                    title="No Findings",
                    description="No code review findings to display"
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        # Stats bar
        severity_counts = {}
        for f in self.all_findings:
            s = f.severity.value
            severity_counts[s] = severity_counts.get(s, 0) + 1

        stat_chips = []
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = severity_counts.get(sev, 0)
            if count > 0:
                stat_chips.append(ft.Container(
                    content=ft.Row(controls=[
                        ft.Container(width=8, height=8, bgcolor=SEVERITY_COLORS.get(sev, "#999"),
                                     border_radius=4),
                        ft.Text(f"{sev.capitalize()} {count}", size=12, color=AppTheme.TEXT_PRIMARY,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=6),
                    padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                    border=ft.Border.all(1, SEVERITY_COLORS.get(sev, "#999")),
                    border_radius=12,
                ))

        resolved = sum(1 for f in self.all_findings if f.is_resolved)
        ignored = sum(1 for f in self.all_findings if f.is_false_positive)
        if resolved or ignored:
            stat_chips.append(ft.Container(expand=True))
            if resolved:
                stat_chips.append(ft.Text(f"{resolved} resolved", size=11, color=AppTheme.SUCCESS))
            if ignored:
                stat_chips.append(ft.Text(f"{ignored} ignored", size=11, color=AppTheme.TEXT_DISABLED))

        stats_row = ft.Row(controls=stat_chips, spacing=8, wrap=True)

        stacked = create_stacked_bar(severity_counts, SEVERITY_COLORS, height=6)

        # Header
        self._search_field = ft.TextField(
            hint_text="Search findings...", prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search, dense=True, border_color=AppTheme.BORDER_COLOR,
            width=280, text_size=13,
        )
        header = ft.Row(controls=[
            ft.Text(f"Findings ({len(self.filtered_findings)})", size=AppTheme.FONT_SIZE_TITLE,
                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ft.Container(expand=True),
            self._search_field,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Chip filters
        severity_options = sorted({f.severity.value for f in self.all_findings})
        type_options = sorted({f.finding_type.value for f in self.all_findings})

        self._severity_chips = ChipFilterRow(
            label="Severity:", options=severity_options,
            color_map=SEVERITY_COLORS, on_change=self._on_severity_filter)
        self._type_chips = ChipFilterRow(
            label="Type:", options=type_options,
            color_map=TYPE_COLORS, on_change=self._on_type_filter)

        sort_control = SortControl(
            options=["Severity", "Category", "File"],
            on_sort_change=self._on_sort_change, default_option="Severity")

        filter_row = ft.Row(controls=[
            self._severity_chips,
            ft.Container(width=16),
            self._type_chips,
            ft.Container(expand=True),
            sort_control,
        ], spacing=0, wrap=True)

        # Findings list
        cards = [FindingCard(finding=f, on_resolve=self.on_resolve, on_ignore=self.on_ignore)
                 for f in self.filtered_findings]

        self._list_view = ft.ListView(controls=cards, spacing=10,
                                       padding=ft.Padding(top=8, bottom=8, left=0, right=0), expand=True)

        if not self.filtered_findings:
            self._list_view = ft.Column(controls=[
                create_empty_state(icon=ft.Icons.FILTER_ALT_OFF, title="No Matching Findings",
                                   description="Adjust filters to see results")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        return ft.Column(controls=[
            header,
            ft.Container(height=8),
            stats_row,
            stacked,
            ft.Container(height=10),
            filter_row,
            ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
            self._list_view,
        ], spacing=6, expand=True)

    def _apply_filters(self):
        self.filtered_findings = self.all_findings.copy()

        if self._severity_filter:
            self.filtered_findings = [f for f in self.filtered_findings
                                       if f.severity.value in self._severity_filter]
        if self._type_filter:
            self.filtered_findings = [f for f in self.filtered_findings
                                       if f.finding_type.value in self._type_filter]
        if self._search_query:
            q = self._search_query.lower()
            self.filtered_findings = [f for f in self.filtered_findings
                                       if q in f.title.lower() or q in f.description.lower()
                                       or q in str(f.location.file_path).lower()]
        self._apply_sort()
        self.content = self._build_content()
        self.update()

    def _apply_sort(self):
        if self._sort_option == "Severity":
            order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            self.filtered_findings.sort(key=lambda f: order.get(f.severity.value, 5),
                                         reverse=not self._sort_asc)
        elif self._sort_option == "Category":
            self.filtered_findings.sort(key=lambda f: f.finding_type.value, reverse=not self._sort_asc)
        elif self._sort_option == "File":
            self.filtered_findings.sort(key=lambda f: str(f.location.file_path), reverse=not self._sort_asc)

    def _on_severity_filter(self, selected: List[str]):
        self._severity_filter = selected
        self._apply_filters()

    def _on_type_filter(self, selected: List[str]):
        self._type_filter = selected
        self._apply_filters()

    def _on_search(self, e):
        self._search_query = e.control.value or ""
        self._apply_filters()

    def _on_sort_change(self, option: str, ascending: bool):
        self._sort_option = option
        self._sort_asc = ascending
        self._apply_filters()

    def refresh(self, findings: List[Finding]):
        self.all_findings = findings
        self.filtered_findings = findings.copy()
        self._severity_filter = []
        self._type_filter = []
        self._search_query = ""
        self.content = self._build_content()
        self.update()
