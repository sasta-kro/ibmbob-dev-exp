"""
Scan Progress Page

Page for selecting folders and monitoring analysis progress.
"""

from typing import Optional, Callable, List
import flet as ft
from ..theme import AppTheme
from ..components import ProgressCard


class ScanPage(ft.Container):
    """Scan progress page component"""
    
    def __init__(
        self,
        on_start_scan: Callable[[List[str], dict], None],
        on_select_folder: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
        """
        Initialize scan page
        
        Args:
            on_start_scan: Callback when scan starts
            on_select_folder: Callback that opens a folder picker
            on_cancel: Callback to cancel scan
        """
        self.on_start_scan = on_start_scan
        self.on_select_folder = on_select_folder
        self.on_cancel = on_cancel
        self.selected_paths: List[str] = []
        self.is_scanning = False
        self.option_values = {
            "enable_ai": True,
            "generate_docs": True,
            "perform_review": True,
            "generate_suggestions": True
        }
        self.progress_data = {
            "scanning": {"current": 0, "total": 0, "status": "Pending"},
            "analyzing": {"current": 0, "total": 0, "status": "Pending"},
            "documenting": {"current": 0, "total": 0, "status": "Pending"},
            "reviewing": {"current": 0, "total": 0, "status": "Pending"}
        }
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _build_content(self) -> ft.Column:
        """Build scan page content"""
        if not self.is_scanning:
            return self._build_setup_view()
        else:
            return self._build_progress_view()
    
    def _build_setup_view(self) -> ft.Column:
        """Build folder selection view"""
        # Header
        header = ft.Text(
            "Select Folders to Analyze",
            size=AppTheme.FONT_SIZE_TITLE,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )
        
        # Selected paths display
        paths_display = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Selected Folders:",
                        size=AppTheme.FONT_SIZE_NORMAL,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(
                        content=self._build_paths_list(),
                        border=ft.Border.all(1, AppTheme.BORDER_COLOR),
                        border_radius=AppTheme.RADIUS_MEDIUM,
                        padding=AppTheme.SPACING_MEDIUM,
                        height=200
                    ) if self.selected_paths else ft.Container(
                        content=ft.Text(
                            "No folders selected",
                            size=AppTheme.FONT_SIZE_NORMAL,
                            color=AppTheme.TEXT_SECONDARY,
                            italic=True
                        ),
                        border=ft.Border.all(1, AppTheme.BORDER_COLOR),
                        border_radius=AppTheme.RADIUS_MEDIUM,
                        padding=AppTheme.SPACING_MEDIUM,
                        height=200,
                        alignment=ft.Alignment(0, 0)
                    )
                ],
                spacing=12
            ),
            padding=ft.Padding(bottom=AppTheme.SPACING_LARGE)
        )
        
        # Action buttons
        action_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_OPEN),
                            ft.Text("Select Folder")
                        ],
                        spacing=8
                    ),
                    on_click=self._select_folder,
                    style=ft.ButtonStyle(
                        padding=ft.Padding(
                            left=AppTheme.SPACING_LARGE,
                            right=AppTheme.SPACING_LARGE,
                            top=AppTheme.SPACING_MEDIUM,
                            bottom=AppTheme.SPACING_MEDIUM
                        )
                    )
                ),
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PLAY_ARROW),
                            ft.Text("Start Analysis")
                        ],
                        spacing=8
                    ),
                    on_click=self._start_analysis,
                    disabled=len(self.selected_paths) == 0,
                    style=ft.ButtonStyle(
                        padding=ft.Padding(
                            left=AppTheme.SPACING_LARGE,
                            right=AppTheme.SPACING_LARGE,
                            top=AppTheme.SPACING_MEDIUM,
                            bottom=AppTheme.SPACING_MEDIUM
                        ),
                        bgcolor=AppTheme.PRIMARY,
                        color=AppTheme.TEXT_ON_PRIMARY
                    )
                )
            ],
            spacing=16
        )
        
        # Configuration options
        config_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Analysis Options",
                        size=AppTheme.FONT_SIZE_LARGE,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Checkbox(
                        label="Enable AI-powered analysis",
                        value=self.option_values["enable_ai"],
                        on_change=lambda e: self._update_option("enable_ai", e.control.value)
                    ),
                    ft.Checkbox(
                        label="Generate documentation",
                        value=self.option_values["generate_docs"],
                        on_change=lambda e: self._update_option("generate_docs", e.control.value)
                    ),
                    ft.Checkbox(
                        label="Perform code review",
                        value=self.option_values["perform_review"],
                        on_change=lambda e: self._update_option("perform_review", e.control.value)
                    ),
                    ft.Checkbox(
                        label="Generate improvement suggestions",
                        value=self.option_values["generate_suggestions"],
                        on_change=lambda e: self._update_option("generate_suggestions", e.control.value)
                    )
                ],
                spacing=8
            ),
            padding=ft.Padding(top=AppTheme.SPACING_XLARGE)
        )
        
        return ft.Column(
            controls=[
                header,
                ft.Container(height=AppTheme.SPACING_LARGE),
                paths_display,
                action_buttons,
                config_section
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _build_progress_view(self) -> ft.Column:
        """Build progress monitoring view"""
        # Header
        header = ft.Row(
            controls=[
                ft.Text(
                    "Analysis in Progress",
                    size=AppTheme.FONT_SIZE_TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    tooltip="Cancel Analysis",
                    on_click=self._cancel_scan,
                    icon_color=AppTheme.ERROR
                ) if self.on_cancel else ft.Container()
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Progress cards
        progress_cards = []
        
        stages = [
            ("scanning", "Scanning Files", ft.Icons.SEARCH),
            ("analyzing", "Analyzing Code", ft.Icons.CODE),
            ("documenting", "Generating Documentation", ft.Icons.DESCRIPTION),
            ("reviewing", "Reviewing Code", ft.Icons.BUG_REPORT)
        ]
        
        for stage_key, stage_title, stage_icon in stages:
            data = self.progress_data[stage_key]
            card = ProgressCard(
                title=stage_title,
                current=data["current"],
                total=data["total"],
                status=data["status"],
                show_cancel=False
            )
            progress_cards.append(card)
        
        # Log output
        log_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Activity Log",
                        size=AppTheme.FONT_SIZE_LARGE,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(
                        content=ft.ListView(
                            controls=[
                                ft.Text(
                                    "Analysis started...",
                                    size=AppTheme.FONT_SIZE_SMALL,
                                    color=AppTheme.TEXT_SECONDARY
                                )
                            ],
                            spacing=4,
                            padding=AppTheme.SPACING_SMALL
                        ),
                        border=ft.Border.all(1, AppTheme.BORDER_COLOR),
                        border_radius=AppTheme.RADIUS_MEDIUM,
                        height=200,
                        bgcolor=AppTheme.BG_SECONDARY
                    )
                ],
                spacing=12
            ),
            padding=ft.Padding(top=AppTheme.SPACING_LARGE)
        )
        
        return ft.Column(
            controls=[
                header,
                ft.Container(height=AppTheme.SPACING_LARGE),
                ft.Column(
                    controls=progress_cards,
                    spacing=16
                ),
                log_section
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _build_paths_list(self) -> ft.Column:
        """Build list of selected paths"""
        path_items = []
        for path in self.selected_paths:
            item = ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FOLDER, size=20, color=AppTheme.PRIMARY),
                    ft.Text(
                        path,
                        size=AppTheme.FONT_SIZE_NORMAL,
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        tooltip="Remove",
                        on_click=lambda _, p=path: self._remove_path(p)
                    )
                ],
                spacing=8
            )
            path_items.append(item)
        
        return ft.Column(
            controls=path_items,
            spacing=8,
            scroll=ft.ScrollMode.AUTO
        )
    
    def _select_folder(self, e):
        """Open folder picker dialog"""
        if self.on_select_folder:
            self.on_select_folder()
    
    def _remove_path(self, path: str):
        """Remove a selected path"""
        if path in self.selected_paths:
            self.selected_paths.remove(path)
        self.content = self._build_content()
        self.update()
    
    def _start_analysis(self, e):
        """Start the analysis"""
        if self.selected_paths:
            self.is_scanning = True
            self.content = self._build_content()
            self.update()
            self.on_start_scan(self.selected_paths, self.option_values.copy())
    
    def _cancel_scan(self, e):
        """Cancel the scan"""
        if self.on_cancel:
            self.on_cancel()
        self.is_scanning = False
        self.content = self._build_content()
        self.update()
    
    def update_progress(
        self,
        stage: str,
        current: int,
        total: int,
        status: str
    ):
        """Update progress for a specific stage"""
        if stage in self.progress_data:
            self.progress_data[stage] = {
                "current": current,
                "total": total,
                "status": status
            }
            if self.is_scanning:
                self.content = self._build_content()
                self.update()
    
    def _update_option(self, key: str, value: bool):
        """Update an analysis option."""
        self.option_values[key] = value
    
    def add_path(self, path: str):
        """Add a path to selected paths"""
        if path not in self.selected_paths:
            self.selected_paths.append(path)
            self.content = self._build_content()
            self.update()
    
    def reset(self):
        """Reset the scan page"""
        self.is_scanning = False
        self.selected_paths = []
        self.progress_data = {
            "scanning": {"current": 0, "total": 0, "status": "Pending"},
            "analyzing": {"current": 0, "total": 0, "status": "Pending"},
            "documenting": {"current": 0, "total": 0, "status": "Pending"},
            "reviewing": {"current": 0, "total": 0, "status": "Pending"}
        }
        self.content = self._build_content()
        self.update()

# Made with Bob
