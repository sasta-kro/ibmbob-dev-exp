"""
Chart Components

Simple chart components for data visualization.
"""

from typing import Dict, List, Optional
import flet as ft
from ..theme import AppTheme


class PieChart(ft.Container):
    """Simple pie chart component"""
    
    def __init__(
        self,
        title: str,
        data: Dict[str, int],
        colors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize pie chart
        
        Args:
            title: Chart title
            data: Dictionary of label to value
            colors: Optional dictionary of label to color
        """
        self.title = title
        self.data = data
        self.colors = colors or {}
        
        super().__init__(
            content=self._build_content(),
            padding=16
        )
    
    def _build_content(self) -> ft.Column:
        """Build chart content"""
        total = sum(self.data.values())
        
        # Title
        title_text = ft.Text(
            self.title,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )
        
        # Legend items
        legend_items = []
        default_colors = [
            AppTheme.PRIMARY,
            AppTheme.SECONDARY,
            AppTheme.SUCCESS,
            AppTheme.WARNING,
            AppTheme.ERROR
        ]
        
        for i, (label, value) in enumerate(self.data.items()):
            color = self.colors.get(label, default_colors[i % len(default_colors)])
            percentage = (value / total * 100) if total > 0 else 0
            
            legend_item = ft.Row(
                controls=[
                    ft.Container(
                        width=16,
                        height=16,
                        bgcolor=color,
                        border_radius=4
                    ),
                    ft.Text(
                        f"{label}: {value} ({percentage:.1f}%)",
                        size=14,
                        color=AppTheme.TEXT_PRIMARY,
                        expand=True
                    )
                ],
                spacing=8
            )
            legend_items.append(legend_item)
        
        return ft.Column(
            controls=[
                title_text,
                ft.Container(height=16),
                ft.Column(
                    controls=legend_items,
                    spacing=8
                )
            ],
            spacing=0
        )


class BarChart(ft.Container):
    """Simple bar chart component"""
    
    def __init__(
        self,
        title: str,
        data: Dict[str, int],
        color: str = AppTheme.PRIMARY,
        max_value: Optional[int] = None
    ):
        """
        Initialize bar chart
        
        Args:
            title: Chart title
            data: Dictionary of label to value
            color: Bar color
            max_value: Maximum value for scaling
        """
        self.title = title
        self.data = data
        self.color = color
        self.max_value = max_value or max(data.values()) if data else 100
        
        super().__init__(
            content=self._build_content(),
            padding=16
        )
    
    def _build_content(self) -> ft.Column:
        """Build chart content"""
        # Title
        title_text = ft.Text(
            self.title,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )
        
        # Bars
        bars = []
        for label, value in self.data.items():
            bar_width = (value / self.max_value * 100) if self.max_value > 0 else 0
            
            bar_row = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                label,
                                size=12,
                                color=AppTheme.TEXT_SECONDARY,
                                width=100
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(value),
                                    size=12,
                                    color=AppTheme.TEXT_ON_PRIMARY
                                ),
                                bgcolor=self.color,
                                width=bar_width * 2,
                                height=24,
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=8),
                                alignment=ft.alignment.center_left
                            )
                        ],
                        spacing=8
                    )
                ],
                spacing=4
            )
            bars.append(bar_row)
        
        return ft.Column(
            controls=[
                title_text,
                ft.Container(height=16),
                ft.Column(
                    controls=bars,
                    spacing=8
                )
            ],
            spacing=0
        )


class MetricCard(ft.Card):
    """Metric display card"""
    
    def __init__(
        self,
        title: str,
        value: str,
        icon: str,
        color: str = AppTheme.PRIMARY,
        subtitle: Optional[str] = None,
        trend: Optional[str] = None
    ):
        """
        Initialize metric card
        
        Args:
            title: Metric title
            value: Metric value
            icon: Icon name
            color: Icon color
            subtitle: Optional subtitle
            trend: Optional trend indicator (up/down/neutral)
        """
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.subtitle = subtitle
        self.trend = trend
        
        super().__init__(
            content=self._build_content(),
            elevation=2
        )
    
    def _build_content(self) -> ft.Container:
        """Build card content"""
        # Icon and value
        main_row = ft.Row(
            controls=[
                ft.Icon(
                    self.icon,
                    size=40,
                    color=self.color
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self.title,
                            size=12,
                            color=AppTheme.TEXT_SECONDARY
                        ),
                        ft.Text(
                            self.value,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        )
                    ],
                    spacing=4,
                    expand=True
                )
            ],
            spacing=16
        )
        
        controls = [main_row]
        
        # Subtitle or trend
        if self.subtitle or self.trend:
            bottom_controls = []
            
            if self.trend:
                trend_icon = ft.icons.TRENDING_UP if self.trend == "up" else \
                            ft.icons.TRENDING_DOWN if self.trend == "down" else \
                            ft.icons.TRENDING_FLAT
                trend_color = AppTheme.SUCCESS if self.trend == "up" else \
                             AppTheme.ERROR if self.trend == "down" else \
                             AppTheme.TEXT_SECONDARY
                
                bottom_controls.append(
                    ft.Icon(trend_icon, size=16, color=trend_color)
                )
            
            if self.subtitle:
                bottom_controls.append(
                    ft.Text(
                        self.subtitle,
                        size=12,
                        color=AppTheme.TEXT_SECONDARY,
                        expand=True
                    )
                )
            
            controls.append(
                ft.Container(height=8)
            )
            controls.append(
                ft.Row(
                    controls=bottom_controls,
                    spacing=8
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=0
            ),
            padding=16
        )


class ProgressRing(ft.Container):
    """Progress ring with percentage"""
    
    def __init__(
        self,
        value: float,
        size: int = 100,
        color: str = AppTheme.PRIMARY,
        label: Optional[str] = None
    ):
        """
        Initialize progress ring
        
        Args:
            value: Progress value (0-100)
            size: Ring size
            color: Ring color
            label: Optional label
        """
        self.value = value
        self.size = size
        self.color = color
        self.label = label
        
        super().__init__(
            content=self._build_content(),
            width=size,
            height=size
        )
    
    def _build_content(self) -> ft.Stack:
        """Build progress ring content"""
        controls = [
            ft.ProgressRing(
                value=self.value / 100,
                width=self.size,
                height=self.size,
                stroke_width=8,
                color=self.color
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{self.value:.0f}%",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        ft.Text(
                            self.label,
                            size=10,
                            color=AppTheme.TEXT_SECONDARY
                        ) if self.label else ft.Container()
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0
                ),
                alignment=ft.alignment.center
            )
        ]
        
        return ft.Stack(controls=controls)

# Made with Bob
