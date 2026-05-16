"""
UI Theme Configuration

Defines colors, fonts, and styling constants for the application.
"""

from typing import Dict, Any
import flet as ft


class AppTheme:
    """Application theme configuration"""
    
    # Colors
    PRIMARY = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    SECONDARY = "#FF9800"
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    ERROR = "#F44336"
    INFO = "#2196F3"
    
    # Severity Colors
    CRITICAL = "#D32F2F"
    HIGH = "#F57C00"
    MEDIUM = "#FBC02D"
    LOW = "#7CB342"
    INFO_SEVERITY = "#1976D2"
    
    # Background Colors
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F5F5F5"
    BG_DARK = "#212121"
    BG_CARD = "#FFFFFF"
    
    # Text Colors
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"
    TEXT_ON_PRIMARY = "#FFFFFF"
    
    # Border Colors
    BORDER_COLOR = "#E0E0E0"
    DIVIDER_COLOR = "#EEEEEE"
    
    # Fonts
    FONT_FAMILY = "Roboto"
    FONT_SIZE_SMALL = 12
    FONT_SIZE_NORMAL = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_XLARGE = 20
    FONT_SIZE_TITLE = 24
    
    # Spacing
    SPACING_SMALL = 8
    SPACING_MEDIUM = 16
    SPACING_LARGE = 24
    SPACING_XLARGE = 32
    
    # Border Radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    
    # Shadows
    SHADOW_LIGHT = ft.BoxShadow(
        spread_radius=1,
        blur_radius=3,
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        offset=ft.Offset(0, 1)
    )
    
    SHADOW_MEDIUM = ft.BoxShadow(
        spread_radius=2,
        blur_radius=6,
        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
        offset=ft.Offset(0, 2)
    )
    
    SHADOW_HEAVY = ft.BoxShadow(
        spread_radius=3,
        blur_radius=10,
        color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
        offset=ft.Offset(0, 4)
    )
    
    @staticmethod
    def get_severity_color(severity: str) -> str:
        """Get color for severity level"""
        severity_map = {
            "critical": AppTheme.CRITICAL,
            "high": AppTheme.HIGH,
            "medium": AppTheme.MEDIUM,
            "low": AppTheme.LOW,
            "info": AppTheme.INFO_SEVERITY
        }
        return severity_map.get(severity.lower(), AppTheme.INFO_SEVERITY)
    
    @staticmethod
    def get_priority_color(priority: int) -> str:
        """Get color for priority score (0-100)"""
        if priority >= 80:
            return AppTheme.CRITICAL
        elif priority >= 60:
            return AppTheme.HIGH
        elif priority >= 40:
            return AppTheme.MEDIUM
        else:
            return AppTheme.LOW
    
    @staticmethod
    def get_light_theme() -> ft.Theme:
        """Get light theme configuration"""
        return ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY,
            use_material3=True
        )
    
    @staticmethod
    def get_dark_theme() -> ft.Theme:
        """Get dark theme configuration"""
        return ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY,
            use_material3=True,
            color_scheme=ft.ColorScheme(
                primary=AppTheme.PRIMARY,
                on_primary=AppTheme.TEXT_ON_PRIMARY,
                background=AppTheme.BG_DARK,
                surface=ft.Colors.GREY_900
            )
        )

# Made with Bob
