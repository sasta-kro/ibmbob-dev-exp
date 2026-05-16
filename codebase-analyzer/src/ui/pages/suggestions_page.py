"""
Suggestions Page — display and manage improvement suggestions.
"""

from typing import List, Optional, Callable
import flet as ft
from ...models.suggestion import Suggestion
from ..theme import AppTheme
from ..components import SuggestionCard, ChipFilterRow, SortControl
from ..utils import create_empty_state, create_badge

EFFORT_COLORS = {"low": AppTheme.SUCCESS, "medium": "#FFA726", "high": AppTheme.ERROR}
IMPACT_COLORS = {"low": "#BDBDBD", "medium": "#42A5F5", "high": "#7E57C2"}
CATEGORY_COLORS = {
    "refactoring": "#00897B",
    "performance": "#F57C00",
    "security": "#7B1FA2",
    "maintainability": "#0288D1",
    "testing": "#558B2F",
    "documentation": "#5D4037",
    "architecture": "#C62828",
    "code_quality": "#1565C0",
    "best_practices": "#6A1B9A",
}


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
        self._effort_filter: List[str] = []
        self._impact_filter: List[str] = []
        self._category_filter: List[str] = []
        self._search_query = ""
        self._sort_option = "Priority"
        self._sort_asc = False

        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )

    def _build_content(self) -> ft.Column:
        if not self.all_suggestions:
            return ft.Column(controls=[
                create_empty_state(
                    icon=ft.Icons.LIGHTBULB_OUTLINE,
                    title="No Suggestions",
                    description="No improvement suggestions available"
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        # Header
        search_field = ft.TextField(
            hint_text="Search suggestions...", prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search, dense=True, border_color=AppTheme.BORDER_COLOR,
            width=280, text_size=13,
        )
        header = ft.Row(controls=[
            ft.Text(f"Suggestions ({len(self.filtered_suggestions)})",
                    size=AppTheme.FONT_SIZE_TITLE, weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY),
            ft.Container(expand=True),
            search_field,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Quick wins banner
        quick_wins = [s for s in self.filtered_suggestions
                      if s.effort.value == "low" and s.impact.value == "high"]
        quick_wins_section = ft.Container()
        if quick_wins:
            mini_cards = []
            for qw in quick_wins[:6]:
                priority_color = AppTheme.get_priority_color(qw.priority_score)
                mini_cards.append(ft.Container(
                    content=ft.Column(controls=[
                        ft.Row(controls=[
                            create_badge(f"{qw.priority_score:.0f}", priority_color),
                            create_badge(qw.category.value.replace("_", " "), "#78909C", size="small"),
                        ], spacing=4),
                        ft.Text(qw.title, size=12, weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY, max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=6),
                    width=200, padding=10, border_radius=8,
                    bgcolor="white", border=ft.Border.all(1, "#E0E0E0"),
                ))

            quick_wins_section = ft.Container(
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.Icon(ft.Icons.FLASH_ON, size=20, color="#FF8F00"),
                        ft.Text(f"Quick Wins ({len(quick_wins)})", size=15,
                                weight=ft.FontWeight.BOLD, color="#FF8F00"),
                        ft.Text("Low effort, high impact", size=12,
                                color=AppTheme.TEXT_SECONDARY, italic=True),
                    ], spacing=8),
                    ft.Row(controls=mini_cards, spacing=10,
                           scroll=ft.ScrollMode.AUTO),
                ], spacing=8),
                padding=14, border_radius=10,
                bgcolor="#FFF8E1",
                border=ft.Border(left=ft.BorderSide(4, "#FF8F00")),
            )

        # Chip filters
        effort_options = sorted({s.effort.value for s in self.all_suggestions})
        impact_options = sorted({s.impact.value for s in self.all_suggestions})
        cat_options = sorted({s.category.value for s in self.all_suggestions})

        effort_chips = ChipFilterRow(label="Effort:", options=effort_options,
                                      color_map=EFFORT_COLORS, on_change=self._on_effort_filter)
        impact_chips = ChipFilterRow(label="Impact:", options=impact_options,
                                      color_map=IMPACT_COLORS, on_change=self._on_impact_filter)
        cat_chips = ChipFilterRow(label="Category:", options=cat_options,
                                   color_map=CATEGORY_COLORS, on_change=self._on_category_filter)

        sort_control = SortControl(
            options=["Priority", "Effort", "Impact"],
            on_sort_change=self._on_sort_change, default_option="Priority")

        filter_row = ft.Column(controls=[
            ft.Row(controls=[effort_chips, ft.Container(width=12), impact_chips], wrap=True),
            ft.Row(controls=[cat_chips, ft.Container(expand=True), sort_control], wrap=True),
        ], spacing=6)

        # Cards list
        cards = [SuggestionCard(suggestion=s, on_accept=self.on_accept, on_dismiss=self.on_dismiss)
                 for s in self.filtered_suggestions]

        list_view = ft.ListView(controls=cards, spacing=10,
                                 padding=ft.Padding(top=8, bottom=8, left=0, right=0), expand=True)

        if not self.filtered_suggestions:
            list_view = ft.Column(controls=[
                create_empty_state(icon=ft.Icons.FILTER_ALT_OFF, title="No Matching Suggestions",
                                   description="Adjust filters to see results")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER, expand=True)

        return ft.Column(controls=[
            header,
            ft.Container(height=6),
            quick_wins_section,
            ft.Container(height=6),
            filter_row,
            ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
            list_view,
        ], spacing=4, expand=True)

    def _apply_filters(self):
        self.filtered_suggestions = self.all_suggestions.copy()

        if self._effort_filter:
            self.filtered_suggestions = [s for s in self.filtered_suggestions
                                          if s.effort.value in self._effort_filter]
        if self._impact_filter:
            self.filtered_suggestions = [s for s in self.filtered_suggestions
                                          if s.impact.value in self._impact_filter]
        if self._category_filter:
            self.filtered_suggestions = [s for s in self.filtered_suggestions
                                          if s.category.value in self._category_filter]
        if self._search_query:
            q = self._search_query.lower()
            self.filtered_suggestions = [s for s in self.filtered_suggestions
                                          if q in s.title.lower() or q in s.description.lower()]
        self._apply_sort()
        self.content = self._build_content()
        self.update()

    def _apply_sort(self):
        if self._sort_option == "Priority":
            self.filtered_suggestions.sort(key=lambda s: s.priority_score, reverse=not self._sort_asc)
        elif self._sort_option == "Effort":
            order = {"low": 0, "medium": 1, "high": 2}
            self.filtered_suggestions.sort(key=lambda s: order.get(s.effort.value, 3),
                                            reverse=not self._sort_asc)
        elif self._sort_option == "Impact":
            order = {"low": 0, "medium": 1, "high": 2}
            self.filtered_suggestions.sort(key=lambda s: order.get(s.impact.value, 3),
                                            reverse=not self._sort_asc)

    def _on_effort_filter(self, selected: List[str]):
        self._effort_filter = selected
        self._apply_filters()

    def _on_impact_filter(self, selected: List[str]):
        self._impact_filter = selected
        self._apply_filters()

    def _on_category_filter(self, selected: List[str]):
        self._category_filter = selected
        self._apply_filters()

    def _on_search(self, e):
        self._search_query = e.control.value or ""
        self._apply_filters()

    def _on_sort_change(self, option: str, ascending: bool):
        self._sort_option = option
        self._sort_asc = ascending
        self._apply_filters()

    def refresh(self, suggestions: List[Suggestion]):
        self.all_suggestions = suggestions
        self.filtered_suggestions = suggestions.copy()
        self._effort_filter = []
        self._impact_filter = []
        self._category_filter = []
        self._search_query = ""
        self.content = self._build_content()
        self.update()
