"""
Filter Components

Reusable filter panel components for filtering data.
"""

from typing import List, Optional, Callable, Dict
import flet as ft
from ..theme import AppTheme


class FilterPanel(ft.Container):
    """Reusable filter panel component"""

    def __init__(
        self,
        filters: Dict[str, List[str]],
        on_filter_change: Callable[[Dict[str, List[str]]], None],
        search_enabled: bool = True,
        on_search: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize filter panel

        Args:
            filters: Dictionary of filter name to list of options
            on_filter_change: Callback when filters change
            search_enabled: Whether to show search box
            on_search: Callback for search
        """
        self.filter_options = filters
        self.on_filter_change = on_filter_change
        self.search_enabled = search_enabled
        self.on_search = on_search
        self.selected_filters: Dict[str, List[str]] = {k: [] for k in filters.keys()}
        self.search_query = ""

        super().__init__(
            content=self._build_content(),
            bgcolor=AppTheme.BG_CARD,
            border=ft.Border.all(1, AppTheme.BORDER_COLOR),
            border_radius=AppTheme.RADIUS_MEDIUM,
            padding=16
        )

    def _build_content(self) -> ft.Column:
        """Build filter panel content"""
        controls = []

        # Search box
        if self.search_enabled:
            search_box = ft.TextField(
                label="Search",
                prefix_icon=ft.Icons.SEARCH,
                on_change=self._on_search_change,
                dense=True,
                border_color=AppTheme.BORDER_COLOR
            )
            controls.append(search_box)
            controls.append(ft.Container(height=16))

        # Filter sections
        for filter_name, options in self.filter_options.items():
            filter_section = self._build_filter_section(filter_name, options)
            controls.append(filter_section)
            controls.append(ft.Container(height=12))

        # Clear filters button
        clear_button = ft.TextButton(
            "Clear All Filters",
            icon=ft.Icons.CLEAR,
            on_click=self._clear_filters
        )
        controls.append(clear_button)

        # Active filter chips
        if any(self.selected_filters.values()):
            controls.append(ft.Container(height=8))
            controls.append(ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR))
            controls.append(ft.Container(height=8))
            controls.append(ft.Text("Active Filters:", size=12, weight=ft.FontWeight.BOLD))
            controls.append(self._build_active_chips())

        return ft.Column(
            controls=controls,
            spacing=0,
            scroll=ft.ScrollMode.AUTO
        )

    def _build_filter_section(self, name: str, options: List[str]) -> ft.Column:
        """Build a filter section"""
        # Section title
        title = ft.Text(
            name.replace("_", " ").title(),
            size=14,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )

        # Checkboxes for options
        checkboxes = []
        for option in options:
            checkbox = ft.Checkbox(
                label=option,
                value=option in self.selected_filters.get(name, []),
                on_change=lambda e, n=name, o=option: self._on_checkbox_change(n, o, e.control.value)
            )
            checkboxes.append(checkbox)

        return ft.Column(
            controls=[title] + checkboxes,
            spacing=4
        )

    def _build_active_chips(self) -> ft.Row:
        """Build active filter chips"""
        chips = []
        for filter_name, selected in self.selected_filters.items():
            for value in selected:
                chip = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                f"{filter_name}: {value}",
                                size=12,
                                color=AppTheme.TEXT_ON_PRIMARY
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=14,
                                icon_color=AppTheme.TEXT_ON_PRIMARY,
                                on_click=lambda e, n=filter_name, v=value: self._remove_filter(n, v)
                            )
                        ],
                        spacing=4
                    ),
                    bgcolor=AppTheme.PRIMARY,
                    border_radius=16,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4)
                )
                chips.append(chip)

        return ft.Row(
            controls=chips,
            spacing=8,
            wrap=True
        )

    def _on_checkbox_change(self, filter_name: str, option: str, checked: bool):
        """Handle checkbox change"""
        if checked:
            if option not in self.selected_filters[filter_name]:
                self.selected_filters[filter_name].append(option)
        else:
            if option in self.selected_filters[filter_name]:
                self.selected_filters[filter_name].remove(option)

        self._notify_change()

    def _on_search_change(self, e):
        """Handle search query change"""
        self.search_query = e.control.value
        if self.on_search:
            self.on_search(self.search_query)

    def _remove_filter(self, filter_name: str, value: str):
        """Remove a specific filter"""
        if value in self.selected_filters[filter_name]:
            self.selected_filters[filter_name].remove(value)
        self._notify_change()

    def _clear_filters(self, e):
        """Clear all filters"""
        self.selected_filters = {k: [] for k in self.filter_options.keys()}
        self.search_query = ""
        self._notify_change()

    def _notify_change(self):
        """Notify parent of filter changes"""
        self.content = self._build_content()
        self.update()
        self.on_filter_change(self.selected_filters)

    def get_active_filters(self) -> Dict[str, List[str]]:
        """Get currently active filters"""
        return {k: v for k, v in self.selected_filters.items() if v}


class SortControl(ft.Container):
    """Sort control component"""

    def __init__(
        self,
        options: List[str],
        on_sort_change: Callable[[str, bool], None],
        default_option: Optional[str] = None
    ):
        """
        Initialize sort control

        Args:
            options: List of sort options
            on_sort_change: Callback when sort changes (option, ascending)
            default_option: Default sort option
        """
        self.options = options
        self.on_sort_change = on_sort_change
        self.current_option = default_option or options[0]
        self.ascending = True

        super().__init__(
            content=self._build_content()
        )

    def _build_content(self) -> ft.Row:
        """Build sort control content"""
        dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(opt) for opt in self.options],
            value=self.current_option,
            on_select=self._on_option_change,
            dense=True,
            width=200
        )

        direction_button = ft.IconButton(
            icon=ft.Icons.ARROW_UPWARD if self.ascending else ft.Icons.ARROW_DOWNWARD,
            tooltip="Sort Direction",
            on_click=self._toggle_direction
        )

        return ft.Row(
            controls=[
                ft.Text("Sort by:", size=14, color=AppTheme.TEXT_SECONDARY),
                dropdown,
                direction_button
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.END
        )

    def _on_option_change(self, e):
        """Handle sort option change"""
        self.current_option = e.control.value
        self.on_sort_change(self.current_option, self.ascending)

    def _toggle_direction(self, e):
        """Toggle sort direction"""
        self.ascending = not self.ascending
        self.content = self._build_content()
        self.update()
        self.on_sort_change(self.current_option, self.ascending)


class SearchBar(ft.Container):
    """Search bar component"""

    def __init__(
        self,
        on_search: Callable[[str], None],
        placeholder: str = "Search...",
        width: Optional[int] = None
    ):
        """
        Initialize search bar

        Args:
            on_search: Callback when search query changes
            placeholder: Placeholder text
            width: Width of search bar
        """
        self.on_search = on_search
        self.placeholder = placeholder
        self.search_width = width

        super().__init__(
            content=self._build_content()
        )

    def _build_content(self) -> ft.TextField:
        """Build search bar content"""
        return ft.TextField(
            label=self.placeholder,
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.on_search(e.control.value),
            dense=True,
            border_color=AppTheme.BORDER_COLOR,
            width=self.search_width
        )

class ChipFilterRow(ft.Container):
    """Horizontal row of toggleable filter chips."""

    def __init__(
        self,
        label: str,
        options: List[str],
        color_map: Optional[Dict[str, str]] = None,
        on_change: Optional[Callable[[List[str]], None]] = None,
    ):
        self.label = label
        self.options = options
        self.color_map = color_map or {}
        self.on_change_cb = on_change
        self.selected: List[str] = []

        super().__init__(content=self._build())

    def _build(self) -> ft.Row:
        chips = []
        for opt in self.options:
            active = opt in self.selected
            color = self.color_map.get(opt, AppTheme.PRIMARY)

            chip = ft.Container(
                content=ft.Text(
                    opt.capitalize(),
                    size=12,
                    weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL,
                    color="white" if active else color,
                ),
                bgcolor=color if active else None,
                border=ft.Border.all(1.5, color),
                border_radius=16,
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                on_click=lambda _, o=opt: self._toggle(o),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
            chips.append(chip)

        return ft.Row(
            controls=[
                ft.Text(self.label, size=12, color=AppTheme.TEXT_SECONDARY,
                        weight=ft.FontWeight.BOLD),
            ] + chips,
            spacing=8,
            wrap=True,
        )

    def _toggle(self, option: str):
        if option in self.selected:
            self.selected.remove(option)
        else:
            self.selected.append(option)
        self.content = self._build()
        self.update()
        if self.on_change_cb:
            self.on_change_cb(list(self.selected))

    def clear(self):
        self.selected = []
        self.content = self._build()
        self.update()
