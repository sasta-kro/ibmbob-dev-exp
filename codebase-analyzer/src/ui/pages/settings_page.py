"""
Settings Page

Application settings and configuration — serves as the central place
to manage Watson AI credentials and analysis preferences.
"""

from typing import Optional, Callable, Dict, Any
import flet as ft
from ..theme import AppTheme


class SettingsPage(ft.Container):
    """Settings page component"""

    def __init__(
        self,
        config=None,
        on_save: Optional[Callable] = None
    ):
        self.config = config
        self.on_save = on_save

        if config:
            uc = config.user_config
            self.settings: Dict[str, Any] = {
                "watson_api_key": uc.get("watson_api_key", ""),
                "watson_url": uc.get("watson_url", "https://us-south.ml.cloud.ibm.com"),
                "watson_project_id": uc.get("watson_project_id", ""),
                "watson_model_id": uc.get("watson_model_id", "openai/gpt-oss-120b"),
                "watson_max_tokens": uc.get("watson_max_tokens", 2000),
                "watson_temperature": uc.get("watson_temperature", 0),
                "enable_ai": uc.get("enable_ai", True),
                "generate_docs": uc.get("generate_docs", True),
                "perform_review": uc.get("perform_review", True),
                "generate_suggestions": uc.get("generate_suggestions", True),
                "theme": uc.get("theme", "light"),
            }
        else:
            self.settings = {
                "watson_api_key": "",
                "watson_url": "https://us-south.ml.cloud.ibm.com",
                "watson_project_id": "",
                "watson_model_id": "openai/gpt-oss-120b",
                "watson_max_tokens": 2000,
                "watson_temperature": 0,
                "enable_ai": True,
                "generate_docs": True,
                "perform_review": True,
                "generate_suggestions": True,
                "theme": "light",
            }

        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )

    def _build_content(self) -> ft.Column:
        """Build settings page content"""
        header = ft.Text(
            "Settings",
            size=AppTheme.FONT_SIZE_TITLE,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )

        missing_creds = not self.settings.get("watson_api_key") or not self.settings.get("watson_project_id")

        # Watson credentials section
        self._api_key_field = ft.TextField(
            label="API Key",
            value=self.settings.get("watson_api_key", ""),
            password=True,
            can_reveal_password=True,
            on_change=lambda e: self._update_setting("watson_api_key", e.control.value),
            border_color=AppTheme.ERROR if not self.settings.get("watson_api_key") else None,
        )

        self._url_field = ft.TextField(
            label="Watson URL",
            value=self.settings.get("watson_url", ""),
            on_change=lambda e: self._update_setting("watson_url", e.control.value),
        )

        self._project_id_field = ft.TextField(
            label="Project ID",
            value=self.settings.get("watson_project_id", ""),
            on_change=lambda e: self._update_setting("watson_project_id", e.control.value),
            border_color=AppTheme.ERROR if not self.settings.get("watson_project_id") else None,
        )

        self._model_field = ft.TextField(
            label="Model ID",
            value=self.settings.get("watson_model_id", ""),
            on_change=lambda e: self._update_setting("watson_model_id", e.control.value),
        )

        self._max_tokens_field = ft.TextField(
            label="Max Tokens",
            value=str(self.settings.get("watson_max_tokens", 2000)),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._update_setting("watson_max_tokens", int(e.control.value) if e.control.value.isdigit() else 2000),
            width=200,
        )

        self._temperature_field = ft.TextField(
            label="Temperature",
            value=str(self.settings.get("watson_temperature", 0)),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._update_setting("watson_temperature", float(e.control.value) if self._is_float(e.control.value) else 0),
            width=200,
        )

        banner_controls = []
        if missing_creds:
            banner_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=AppTheme.WARNING, size=20),
                            ft.Text(
                                "Watson API key and Project ID are required for AI features.",
                                color=AppTheme.WARNING,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=8,
                    ),
                    bgcolor="#FFF3E0",
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    border_radius=8,
                )
            )

        watson_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.KEY, color=AppTheme.PRIMARY, size=20),
                                ft.Text(
                                    "IBM Watson AI Credentials",
                                    size=AppTheme.FONT_SIZE_LARGE,
                                    weight=ft.FontWeight.BOLD
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Text(
                            "Configure your IBM watsonx.ai credentials for AI-powered analysis",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        ),
                        ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
                        self._api_key_field,
                        self._url_field,
                        self._project_id_field,
                        ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
                        ft.Text(
                            "Model Configuration",
                            size=AppTheme.FONT_SIZE_NORMAL,
                            weight=ft.FontWeight.W_500
                        ),
                        self._model_field,
                        ft.Row(
                            controls=[
                                self._max_tokens_field,
                                self._temperature_field,
                            ],
                            spacing=16,
                        ),
                    ],
                    spacing=8
                ),
                padding=AppTheme.SPACING_LARGE
            ),
            elevation=2
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
                            content=ft.Text("View Documentation"),
                            icon=ft.Icons.OPEN_IN_NEW,
                            url="https://github.com/sasta-kro/ibmbob-dev-exp",
                        )
                    ],
                    spacing=8
                ),
                padding=AppTheme.SPACING_LARGE
            ),
            elevation=2
        )

        # Save button
        save_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SAVE),
                    ft.Text("Save Settings")
                ],
                spacing=8
            ),
            on_click=self._save_settings,
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

        return ft.Column(
            controls=[
                header,
                ft.Container(height=AppTheme.SPACING_LARGE),
                *banner_controls,
                ft.Container(height=AppTheme.SPACING_MEDIUM) if banner_controls else ft.Container(),
                watson_section,
                ft.Container(height=AppTheme.SPACING_MEDIUM),
                analysis_section,
                ft.Container(height=AppTheme.SPACING_MEDIUM),
                about_section,
                ft.Container(height=AppTheme.SPACING_LARGE),
                save_button
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    @staticmethod
    def _is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _update_setting(self, key: str, value):
        """Update a setting value"""
        self.settings[key] = value

    def _save_settings(self, e):
        """Save settings to user_config.json and notify callback"""
        if self.config:
            self.config.update_user_config(self.settings)

        if self.on_save:
            self.on_save(self.settings)

    def load_settings(self, settings: dict):
        """Load settings from config"""
        self.settings.update(settings)
        self.content = self._build_content()
        self.update()

# Made with Bob
