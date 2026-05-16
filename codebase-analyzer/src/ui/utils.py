"""
UI Utility Functions

Helper functions for UI components and formatting.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import flet as ft


def format_number(num: int) -> str:
    """Format number with thousands separator"""
    return f"{num:,}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage value"""
    return f"{value:.{decimals}f}%"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def create_badge(
    text: str,
    color: str,
    text_color: str = "#FFFFFF",
    size: str = "small"
) -> ft.Container:
    """Create a badge component"""
    font_size = 10 if size == "small" else 12
    padding = 4 if size == "small" else 6
    
    return ft.Container(
        content=ft.Text(
            text,
            size=font_size,
            color=text_color,
            weight=ft.FontWeight.BOLD
        ),
        bgcolor=color,
        border_radius=12,
        padding=ft.Padding(
            left=padding + 4,
            right=padding + 4,
            top=padding,
            bottom=padding
        )
    )


def create_icon_button(
    icon: str,
    tooltip: str,
    on_click,
    color: Optional[str] = None,
    size: int = 20
) -> ft.IconButton:
    """Create an icon button with tooltip"""
    return ft.IconButton(
        icon=icon,
        tooltip=tooltip,
        on_click=on_click,
        icon_color=color,
        icon_size=size
    )


def create_divider(height: int = 1, color: str = "#E0E0E0") -> ft.Divider:
    """Create a divider"""
    return ft.Divider(height=height, color=color)


def create_spacer(height: int = 16) -> ft.Container:
    """Create a vertical spacer"""
    return ft.Container(height=height)


def create_card(
    content: ft.Control,
    padding: int = 16,
    elevation: int = 2
) -> ft.Card:
    """Create a card container"""
    return ft.Card(
        content=ft.Container(
            content=content,
            padding=padding
        ),
        elevation=elevation
    )


def create_loading_indicator(message: str = "Loading...") -> ft.Column:
    """Create a loading indicator with message"""
    return ft.Column(
        controls=[
            ft.ProgressRing(),
            ft.Text(message, size=14, color="#757575")
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16
    )


def create_empty_state(
    icon: str,
    title: str,
    description: str,
    action_text: Optional[str] = None,
    on_action = None
) -> ft.Column:
    """Create an empty state display"""
    controls = [
        ft.Icon(icon, size=64, color="#BDBDBD"),
        ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#757575"),
        ft.Text(description, size=14, color="#9E9E9E", text_align=ft.TextAlign.CENTER)
    ]
    
    if action_text and on_action:
        controls.append(
            ft.ElevatedButton(
                content=action_text,
                on_click=on_action,
                style=ft.ButtonStyle(
                    padding=ft.Padding(left=24, right=24, top=12, bottom=12)
                )
            )
        )
    
    return ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16
    )


def create_error_display(
    error_message: str,
    on_retry = None
) -> ft.Column:
    """Create an error display"""
    controls = [
        ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color="#F44336"),
        ft.Text("Error", size=20, weight=ft.FontWeight.BOLD, color="#F44336"),
        ft.Text(error_message, size=14, color="#757575", text_align=ft.TextAlign.CENTER)
    ]
    
    if on_retry:
        controls.append(
            ft.ElevatedButton(
                content="Retry",
                on_click=on_retry,
                icon=ft.Icons.REFRESH
            )
        )
    
    return ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16
    )


def show_snackbar(
    page: ft.Page,
    message: str,
    severity: str = "info",
    duration: int = 3000
):
    """Show a snackbar notification"""
    colors = {
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800",
        "info": "#2196F3"
    }
    
    snackbar = ft.SnackBar(
        content=ft.Text(message, color="#FFFFFF"),
        bgcolor=colors.get(severity, colors["info"]),
        duration=duration
    )
    page.snack_bar = snackbar
    snackbar.open = True
    page.update()


def create_stat_card(
    title: str,
    value: str,
    icon: str,
    color: str = "#2196F3",
    subtitle: Optional[str] = None
) -> ft.Card:
    """Create a statistics card"""
    content_controls = [
        ft.Row(
            controls=[
                ft.Icon(icon, size=32, color=color),
                ft.Column(
                    controls=[
                        ft.Text(title, size=12, color="#757575"),
                        ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color="#212121")
                    ],
                    spacing=4
                )
            ],
            spacing=16
        )
    ]
    
    if subtitle:
        content_controls.append(
            ft.Text(subtitle, size=12, color="#9E9E9E")
        )
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=content_controls,
                spacing=8
            ),
            padding=16
        ),
        elevation=2
    )

# Made with Bob
