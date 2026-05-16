"""
Chart Components

Simple chart components for data visualization.
"""

from typing import Dict, Optional
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
        total = sum(self.data.values())

        title_text = ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)

        default_colors = [AppTheme.PRIMARY, AppTheme.SECONDARY, AppTheme.SUCCESS, AppTheme.WARNING, AppTheme.ERROR,
                          "#78909C", "#AB47BC", "#26A69A", "#EC407A", "#8D6E63"]

        color_for = {}
        segments = []
        legend_items = []

        for i, (label, value) in enumerate(self.data.items()):
            color = self.colors.get(label, default_colors[i % len(default_colors)])
            color_for[label] = color
            percentage = (value / total * 100) if total > 0 else 0

            if value > 0:
                segments.append(ft.Container(bgcolor=color, expand=value, height=14, tooltip=f"{label}: {value}"))

            legend_items.append(ft.Row(controls=[
                ft.Container(width=12, height=12, bgcolor=color, border_radius=3),
                ft.Text(f"{label}", size=12, color=AppTheme.TEXT_PRIMARY),
                ft.Text(f"{value} ({percentage:.0f}%)", size=12, color=AppTheme.TEXT_SECONDARY),
            ], spacing=6))

        stacked_bar = ft.Container(
            content=ft.Row(controls=segments, spacing=1, expand=True),
            border_radius=7, clip_behavior=ft.ClipBehavior.HARD_EDGE, height=14,
        ) if segments else ft.Container(height=14, bgcolor="#EEEEEE", border_radius=7)

        return ft.Column(controls=[
            title_text,
            ft.Container(height=12),
            stacked_bar,
            ft.Container(height=10),
            ft.Column(controls=legend_items, spacing=4),
        ], spacing=0)


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
        title_text = ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)

        bars = []
        for label, value in self.data.items():
            fraction = (value / self.max_value) if self.max_value > 0 else 0

            bar_row = ft.Row(controls=[
                ft.Text(label.capitalize(), size=12, color=AppTheme.TEXT_SECONDARY, width=100),
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Container(bgcolor=self.color, expand=max(int(fraction * 100), 1),
                                     height=22, border_radius=4),
                        ft.Container(expand=max(100 - int(fraction * 100), 1)),
                    ], spacing=0, expand=True),
                    expand=True,
                ),
                ft.Text(str(value), size=12, color=AppTheme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD, width=40),
            ], spacing=8)
            bars.append(bar_row)

        return ft.Column(controls=[
            title_text,
            ft.Container(height=12),
            ft.Column(controls=bars, spacing=6),
        ], spacing=0)


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
                trend_icon = ft.Icons.TRENDING_UP if self.trend == "up" else \
                            ft.Icons.TRENDING_DOWN if self.trend == "down" else \
                            ft.Icons.TRENDING_FLAT
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
                alignment=ft.Alignment(0, 0)
            )
        ]

        return ft.Stack(controls=controls)

# Made with Bob
