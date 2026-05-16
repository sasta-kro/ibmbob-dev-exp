"""
Suggestions Page

Display and manage improvement suggestions.
"""

from typing import List, Optional, Callable
import flet as ft
from ...models.suggestion import Suggestion
from ..theme import AppTheme
from ..components import SuggestionCard, FilterPanel, SortControl
from ..utils import create_empty_state


class SuggestionsPage(ft.Container):
    """Suggestions page component"""
    
    def __init__(
        self,
        suggestions: Optional[List[Suggestion]] = None,
        on_accept: Optional[Callable] = None,
        on_dismiss: Optional[Callable] = None
    ):
        """
        Initialize suggestions page
        
        Args:
            suggestions: List of suggestions to display
            on_accept: Callback when suggestion is accepted
            on_dismiss: Callback when suggestion is dismissed
        """
        self.all_suggestions = suggestions or []
        self.filtered_suggestions = self.all_suggestions.copy()
        self.on_accept = on_accept
        self.on_dismiss = on_dismiss
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _build_content(self) -> ft.Row:
        """Build suggestions page content"""
        if not self.all_suggestions:
            return ft.Row(
                controls=[
                    create_empty_state(
                        icon=ft.icons.LIGHTBULB_OUTLINE,
                        title="No Suggestions",
                        description="No improvement suggestions available"
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        
        # Filter panel
        filter_options = {
            "effort": ["low", "medium", "high"],
            "impact": ["low", "medium", "high"],
            "category": ["refactoring", "performance", "security", "documentation", "testing", "architecture"]
        }
        
        filter_panel = FilterPanel(
            filters=filter_options,
            on_filter_change=self._on_filter_change,
            search_enabled=True,
            on_search=self._on_search
        )
        
        # Main content area
        main_content = self._build_suggestions_list()
        
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
    
    def _build_suggestions_list(self) -> ft.Column:
        """Build suggestions list"""
        # Header with count and sort
        header = ft.Row(
            controls=[
                ft.Text(
                    f"Suggestions ({len(self.filtered_suggestions)})",
                    size=AppTheme.FONT_SIZE_TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    expand=True
                ),
                SortControl(
                    options=["Priority", "Effort", "Impact"],
                    on_sort_change=self._on_sort_change,
                    default_option="Priority"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Quick wins section
        quick_wins = [s for s in self.filtered_suggestions if s.effort.value == "low" and s.impact.value == "high"]
        
        controls = [header, ft.Container(height=AppTheme.SPACING_LARGE)]
        
        # Show quick wins if any
        if quick_wins:
            controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.FLASH_ON, color=AppTheme.SUCCESS),
                                    ft.Text(
                                        f"Quick Wins ({len(quick_wins)})",
                                        size=AppTheme.FONT_SIZE_LARGE,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppTheme.SUCCESS
                                    )
                                ],
                                spacing=8
                            ),
                            ft.Text(
                                "Low effort, high impact improvements",
                                size=AppTheme.FONT_SIZE_SMALL,
                                color=AppTheme.TEXT_SECONDARY
                            )
                        ],
                        spacing=4
                    ),
                    padding=ft.padding.only(bottom=AppTheme.SPACING_MEDIUM)
                )
            )
        
        # Suggestions cards
        if not self.filtered_suggestions:
            suggestions_content = create_empty_state(
                icon=ft.icons.FILTER_ALT_OFF,
                title="No Matching Suggestions",
                description="Try adjusting your filters"
            )
        else:
            suggestion_cards = [
                SuggestionCard(
                    suggestion=suggestion,
                    on_accept=self.on_accept,
                    on_dismiss=self.on_dismiss
                )
                for suggestion in self.filtered_suggestions
            ]
            
            suggestions_content = ft.ListView(
                controls=suggestion_cards,
                spacing=12,
                padding=AppTheme.SPACING_MEDIUM,
                expand=True
            )
        
        controls.append(suggestions_content)
        
        return ft.Column(
            controls=controls,
            spacing=0,
            expand=True
        )
    
    def _on_filter_change(self, filters: dict):
        """Handle filter changes"""
        self.filtered_suggestions = self.all_suggestions.copy()
        
        # Apply effort filter
        if filters.get("effort"):
            self.filtered_suggestions = [
                s for s in self.filtered_suggestions
                if s.effort.value in filters["effort"]
            ]
        
        # Apply impact filter
        if filters.get("impact"):
            self.filtered_suggestions = [
                s for s in self.filtered_suggestions
                if s.impact.value in filters["impact"]
            ]
        
        # Apply category filter
        if filters.get("category"):
            self.filtered_suggestions = [
                s for s in self.filtered_suggestions
                if s.category.value in filters["category"]
            ]
        
        self.content = self._build_content()
        self.update()
    
    def _on_search(self, query: str):
        """Handle search query"""
        if not query:
            self.filtered_suggestions = self.all_suggestions.copy()
        else:
            query_lower = query.lower()
            self.filtered_suggestions = [
                s for s in self.all_suggestions
                if query_lower in s.title.lower() or
                   query_lower in s.description.lower()
            ]
        
        self.content = self._build_content()
        self.update()
    
    def _on_sort_change(self, option: str, ascending: bool):
        """Handle sort changes"""
        if option == "Priority":
            self.filtered_suggestions.sort(
                key=lambda s: s.priority_score,
                reverse=not ascending
            )
        elif option == "Effort":
            effort_order = {"low": 0, "medium": 1, "high": 2}
            self.filtered_suggestions.sort(
                key=lambda s: effort_order.get(s.effort.value, 3),
                reverse=not ascending
            )
        elif option == "Impact":
            impact_order = {"low": 0, "medium": 1, "high": 2}
            self.filtered_suggestions.sort(
                key=lambda s: impact_order.get(s.impact.value, 3),
                reverse=not ascending
            )
        
        self.content = self._build_content()
        self.update()
    
    def refresh(self, suggestions: List[Suggestion]):
        """Refresh with new suggestions"""
        self.all_suggestions = suggestions
        self.filtered_suggestions = suggestions.copy()
        self.content = self._build_content()
        self.update()

# Made with Bob
