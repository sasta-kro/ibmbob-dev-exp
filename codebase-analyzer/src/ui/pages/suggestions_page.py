"""
Suggestions Page - display and manage improvement suggestions.
"""

from typing import List, Optional, Callable
import flet as ft
from ...models.suggestion import Suggestion
from ..theme import AppTheme

PAGE_SIZE = 50

EFFORT_COLORS = {"low": AppTheme.SUCCESS, "medium": "#FFA726", "high": AppTheme.ERROR}
IMPACT_COLORS = {"low": "#BDBDBD", "medium": "#42A5F5", "high": "#7E57C2"}


class SuggestionsPage(ft.Container):

    def __init__(
        self,
        suggestions: Optional[List[Suggestion]] = None,
        on_accept: Optional[Callable] = None,
        on_dismiss: Optional[Callable] = None
    ):
        self.all_suggestions = suggestions or []
        self.filtered_suggestions = self.all_suggestions.copy()
        self.on_accept = on_accept
        self.on_dismiss = on_dismiss
        self._visible_count = PAGE_SIZE
        self._search_query = ""
        self._mounted = False
        self._title_text = ft.Text(
            f"Suggestions ({len(self.filtered_suggestions)})",
            size=AppTheme.FONT_SIZE_TITLE,
            weight=ft.FontWeight.BOLD
        )
        self._search_field = ft.TextField(
            hint_text="Search suggestions...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search,
            dense=True,
            border_color=AppTheme.BORDER_COLOR,
            text_size=13,
            value=self._search_query,
        )
        self._list_column = ft.Column(controls=[], spacing=6)
        self._show_more_label = ft.Text("", size=14, color=AppTheme.PRIMARY,
                                        weight=ft.FontWeight.BOLD)
        self._show_more_button = ft.TextButton(
            content=self._show_more_label,
            on_click=self._load_more,
        )
        self._show_more_container = ft.Container(
            content=self._show_more_button,
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding(top=12, bottom=12, left=0, right=0),
            visible=False,
        )

        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )

        if self.all_suggestions:
            self._update_list_view()

    def _build_content(self) -> ft.Column:
        if not self.all_suggestions:
            return ft.Column(controls=[
                ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=64, color="#BDBDBD"),
                ft.Text("No Suggestions", size=20, weight=ft.FontWeight.BOLD, color="#757575"),
                ft.Text("Run an analysis to see suggestions here", size=14, color="#9E9E9E"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        rows = []
        rows.append(self._title_text)
        rows.append(self._search_field)
        rows.append(ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR))
        rows.append(self._list_column)
        rows.append(self._show_more_container)

        return ft.Column(controls=rows, spacing=6,
                         scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_rows(self) -> List[ft.Control]:
        rows: List[ft.Control] = []
        visible = self.filtered_suggestions[:self._visible_count]
        for s in visible:
            priority_color = AppTheme.get_priority_color(s.priority_score)
            effort_color = EFFORT_COLORS.get(s.effort.value, "#9E9E9E")
            impact_color = IMPACT_COLORS.get(s.impact.value, "#9E9E9E")
            description_text = s.description or s.rationale or ""

            row = ft.Container(
                content=ft.Row(controls=[
                    ft.Container(
                        content=ft.Text(f"{s.priority_score:.0f}", size=12, color="white",
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=priority_color, border_radius=4, width=40,
                        alignment=ft.Alignment(0, 0),
                        padding=ft.Padding(left=6, right=6, top=4, bottom=4),
                    ),
                    ft.Column(controls=[
                        ft.Text(s.title, size=14, weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY),
                        ft.Text(
                            description_text,
                            size=12,
                            color=AppTheme.TEXT_SECONDARY,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row(controls=[
                            ft.Container(
                                content=ft.Text(f"Effort: {s.effort.value}", size=10,
                                                color=effort_color, weight=ft.FontWeight.BOLD),
                                border=ft.Border.all(1, effort_color), border_radius=8,
                                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                            ),
                            ft.Container(
                                content=ft.Text(f"Impact: {s.impact.value}", size=10,
                                                color=impact_color, weight=ft.FontWeight.BOLD),
                                border=ft.Border.all(1, impact_color), border_radius=8,
                                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                            ),
                            ft.Text(s.category.value.replace("_", " "), size=10,
                                    color=AppTheme.TEXT_DISABLED),
                        ], spacing=6),
                    ], spacing=4, expand=True),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, AppTheme.DIVIDER_COLOR)),
            )
            rows.append(row)

        return rows

    def _update_list_view(self):
        self._title_text.value = f"Suggestions ({len(self.filtered_suggestions)})"
        self._list_column.controls = self._build_rows()
        remaining = len(self.filtered_suggestions) - self._visible_count
        self._show_more_container.visible = remaining > 0
        if remaining > 0:
            self._show_more_label.value = f"Show more ({remaining} remaining)"
        self._request_update()

    def _request_update(self):
        if self._mounted:
            self.update()

    def did_mount(self):
        self._mounted = True

    def did_unmount(self):
        self._mounted = False

    def refresh(self, suggestions: List[Suggestion]):
        self.all_suggestions = suggestions
        self.filtered_suggestions = suggestions.copy()
        self._search_query = ""
        self._visible_count = PAGE_SIZE
        self._search_field.value = self._search_query
        self.content = self._build_content()
        if self.all_suggestions:
            self._update_list_view()
        self._request_update()

    def _load_more(self, e):
        self._visible_count += PAGE_SIZE
        self._update_list_view()

    def _on_search(self, e):
        self._search_query = e.control.value or ""
        self._search_field.value = self._search_query
        self._apply_filters()

    def _apply_filters(self):
        self.filtered_suggestions = self.all_suggestions.copy()
        if self._search_query:
            q = self._search_query.lower()
            self.filtered_suggestions = [s for s in self.filtered_suggestions
                                          if q in s.title.lower() or q in s.description.lower()]
        self._visible_count = PAGE_SIZE
        self._update_list_view()
