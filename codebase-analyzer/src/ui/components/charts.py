"""
Chart Components

Simple chart components for data visualization.
"""

import base64
import math
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

        default_colors = [AppTheme.PRIMARY, AppTheme.SECONDARY, AppTheme.SUCCESS, AppTheme.WARNING, AppTheme.ERROR,
                          "#78909C", "#AB47BC", "#26A69A", "#EC407A", "#8D6E63"]

        legend_items = []

        for i, (label, value) in enumerate(self.data.items()):
            color = self.colors.get(label, default_colors[i % len(default_colors)])
            percentage = (value / total * 100) if total > 0 else 0

            legend_items.append(ft.Row(controls=[
                ft.Container(width=12, height=12, bgcolor=color, border_radius=3),
                ft.Text(
                    f"{label}",
                    size=12,
                    color=AppTheme.TEXT_PRIMARY,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(f"{value} ({percentage:.0f}%)", size=12, color=AppTheme.TEXT_SECONDARY),
            ], spacing=6))

        controls = []
        if self.title:
            controls.append(
                ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
            )
            controls.append(ft.Container(height=12))

        controls.extend([
            self._build_circular_chart(),
            ft.Container(height=14),
            self._build_legend_grid(legend_items),
        ])

        return ft.Column(controls=controls, spacing=0)

    def _build_circular_chart(self) -> ft.Control:
        svg_markup = self._build_pie_chart_svg()
        svg_bytes = svg_markup.encode("utf-8")
        svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")

        return ft.Container(
            content=ft.Image(
                src=f"data:image/svg+xml;base64,{svg_base64}",
                width=180,
                height=180,
            ),
            alignment=ft.Alignment(0, 0),
            height=190,
        )

    def _build_legend_grid(self, legend_items: list[ft.Control]) -> ft.Control:
        if not legend_items:
            return ft.Container()

        column_count = 2 if len(legend_items) > 1 else 1
        items_per_column = math.ceil(len(legend_items) / column_count)
        legend_columns = []

        for column_index in range(column_count):
            start_index = column_index * items_per_column
            end_index = start_index + items_per_column
            legend_columns.append(
                ft.Container(
                    content=ft.Column(
                        controls=legend_items[start_index:end_index],
                        spacing=4,
                    ),
                    expand=True,
                )
            )

        return ft.Row(
            controls=legend_columns,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def _build_pie_chart_svg(self) -> str:
        total = sum(value for value in self.data.values() if value > 0)
        size = 180
        center = size / 2
        outer_radius = 72
        inner_radius = 34
        start_angle = -90.0

        default_colors = [
            AppTheme.PRIMARY,
            AppTheme.SECONDARY,
            AppTheme.SUCCESS,
            AppTheme.WARNING,
            AppTheme.ERROR,
            "#78909C",
            "#AB47BC",
            "#26A69A",
            "#EC407A",
            "#8D6E63",
        ]

        slices = []

        if total <= 0:
            slices.append(
                f'<circle cx="{center}" cy="{center}" r="{outer_radius}" fill="#EEEEEE" />'
            )
        else:
            for index, (label, value) in enumerate(self.data.items()):
                if value <= 0:
                    continue

                color = self.colors.get(label, default_colors[index % len(default_colors)])
                sweep_angle = (value / total) * 360.0
                if sweep_angle >= 359.999:
                    slices.append(
                        f'<circle cx="{center}" cy="{center}" r="{outer_radius}" fill="{color}" />'
                    )
                    break
                end_angle = start_angle + sweep_angle
                slices.append(
                    self._build_donut_slice_path(
                        center=center,
                        outer_radius=outer_radius,
                        inner_radius=inner_radius,
                        start_angle=start_angle,
                        end_angle=end_angle,
                        fill_color=color,
                    )
                )
                start_angle = end_angle

        slices.append(
            f'<circle cx="{center}" cy="{center}" r="{inner_radius}" fill="white" />'
        )

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}">'
            + "".join(slices)
            + "</svg>"
        )

    def _build_donut_slice_path(
        self,
        center: float,
        outer_radius: float,
        inner_radius: float,
        start_angle: float,
        end_angle: float,
        fill_color: str,
    ) -> str:
        start_outer_x, start_outer_y = self._polar_to_cartesian(center, outer_radius, start_angle)
        end_outer_x, end_outer_y = self._polar_to_cartesian(center, outer_radius, end_angle)
        start_inner_x, start_inner_y = self._polar_to_cartesian(center, inner_radius, start_angle)
        end_inner_x, end_inner_y = self._polar_to_cartesian(center, inner_radius, end_angle)
        large_arc_flag = 1 if end_angle - start_angle > 180 else 0

        return (
            f'<path d="M {start_outer_x:.3f} {start_outer_y:.3f} '
            f'A {outer_radius:.3f} {outer_radius:.3f} 0 {large_arc_flag} 1 {end_outer_x:.3f} {end_outer_y:.3f} '
            f'L {end_inner_x:.3f} {end_inner_y:.3f} '
            f'A {inner_radius:.3f} {inner_radius:.3f} 0 {large_arc_flag} 0 {start_inner_x:.3f} {start_inner_y:.3f} Z" '
            f'fill="{fill_color}" />'
        )

    def _polar_to_cartesian(self, center: float, radius: float, angle_in_degrees: float) -> tuple[float, float]:
        angle_in_radians = math.radians(angle_in_degrees)
        x_coordinate = center + radius * math.cos(angle_in_radians)
        y_coordinate = center + radius * math.sin(angle_in_radians)
        return x_coordinate, y_coordinate


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
