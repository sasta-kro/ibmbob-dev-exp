"""
Findings Page — display and filter code review findings.
"""

from typing import List, Optional, Callable
import flet as ft
from ...models.finding import Finding
from ..theme import AppTheme

PAGE_SIZE = 50

SEVERITY_COLORS = {
    "critical": AppTheme.CRITICAL,
    "high": AppTheme.HIGH,
    "medium": AppTheme.MEDIUM,
    "low": AppTheme.LOW,
    "info": AppTheme.INFO_SEVERITY,
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
        self._visible_count = PAGE_SIZE
        self._search_query = ""

        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )

    def _build_content(self) -> ft.Column:
        if not self.all_findings:
            return ft.Column(controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color="#BDBDBD"),
                ft.Text("No Findings", size=20, weight=ft.FontWeight.BOLD, color="#757575"),
                ft.Text("Run an analysis to see findings here", size=14, color="#9E9E9E"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        rows = []

        # Title + count
        rows.append(ft.Text(f"Findings ({len(self.filtered_findings)})",
                            size=AppTheme.FONT_SIZE_TITLE, weight=ft.FontWeight.BOLD))

        # Severity summary line
        sev_counts = {}
        for f in self.all_findings:
            s = f.severity.value
            sev_counts[s] = sev_counts.get(s, 0) + 1
        summary_parts = []
        for sev in ["critical", "high", "medium", "low", "info"]:
            c = sev_counts.get(sev, 0)
            if c > 0:
                color = SEVERITY_COLORS.get(sev, "#999")
                summary_parts.append(ft.Container(
                    content=ft.Text(f"{sev.upper()} {c}", size=11, color="white",
                                    weight=ft.FontWeight.BOLD),
                    bgcolor=color, border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                ))
        if summary_parts:
            rows.append(ft.Row(controls=summary_parts, spacing=6))

        # Search
        rows.append(ft.TextField(
            hint_text="Search findings...", prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search, dense=True, border_color=AppTheme.BORDER_COLOR,
            text_size=13,
        ))

        rows.append(ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR))

        # Finding rows — plain containers, no custom cards
        visible = self.filtered_findings[:self._visible_count]
        for f in visible:
            sev = f.severity.value
            color = SEVERITY_COLORS.get(sev, "#999")
            loc = f.location

            line_label = str(loc.line_start)
            if loc.line_end and loc.line_end != loc.line_start:
                line_label = f"{loc.line_start}-{loc.line_end}"

            row = ft.Container(
                content=ft.Row(controls=[
                    ft.Container(
                        content=ft.Text(sev.upper(), size=10, color="white",
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=color, border_radius=4, width=70,
                        alignment=ft.Alignment(0, 0),
                        padding=ft.Padding(left=6, right=6, top=4, bottom=4),
                    ),
                    ft.Column(controls=[
                        ft.Text(f.title, size=14, weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY),
                        ft.Text(f.description, size=12, color=AppTheme.TEXT_PRIMARY,
                                max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{loc.file_path}:{line_label}", size=11,
                                color=AppTheme.TEXT_SECONDARY),
                    ], spacing=2, expand=True),
                    ft.Text(f.finding_type.value.replace("_", " "), size=11,
                            color=AppTheme.TEXT_DISABLED),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, AppTheme.DIVIDER_COLOR)),
            )
            rows.append(row)

        # Show more
        remaining = len(self.filtered_findings) - self._visible_count
        if remaining > 0:
            rows.append(ft.Container(
                content=ft.TextButton(
                    content=ft.Text(f"Show more ({remaining} remaining)",
                                    size=14, color=AppTheme.PRIMARY,
                                    weight=ft.FontWeight.BOLD),
                    on_click=self._load_more,
                ),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding(top=12, bottom=12, left=0, right=0),
            ))

        return ft.Column(controls=rows, spacing=6,
                         scroll=ft.ScrollMode.AUTO, expand=True)

    def _load_more(self, e):
        self._visible_count += PAGE_SIZE
        self.content = self._build_content()
        self.update()

    def _on_search(self, e):
        self._search_query = e.control.value or ""
        self._apply_filters()

    def _apply_filters(self):
        self.filtered_findings = self.all_findings.copy()
        if self._search_query:
            q = self._search_query.lower()
            self.filtered_findings = [f for f in self.filtered_findings
                                       if q in f.title.lower() or q in f.description.lower()
                                       or q in str(f.location.file_path).lower()]
        self._visible_count = PAGE_SIZE
        self.content = self._build_content()
        self.update()

    def refresh(self, findings: List[Finding]):
        self.all_findings = findings
        self.filtered_findings = findings.copy()
        self._search_query = ""
        self._visible_count = PAGE_SIZE
        self.content = self._build_content()
        self.update()
