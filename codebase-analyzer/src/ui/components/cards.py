"""
Card Components

Reusable card components for displaying findings, suggestions, and other data.
"""

from typing import Optional, Callable
import flet as ft
from ...models.finding import Finding
from ...models.suggestion import Suggestion
from ..theme import AppTheme
from ..utils import create_badge, truncate_text


class FindingCard(ft.Card):
    """Card for displaying a code review finding."""

    def __init__(
        self,
        finding: Finding,
        on_resolve: Optional[Callable] = None,
        on_ignore: Optional[Callable] = None,
        expanded: bool = False
    ):
        self.finding = finding
        self.on_resolve = on_resolve
        self.on_ignore = on_ignore
        self.is_expanded = expanded

        super().__init__(content=self._build_content(), elevation=1)

    def _build_content(self) -> ft.Container:
        sev = self.finding.severity.value
        severity_color = AppTheme.get_severity_color(sev)

        # Header row
        header = ft.Row(controls=[
            create_badge(sev.upper(), severity_color),
            ft.Text(self.finding.title, size=15, weight=ft.FontWeight.BOLD, expand=True,
                     color=AppTheme.TEXT_PRIMARY),
            create_badge(self.finding.finding_type.value.replace("_", " "), "#78909C", size="small"),
            ft.IconButton(
                icon=ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE,
                on_click=self._toggle_expand, icon_size=18,
            ),
        ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Location + metadata
        loc = self.finding.location
        line_label = str(loc.line_start) if loc.line_start == loc.line_end else f"{loc.line_start}-{loc.line_end}"
        meta_items = [
            ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=13, color=AppTheme.TEXT_DISABLED),
            ft.Text(f"{loc.file_path}:{line_label}", size=12, color=AppTheme.TEXT_SECONDARY),
        ]
        if hasattr(self.finding, 'confidence') and self.finding.confidence:
            meta_items.extend([
                ft.Container(width=12),
                ft.Text(f"{self.finding.confidence:.0%} confidence", size=11, color=AppTheme.TEXT_DISABLED),
            ])
        if hasattr(self.finding, 'source') and self.finding.source:
            meta_items.extend([
                ft.Container(width=8),
                ft.Text(f"via {self.finding.source}", size=11, color=AppTheme.TEXT_DISABLED, italic=True),
            ])
        meta_row = ft.Row(controls=meta_items, spacing=4)

        # Description
        desc_text = self.finding.description if self.is_expanded else truncate_text(self.finding.description, 180)
        description = ft.Text(desc_text, size=13, color=AppTheme.TEXT_PRIMARY)

        controls = [header, meta_row, description]

        if self.is_expanded:
            if loc.code_snippet:
                controls.append(ft.Container(
                    content=ft.Text(loc.code_snippet, size=11, font_family="monospace",
                                    color=AppTheme.TEXT_PRIMARY),
                    bgcolor="#F8F9FA", padding=12, border_radius=6,
                    border=ft.Border.all(1, "#E8E8E8"),
                    margin=ft.Margin(top=4, bottom=0, left=0, right=0),
                ))

            rec = self.finding.suggested_fix or self.finding.recommendation
            if rec:
                controls.append(ft.Container(
                    content=ft.Column(controls=[
                        ft.Text("Suggested Fix", size=12, weight=ft.FontWeight.BOLD, color=AppTheme.SUCCESS),
                        ft.Text(rec, size=13, color=AppTheme.TEXT_PRIMARY),
                    ], spacing=4),
                    bgcolor="#F1F8E9", padding=10, border_radius=6,
                    margin=ft.Margin(top=4, bottom=0, left=0, right=0),
                ))

            if self.on_resolve or self.on_ignore:
                btns = []
                if self.on_resolve:
                    btns.append(ft.ElevatedButton("Resolve", icon=ft.Icons.CHECK_CIRCLE,
                                                   on_click=lambda _: self.on_resolve(self.finding),
                                                   bgcolor=AppTheme.SUCCESS, color="white"))
                if self.on_ignore:
                    btns.append(ft.OutlinedButton("Ignore", icon=ft.Icons.CANCEL,
                                                   on_click=lambda _: self.on_ignore(self.finding)))
                controls.append(ft.Row(controls=btns, spacing=8))

        return ft.Container(
            content=ft.Column(controls=controls, spacing=8),
            padding=ft.Padding(left=20, right=16, top=14, bottom=14),
            border=ft.Border(left=ft.BorderSide(4, severity_color)),
        )

    def _toggle_expand(self, e):
        self.is_expanded = not self.is_expanded
        self.content = self._build_content()
        self.update()


EFFORT_COLORS = {"low": AppTheme.SUCCESS, "medium": "#FFA726", "high": AppTheme.ERROR}
IMPACT_COLORS = {"low": "#BDBDBD", "medium": "#42A5F5", "high": "#7E57C2"}


class SuggestionCard(ft.Card):
    """Card for displaying an improvement suggestion."""

    def __init__(
        self,
        suggestion: Suggestion,
        on_accept: Optional[Callable] = None,
        on_dismiss: Optional[Callable] = None,
        expanded: bool = False
    ):
        self.suggestion = suggestion
        self.on_accept = on_accept
        self.on_dismiss = on_dismiss
        self.is_expanded = expanded

        super().__init__(content=self._build_content(), elevation=1)

    def _build_content(self) -> ft.Container:
        s = self.suggestion
        priority_color = AppTheme.get_priority_color(s.priority_score)
        effort_color = EFFORT_COLORS.get(s.effort.value, "#9E9E9E")
        impact_color = IMPACT_COLORS.get(s.impact.value, "#9E9E9E")

        # Header
        header = ft.Row(controls=[
            create_badge(f"{s.priority_score:.0f}", priority_color),
            ft.Text(s.title, size=15, weight=ft.FontWeight.BOLD, expand=True, color=AppTheme.TEXT_PRIMARY),
            ft.IconButton(icon=ft.Icons.EXPAND_LESS if self.is_expanded else ft.Icons.EXPAND_MORE,
                          on_click=self._toggle_expand, icon_size=18),
        ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Pill badges row
        pills = ft.Row(controls=[
            create_badge(f"Effort: {s.effort.value}", effort_color, size="small"),
            create_badge(f"Impact: {s.impact.value}", impact_color, size="small"),
            create_badge(s.category.value.replace("_", " "), "#78909C", size="small"),
        ], spacing=6)

        # Meta info
        meta_items = []
        if hasattr(s, 'related_files') and s.related_files:
            meta_items.append(ft.Text(f"Affects {len(s.related_files)} file(s)", size=11,
                                       color=AppTheme.TEXT_DISABLED))
        meta_row = ft.Row(controls=meta_items, spacing=8) if meta_items else ft.Container()

        # Description
        desc = s.description if self.is_expanded else truncate_text(s.description, 180)
        description = ft.Text(desc, size=13, color=AppTheme.TEXT_PRIMARY)

        controls = [header, pills, meta_row, description]

        if self.is_expanded:
            if hasattr(s, 'rationale') and s.rationale:
                controls.append(ft.Container(
                    content=ft.Column(controls=[
                        ft.Text("Rationale", size=12, weight=ft.FontWeight.BOLD, color=AppTheme.INFO),
                        ft.Text(s.rationale, size=13, color=AppTheme.TEXT_PRIMARY),
                    ], spacing=4),
                    bgcolor="#E3F2FD", padding=10, border_radius=6,
                ))

            if s.benefits:
                benefit_controls = [ft.Text("Benefits", size=12, weight=ft.FontWeight.BOLD, color=AppTheme.SUCCESS)]
                for b in s.benefits:
                    benefit_controls.append(ft.Row(controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=AppTheme.SUCCESS),
                        ft.Text(b, size=12, expand=True, color=AppTheme.TEXT_PRIMARY),
                    ], spacing=6))
                controls.append(ft.Container(
                    content=ft.Column(controls=benefit_controls, spacing=4),
                    bgcolor="#F1F8E9", padding=10, border_radius=6,
                ))

            if s.implementation_steps:
                step_controls = [ft.Text("Implementation Steps", size=12, weight=ft.FontWeight.BOLD)]
                for i, step in enumerate(s.implementation_steps, 1):
                    step_row_items = [
                        ft.Container(
                            content=ft.Text(str(i), size=11, color="white", weight=ft.FontWeight.BOLD,
                                            text_align=ft.TextAlign.CENTER),
                            width=22, height=22, border_radius=11, bgcolor=AppTheme.PRIMARY,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(controls=[
                            ft.Text(step.description, size=12, color=AppTheme.TEXT_PRIMARY),
                            ft.Text(f"~{step.estimated_time}", size=11, color=AppTheme.TEXT_DISABLED,
                                    italic=True) if step.estimated_time else ft.Container(),
                        ], spacing=2, expand=True),
                    ]
                    step_controls.append(ft.Row(controls=step_row_items, spacing=8))
                controls.append(ft.Column(controls=step_controls, spacing=6))

            if hasattr(s, 'risks') and s.risks:
                risk_items = [ft.Text("Risks", size=12, weight=ft.FontWeight.BOLD, color=AppTheme.ERROR)]
                for r in s.risks:
                    risk_items.append(ft.Row(controls=[
                        ft.Icon(ft.Icons.WARNING, size=14, color=AppTheme.WARNING),
                        ft.Text(r, size=12, expand=True, color=AppTheme.TEXT_PRIMARY),
                    ], spacing=6))
                controls.append(ft.Container(
                    content=ft.Column(controls=risk_items, spacing=4),
                    bgcolor="#FFF3E0", padding=10, border_radius=6,
                ))

            if self.on_accept or self.on_dismiss:
                btns = []
                if self.on_accept:
                    btns.append(ft.ElevatedButton("Accept", icon=ft.Icons.CHECK,
                                                   on_click=lambda _: self.on_accept(s),
                                                   bgcolor=AppTheme.SUCCESS, color="white"))
                if self.on_dismiss:
                    btns.append(ft.OutlinedButton("Dismiss", icon=ft.Icons.CLOSE,
                                                   on_click=lambda _: self.on_dismiss(s)))
                controls.append(ft.Row(controls=btns, spacing=8))

        return ft.Container(
            content=ft.Column(controls=controls, spacing=8),
            padding=ft.Padding(left=20, right=16, top=14, bottom=14),
            border=ft.Border(left=ft.BorderSide(4, priority_color)),
        )

    def _toggle_expand(self, e):
        self.is_expanded = not self.is_expanded
        self.content = self._build_content()
        self.update()


class ProgressCard(ft.Card):
    """Card component for displaying progress"""

    def __init__(
        self,
        title: str,
        current: int = 0,
        total: int = 100,
        status: str = "In Progress",
        show_cancel: bool = False,
        on_cancel: Optional[Callable] = None
    ):
        self.title = title
        self.current = current
        self.total = total
        self.status = status
        self.show_cancel = show_cancel
        self.on_cancel = on_cancel

        super().__init__(
            content=self._build_content(),
            elevation=2
        )

    def _build_content(self) -> ft.Container:
        """Build card content"""
        percentage = (self.current / self.total * 100) if self.total > 0 else 0

        # Header
        header = ft.Row(
            controls=[
                ft.Text(
                    self.title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    expand=True
                ),
                ft.Text(
                    f"{self.current}/{self.total}",
                    size=14,
                    color="#757575"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Progress bar
        progress_bar = ft.ProgressBar(
            value=percentage / 100,
            color=AppTheme.PRIMARY,
            bgcolor="#E0E0E0",
            height=8
        )

        # Status and percentage
        status_row = ft.Row(
            controls=[
                ft.Text(self.status, size=12, color="#757575"),
                ft.Text(f"{percentage:.1f}%", size=12, color="#757575")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        controls = [header, progress_bar, status_row]

        # Cancel button
        if self.show_cancel and self.on_cancel:
            controls.append(
                ft.Container(
                    content=ft.OutlinedButton(
                        "Cancel",
                        icon=ft.Icons.CANCEL,
                        on_click=lambda _: self.on_cancel()
                    ),
                    alignment=ft.Alignment(1, 0)
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=8
            ),
            padding=16
        )

    def update_progress(self, current: int, status: Optional[str] = None):
        """Update progress values"""
        self.current = current
        if status:
            self.status = status
        self.content = self._build_content()
        self.update()

# Made with Bob
