"""
Settings Page

Application settings and configuration.
"""

from typing import Optional, Callable
import flet as ft
from ..theme import AppTheme


class SettingsPage(ft.Container):
    """Settings page component"""
    
    def __init__(
        self,
        on_save: Optional[Callable] = None
    ):
        """
        Initialize settings page
        
        Args:
            on_save: Callback when settings are saved
        """
        self.on_save = on_save
        self.settings = {
            "enable_ai": True,
            "generate_docs": True,
            "perform_review": True,
            "generate_suggestions": True,
            "theme": "light"
        }
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _build_content(self) -> ft.Column:
        """Build settings page content"""
        # Header
        header = ft.Text(
            "Settings",
            size=AppTheme.FONT_SIZE_TITLE,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )
        
        # Analysis settings section
        analysis_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Analysis Options",
                            size=AppTheme.FONT_SIZE_LARGE,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
                        ft.Checkbox(
                            label="Enable AI-powered analysis",
                            value=self.settings["enable_ai"],
                            on_change=lambda e: self._update_setting("enable_ai", e.control.value)
                        ),
                        ft.Text(
                            "Use IBM Watson AI for deeper code analysis",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        ),
                        ft.Container(height=8),
                        ft.Checkbox(
                            label="Generate documentation",
                            value=self.settings["generate_docs"],
                            on_change=lambda e: self._update_setting("generate_docs", e.control.value)
                        ),
                        ft.Text(
                            "Auto-generate comprehensive documentation",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        ),
                        ft.Container(height=8),
                        ft.Checkbox(
                            label="Perform code review",
                            value=self.settings["perform_review"],
                            on_change=lambda e: self._update_setting("perform_review", e.control.value)
                        ),
                        ft.Text(
                            "Identify bugs, security issues, and improvements",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        ),
                        ft.Container(height=8),
                        ft.Checkbox(
                            label="Generate improvement suggestions",
                            value=self.settings["generate_suggestions"],
                            on_change=lambda e: self._update_setting("generate_suggestions", e.control.value)
                        ),
                        ft.Text(
                            "Get actionable improvement recommendations",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        )
                    ],
                    spacing=8
                ),
                padding=AppTheme.SPACING_LARGE
            ),
            elevation=2
        )
        
        # Appearance settings section
        appearance_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Appearance",
                            size=AppTheme.FONT_SIZE_LARGE,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
                        ft.RadioGroup(
                            content=ft.Column(
                                controls=[
                                    ft.Radio(value="light", label="Light Theme"),
                                    ft.Radio(value="dark", label="Dark Theme"),
                                    ft.Radio(value="system", label="System Default")
                                ]
                            ),
                            value=self.settings["theme"],
                            on_change=lambda e: self._update_setting("theme", e.control.value)
                        )
                    ],
                    spacing=8
                ),
                padding=AppTheme.SPACING_LARGE
            ),
            elevation=2
        )
        
        # About section
        about_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "About",
                            size=AppTheme.FONT_SIZE_LARGE,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
                        ft.Text(
                            "Codebase Analyzer v1.0.0",
                            size=AppTheme.FONT_SIZE_NORMAL
                        ),
                        ft.Text(
                            "A comprehensive tool for analyzing, documenting, and improving codebases",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        ),
                        ft.Container(height=8),
                        ft.TextButton(
                            "View Documentation",
                            icon=ft.icons.OPEN_IN_NEW
                        ),
                        ft.TextButton(
                            "Report an Issue",
                            icon=ft.icons.BUG_REPORT
                        )
                    ],
                    spacing=8
                ),
                padding=AppTheme.SPACING_LARGE
            ),
            elevation=2
        )
        
        # Save button
        save_button = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.SAVE),
                    ft.Text("Save Settings")
                ],
                spacing=8
            ),
            on_click=self._save_settings,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(
                    horizontal=AppTheme.SPACING_LARGE,
                    vertical=AppTheme.SPACING_MEDIUM
                ),
                bgcolor=AppTheme.PRIMARY,
                color=AppTheme.TEXT_ON_PRIMARY
            )
        )
        
        return ft.Column(
            controls=[
                header,
                ft.Container(height=AppTheme.SPACING_LARGE),
                analysis_section,
                ft.Container(height=AppTheme.SPACING_MEDIUM),
                appearance_section,
                ft.Container(height=AppTheme.SPACING_MEDIUM),
                about_section,
                ft.Container(height=AppTheme.SPACING_LARGE),
                save_button
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _update_setting(self, key: str, value):
        """Update a setting value"""
        self.settings[key] = value
    
    def _save_settings(self, e):
        """Save settings"""
        if self.on_save:
            self.on_save(self.settings)
    
    def load_settings(self, settings: dict):
        """Load settings from config"""
        self.settings.update(settings)
        self.content = self._build_content()
        self.update()

# Made with Bob
