"""
Card Components

Reusable card components for displaying findings, suggestions, and other data.
"""

from typing import Optional, List, Callable
import flet as ft
from ...models.finding import Finding, FindingSeverity, FindingCategory
from ...models.suggestion import Suggestion, EffortLevel, ImpactLevel
from ..theme import AppTheme
from ..utils import create_badge, truncate_text


class FindingCard(ft.Card):
    """Card component for displaying a code review finding"""
    
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
        
        super().__init__(
            content=self._build_content(),
            elevation=2
        )
    
    def _build_content(self) -> ft.Container:
        """Build card content"""
        severity_color = AppTheme.get_severity_color(self.finding.severity.value)
        
        # Header with severity badge and title
        header = ft.Row(
            controls=[
                create_badge(
                    self.finding.severity.value.upper(),
                    severity_color
                ),
                ft.Text(
                    self.finding.title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.icons.EXPAND_MORE if not self.is_expanded else ft.icons.EXPAND_LESS,
                    on_click=self._toggle_expand,
                    tooltip="Expand/Collapse"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # File location
        location = ft.Text(
            f"{self.finding.file_path}:{self.finding.line_number or 'N/A'}",
            size=12,
            color="#757575"
        )
        
        # Category badge
        category_badge = create_badge(
            self.finding.category.value,
            "#9E9E9E",
            size="small"
        )
        
        # Description
        description = ft.Text(
            truncate_text(self.finding.description, 200) if not self.is_expanded else self.finding.description,
            size=14,
            color="#212121"
        )
        
        controls = [header, location, category_badge, description]
        
        # Expandable content
        if self.is_expanded:
            if self.finding.evidence:
                controls.append(ft.Container(height=8))
                controls.append(ft.Text("Evidence:", size=12, weight=ft.FontWeight.BOLD))
                controls.append(
                    ft.Container(
                        content=ft.Text(
                            self.finding.evidence,
                            size=12,
                            font_family="monospace"
                        ),
                        bgcolor="#F5F5F5",
                        padding=8,
                        border_radius=4
                    )
                )
            
            if self.finding.suggestion:
                controls.append(ft.Container(height=8))
                controls.append(ft.Text("Suggested Fix:", size=12, weight=ft.FontWeight.BOLD))
                controls.append(ft.Text(self.finding.suggestion, size=14))
            
            # Action buttons
            if self.on_resolve or self.on_ignore:
                action_buttons = []
                if self.on_resolve:
                    action_buttons.append(
                        ft.ElevatedButton(
                            "Mark Resolved",
                            icon=ft.icons.CHECK_CIRCLE,
                            on_click=lambda _: self.on_resolve(self.finding)
                        )
                    )
                if self.on_ignore:
                    action_buttons.append(
                        ft.OutlinedButton(
                            "Ignore",
                            icon=ft.icons.CANCEL,
                            on_click=lambda _: self.on_ignore(self.finding)
                        )
                    )
                
                controls.append(ft.Container(height=8))
                controls.append(
                    ft.Row(
                        controls=action_buttons,
                        spacing=8
                    )
                )
        
        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=8
            ),
            padding=16
        )
    
    def _toggle_expand(self, e):
        """Toggle card expansion"""
        self.is_expanded = not self.is_expanded
        self.content = self._build_content()
        self.update()


class SuggestionCard(ft.Card):
    """Card component for displaying an improvement suggestion"""
    
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
        
        super().__init__(
            content=self._build_content(),
            elevation=2
        )
    
    def _build_content(self) -> ft.Container:
        """Build card content"""
        priority_color = AppTheme.get_priority_color(self.suggestion.priority_score)
        
        # Header with priority and title
        header = ft.Row(
            controls=[
                create_badge(
                    f"Priority: {self.suggestion.priority_score}",
                    priority_color
                ),
                ft.Text(
                    self.suggestion.title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.icons.EXPAND_MORE if not self.is_expanded else ft.icons.EXPAND_LESS,
                    on_click=self._toggle_expand,
                    tooltip="Expand/Collapse"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Effort and Impact badges
        badges = ft.Row(
            controls=[
                create_badge(
                    f"Effort: {self.suggestion.effort.value}",
                    "#9E9E9E",
                    size="small"
                ),
                create_badge(
                    f"Impact: {self.suggestion.impact.value}",
                    "#2196F3",
                    size="small"
                ),
                create_badge(
                    self.suggestion.category.value,
                    "#FF9800",
                    size="small"
                )
            ],
            spacing=8
        )
        
        # Description
        description = ft.Text(
            truncate_text(self.suggestion.description, 200) if not self.is_expanded else self.suggestion.description,
            size=14,
            color="#212121"
        )
        
        controls = [header, badges, description]
        
        # Expandable content
        if self.is_expanded:
            # Benefits
            if self.suggestion.benefits:
                controls.append(ft.Container(height=8))
                controls.append(ft.Text("Benefits:", size=12, weight=ft.FontWeight.BOLD))
                for benefit in self.suggestion.benefits:
                    controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.CHECK_CIRCLE, size=16, color="#4CAF50"),
                                ft.Text(benefit, size=14, expand=True)
                            ],
                            spacing=8
                        )
                    )
            
            # Implementation steps
            if self.suggestion.implementation_steps:
                controls.append(ft.Container(height=8))
                controls.append(ft.Text("Implementation Steps:", size=12, weight=ft.FontWeight.BOLD))
                for i, step in enumerate(self.suggestion.implementation_steps, 1):
                    controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(f"{i}.", size=14, weight=ft.FontWeight.BOLD),
                                ft.Column(
                                    controls=[
                                        ft.Text(step.description, size=14),
                                        ft.Text(
                                            f"Estimated time: {step.estimated_time}",
                                            size=12,
                                            color="#757575"
                                        ) if step.estimated_time else ft.Container()
                                    ],
                                    spacing=4,
                                    expand=True
                                )
                            ],
                            spacing=8
                        )
                    )
            
            # Action buttons
            if self.on_accept or self.on_dismiss:
                action_buttons = []
                if self.on_accept:
                    action_buttons.append(
                        ft.ElevatedButton(
                            "Accept",
                            icon=ft.icons.CHECK,
                            on_click=lambda _: self.on_accept(self.suggestion)
                        )
                    )
                if self.on_dismiss:
                    action_buttons.append(
                        ft.OutlinedButton(
                            "Dismiss",
                            icon=ft.icons.CLOSE,
                            on_click=lambda _: self.on_dismiss(self.suggestion)
                        )
                    )
                
                controls.append(ft.Container(height=8))
                controls.append(
                    ft.Row(
                        controls=action_buttons,
                        spacing=8
                    )
                )
        
        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=8
            ),
            padding=16
        )
    
    def _toggle_expand(self, e):
        """Toggle card expansion"""
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
                        icon=ft.icons.CANCEL,
                        on_click=lambda _: self.on_cancel()
                    ),
                    alignment=ft.alignment.center_right
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
