"""
Home Page

Welcome page with project selection and recent projects.
"""

from typing import Optional, Callable, List
import flet as ft
from ..theme import AppTheme
from ..utils import create_empty_state, create_stat_card


class HomePage(ft.Container):
    """Home page component"""
    
    def __init__(
        self,
        on_new_analysis: Callable,
        recent_projects: Optional[List[dict]] = None
    ):
        """
        Initialize home page
        
        Args:
            on_new_analysis: Callback for starting new analysis
            recent_projects: List of recent project data
        """
        self.on_new_analysis = on_new_analysis
        self.recent_projects = recent_projects or []
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _build_content(self) -> ft.Column:
        """Build home page content"""
        # Welcome header
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Codebase Analyzer",
                        size=AppTheme.FONT_SIZE_TITLE + 8,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.PRIMARY
                    ),
                    ft.Text(
                        "Analyze, document, and improve your codebase",
                        size=AppTheme.FONT_SIZE_LARGE,
                        color=AppTheme.TEXT_SECONDARY
                    )
                ],
                spacing=8
            ),
            padding=ft.padding.only(bottom=AppTheme.SPACING_XLARGE)
        )
        
        # New analysis button
        new_analysis_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ADD_CIRCLE_OUTLINE, size=24),
                        ft.Text(
                            "Start New Analysis",
                            size=AppTheme.FONT_SIZE_LARGE,
                            weight=ft.FontWeight.BOLD
                        )
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                on_click=lambda _: self.on_new_analysis(),
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(
                        horizontal=AppTheme.SPACING_XLARGE,
                        vertical=AppTheme.SPACING_LARGE
                    ),
                    bgcolor=AppTheme.PRIMARY,
                    color=AppTheme.TEXT_ON_PRIMARY
                ),
                height=80
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.only(bottom=AppTheme.SPACING_XLARGE)
        )
        
        controls = [header, new_analysis_button]
        
        # Recent projects section
        if self.recent_projects:
            controls.append(self._build_recent_projects())
        else:
            controls.append(self._build_empty_state())
        
        # Features section
        controls.append(self._build_features_section())
        
        return ft.Column(
            controls=controls,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _build_recent_projects(self) -> ft.Container:
        """Build recent projects section"""
        project_cards = []
        
        for project in self.recent_projects[:5]:  # Show max 5 recent
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.icons.FOLDER,
                                        size=32,
                                        color=AppTheme.PRIMARY
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                project.get("name", "Unknown Project"),
                                                size=AppTheme.FONT_SIZE_LARGE,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Text(
                                                project.get("path", ""),
                                                size=AppTheme.FONT_SIZE_SMALL,
                                                color=AppTheme.TEXT_SECONDARY
                                            )
                                        ],
                                        spacing=4,
                                        expand=True
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_FORWARD,
                                        tooltip="Open Project",
                                        on_click=lambda _, p=project: self._open_project(p)
                                    )
                                ],
                                spacing=16
                            ),
                            ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        f"Files: {project.get('file_count', 0)}",
                                        size=AppTheme.FONT_SIZE_SMALL,
                                        color=AppTheme.TEXT_SECONDARY
                                    ),
                                    ft.Text(
                                        f"Findings: {project.get('findings_count', 0)}",
                                        size=AppTheme.FONT_SIZE_SMALL,
                                        color=AppTheme.TEXT_SECONDARY
                                    ),
                                    ft.Text(
                                        f"Last analyzed: {project.get('last_analyzed', 'Never')}",
                                        size=AppTheme.FONT_SIZE_SMALL,
                                        color=AppTheme.TEXT_SECONDARY
                                    )
                                ],
                                spacing=16
                            )
                        ],
                        spacing=12
                    ),
                    padding=16
                ),
                elevation=2
            )
            project_cards.append(card)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Recent Projects",
                        size=AppTheme.FONT_SIZE_XLARGE,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY
                    ),
                    ft.Container(height=16),
                    ft.Column(
                        controls=project_cards,
                        spacing=12
                    )
                ],
                spacing=0
            ),
            padding=ft.padding.only(bottom=AppTheme.SPACING_XLARGE)
        )
    
    def _build_empty_state(self) -> ft.Container:
        """Build empty state when no recent projects"""
        return ft.Container(
            content=create_empty_state(
                icon=ft.icons.FOLDER_OPEN,
                title="No Recent Projects",
                description="Start a new analysis to see your projects here"
            ),
            padding=ft.padding.symmetric(vertical=AppTheme.SPACING_XLARGE),
            alignment=ft.alignment.center
        )
    
    def _build_features_section(self) -> ft.Container:
        """Build features showcase section"""
        features = [
            {
                "icon": ft.icons.SEARCH,
                "title": "Code Analysis",
                "description": "Deep analysis of your codebase structure and patterns"
            },
            {
                "icon": ft.icons.DESCRIPTION,
                "title": "Documentation",
                "description": "Auto-generate comprehensive documentation"
            },
            {
                "icon": ft.icons.BUG_REPORT,
                "title": "Code Review",
                "description": "Identify bugs, security issues, and improvements"
            },
            {
                "icon": ft.icons.LIGHTBULB,
                "title": "Suggestions",
                "description": "Get actionable improvement recommendations"
            }
        ]
        
        feature_cards = []
        for feature in features:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                feature["icon"],
                                size=48,
                                color=AppTheme.PRIMARY
                            ),
                            ft.Text(
                                feature["title"],
                                size=AppTheme.FONT_SIZE_LARGE,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                feature["description"],
                                size=AppTheme.FONT_SIZE_NORMAL,
                                color=AppTheme.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12
                    ),
                    padding=AppTheme.SPACING_LARGE,
                    width=250
                ),
                elevation=1
            )
            feature_cards.append(card)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Features",
                        size=AppTheme.FONT_SIZE_XLARGE,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY
                    ),
                    ft.Container(height=16),
                    ft.Row(
                        controls=feature_cards,
                        spacing=16,
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                spacing=0
            ),
            padding=ft.padding.only(top=AppTheme.SPACING_XLARGE)
        )
    
    def _open_project(self, project: dict):
        """Open a recent project"""
        # This would be implemented to load the project
        pass
    
    def refresh(self, recent_projects: Optional[List[dict]] = None):
        """Refresh the page with updated data"""
        if recent_projects is not None:
            self.recent_projects = recent_projects
        self.content = self._build_content()
        self.update()

# Made with Bob
