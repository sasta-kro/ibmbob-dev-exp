"""
Scan Progress Page

Page for selecting folders and monitoring analysis progress.
"""

import os
from typing import Optional, Callable, List
import flet as ft
from ..theme import AppTheme
from ..components import ProgressCard


FILE_EXT_ICONS = {
    ".py": (ft.Icons.CODE, "#3572A5"),
    ".js": (ft.Icons.JAVASCRIPT, "#F7DF1E"),
    ".ts": (ft.Icons.CODE, "#3178C6"),
    ".tsx": (ft.Icons.CODE, "#3178C6"),
    ".jsx": (ft.Icons.JAVASCRIPT, "#61DAFB"),
    ".html": (ft.Icons.WEB, "#E34F26"),
    ".css": (ft.Icons.PALETTE, "#1572B6"),
    ".json": (ft.Icons.DATA_OBJECT, "#A0A0A0"),
    ".md": (ft.Icons.ARTICLE, "#083FA1"),
    ".yml": (ft.Icons.SETTINGS, "#CB171E"),
    ".yaml": (ft.Icons.SETTINGS, "#CB171E"),
    ".sql": (ft.Icons.STORAGE, "#336791"),
    ".sh": (ft.Icons.TERMINAL, "#4EAA25"),
    ".go": (ft.Icons.CODE, "#00ADD8"),
    ".rs": (ft.Icons.CODE, "#DEA584"),
    ".java": (ft.Icons.CODE, "#B07219"),
    ".rb": (ft.Icons.CODE, "#CC342D"),
    ".php": (ft.Icons.CODE, "#4F5D95"),
    ".c": (ft.Icons.CODE, "#555555"),
    ".cpp": (ft.Icons.CODE, "#F34B7D"),
    ".h": (ft.Icons.CODE, "#555555"),
    ".swift": (ft.Icons.CODE, "#FA7343"),
}

PHASE_CONFIG = {
    "scanning": {
        "icon": ft.Icons.FOLDER_OPEN,
        "color": "#2196F3",
        "bg": "#E3F2FD",
        "label": "Scanning",
        "verb": "Reading",
    },
    "analyzing": {
        "icon": ft.Icons.PSYCHOLOGY,
        "color": "#9C27B0",
        "bg": "#F3E5F5",
        "label": "Analyzing",
        "verb": "Studying",
    },
    "documenting": {
        "icon": ft.Icons.AUTO_STORIES,
        "color": "#FF9800",
        "bg": "#FFF3E0",
        "label": "Documenting",
        "verb": "Writing docs for",
    },
    "reviewing": {
        "icon": ft.Icons.BUG_REPORT,
        "color": "#4CAF50",
        "bg": "#E8F5E9",
        "label": "Reviewing",
        "verb": "Checking",
    },
}


def _icon_for_file(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    return FILE_EXT_ICONS.get(ext, (ft.Icons.INSERT_DRIVE_FILE, "#78909C"))


class ScanPage(ft.Container):

    def __init__(
        self,
        on_start_scan: Callable[[List[str], dict], None],
        on_select_folder: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ):
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
        self._current_phase = "scanning"
        self._current_file = ""
        self._recent_files: List[str] = []
        self._file_count = 0

        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )

    def _build_content(self) -> ft.Column:
        if not self.is_scanning:
            return self._build_setup_view()
        return self._build_progress_view()

    # ── Setup View ──────────────────────────────────────────────

    def _build_setup_view(self) -> ft.Column:
        header = ft.Text(
            "Select Folders to Analyze",
            size=AppTheme.FONT_SIZE_TITLE,
            weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY
        )

        paths_display = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Selected Folders:", size=AppTheme.FONT_SIZE_NORMAL, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self._build_paths_list(),
                        border=ft.Border.all(1, AppTheme.BORDER_COLOR),
                        border_radius=AppTheme.RADIUS_MEDIUM,
                        padding=AppTheme.SPACING_MEDIUM,
                        height=200
                    ) if self.selected_paths else ft.Container(
                        content=ft.Text("No folders selected", size=AppTheme.FONT_SIZE_NORMAL,
                                        color=AppTheme.TEXT_SECONDARY, italic=True),
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

        browse_button = ft.ElevatedButton(
            content=ft.Row(controls=[ft.Icon(ft.Icons.FOLDER_OPEN), ft.Text("Browse Folder")], spacing=8),
            on_click=self._on_browse_click,
            style=ft.ButtonStyle(
                padding=ft.Padding(left=AppTheme.SPACING_LARGE, right=AppTheme.SPACING_LARGE,
                                   top=AppTheme.SPACING_MEDIUM, bottom=AppTheme.SPACING_MEDIUM),
                bgcolor=AppTheme.PRIMARY, color=AppTheme.TEXT_ON_PRIMARY
            )
        )

        self.path_input = ft.TextField(
            label="Or paste folder path", hint_text="/path/to/project",
            prefix_icon=ft.Icons.FOLDER, expand=True,
            border_color=AppTheme.BORDER_COLOR,
            on_submit=lambda e: self._add_typed_path(e), text_size=13,
        )

        path_input_row = ft.Column(
            controls=[
                browse_button,
                ft.Row(controls=[
                    self.path_input,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=lambda _: self._add_typed_path(None), tooltip="Add path")
                ], spacing=8)
            ],
            spacing=12
        )

        start_button = ft.Button(
            content=ft.Row(controls=[ft.Icon(ft.Icons.PLAY_ARROW), ft.Text("Start Analysis")], spacing=8),
            on_click=self._start_analysis,
            disabled=len(self.selected_paths) == 0,
            style=ft.ButtonStyle(
                padding=ft.Padding(left=AppTheme.SPACING_LARGE, right=AppTheme.SPACING_LARGE,
                                   top=AppTheme.SPACING_MEDIUM, bottom=AppTheme.SPACING_MEDIUM),
                bgcolor=AppTheme.PRIMARY, color=AppTheme.TEXT_ON_PRIMARY
            )
        )

        config_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Analysis Options", size=AppTheme.FONT_SIZE_LARGE, weight=ft.FontWeight.BOLD),
                    ft.Checkbox(label="Enable AI-powered analysis", value=self.option_values["enable_ai"],
                                on_change=lambda e: self._update_option("enable_ai", e.control.value)),
                    ft.Checkbox(label="Generate documentation", value=self.option_values["generate_docs"],
                                on_change=lambda e: self._update_option("generate_docs", e.control.value)),
                    ft.Checkbox(label="Perform code review", value=self.option_values["perform_review"],
                                on_change=lambda e: self._update_option("perform_review", e.control.value)),
                    ft.Checkbox(label="Generate improvement suggestions", value=self.option_values["generate_suggestions"],
                                on_change=lambda e: self._update_option("generate_suggestions", e.control.value)),
                ],
                spacing=8
            ),
            padding=ft.Padding(top=AppTheme.SPACING_XLARGE)
        )

        return ft.Column(
            controls=[header, ft.Container(height=AppTheme.SPACING_LARGE), paths_display,
                      ft.Column(controls=[path_input_row, start_button], spacing=16), config_section],
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True
        )

    # ── Progress View ───────────────────────────────────────────

    def _build_progress_view(self) -> ft.Column:
        phase = PHASE_CONFIG.get(self._current_phase, PHASE_CONFIG["scanning"])
        phase_data = self.progress_data.get(self._current_phase, {"current": 0, "total": 0})
        total_pct = self._get_overall_progress()
        file_icon, file_color = _icon_for_file(self._current_file) if self._current_file else (ft.Icons.HOURGLASS_EMPTY, "#9E9E9E")

        # ── Current file hero ──
        spinning_ring = ft.ProgressRing(
            width=100, height=100, stroke_width=4,
            color=phase["color"],
        )
        center_icon = ft.Container(
            content=ft.Icon(file_icon, size=40, color=file_color),
            width=100, height=100,
            alignment=ft.Alignment(0, 0),
        )
        hero_circle = ft.Container(
            content=ft.Stack(controls=[spinning_ring, center_icon], width=100, height=100),
            width=120, height=120,
            alignment=ft.Alignment(0, 0),
            border_radius=60,
            bgcolor=phase["bg"],
            animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
        )

        file_display_name = self._current_file or "Preparing..."
        hero_filename = ft.Text(
            file_display_name,
            size=22, weight=ft.FontWeight.BOLD,
            color=AppTheme.TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER,
            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
            width=500,
        )

        verb = phase["verb"]
        hero_action = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(phase["icon"], size=16, color=phase["color"]),
                    ft.Text(f"{verb} {file_display_name}", size=14,
                            color=phase["color"], italic=True,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, width=400),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        hero_counter = ft.Text(
            f"{phase_data['current']} / {phase_data['total']}" if phase_data["total"] > 0 else "",
            size=13, color=AppTheme.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER,
        )

        hero = ft.Container(
            content=ft.Column(
                controls=[hero_circle, hero_filename, hero_action, hero_counter],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.Padding(top=30, bottom=20, left=0, right=0),
            alignment=ft.Alignment(0, 0),
        )

        # ── Overall progress bar ──
        bar_section = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Text("Overall", size=12, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_SECONDARY),
                    ft.Text(f"{total_pct:.0f}%", size=12, weight=ft.FontWeight.BOLD, color=phase["color"]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.ProgressBar(value=total_pct / 100, color=phase["color"], bgcolor="#EEEEEE", height=8),
                    border_radius=4, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
            ], spacing=6),
            padding=ft.Padding(left=24, right=24, top=0, bottom=16),
        )

        # ── Phase steps ──
        phases_order = ["scanning", "analyzing", "documenting", "reviewing"]
        current_idx = phases_order.index(self._current_phase) if self._current_phase in phases_order else 0

        step_controls = []
        for i, pk in enumerate(phases_order):
            p = PHASE_CONFIG[pk]
            pd = self.progress_data[pk]
            done = pd["current"] >= pd["total"] and pd["total"] > 0
            active = pk == self._current_phase
            future = i > current_idx

            if done:
                icon_widget = ft.Container(
                    content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=24, color=AppTheme.SUCCESS),
                    width=36, height=36, alignment=ft.Alignment(0, 0),
                )
            elif active:
                icon_widget = ft.Container(
                    content=ft.Stack(controls=[
                        ft.ProgressRing(width=36, height=36, stroke_width=3, color=p["color"]),
                        ft.Container(content=ft.Icon(p["icon"], size=16, color=p["color"]),
                                     width=36, height=36, alignment=ft.Alignment(0, 0)),
                    ], width=36, height=36),
                    width=36, height=36,
                )
            else:
                icon_widget = ft.Container(
                    content=ft.Icon(p["icon"], size=20,
                                    color=AppTheme.TEXT_DISABLED if future else AppTheme.TEXT_SECONDARY),
                    width=36, height=36, alignment=ft.Alignment(0, 0),
                    border_radius=18,
                    bgcolor="#F5F5F5" if future else None,
                )

            color = AppTheme.SUCCESS if done else p["color"] if active else AppTheme.TEXT_DISABLED if future else AppTheme.TEXT_SECONDARY

            step = ft.Column(
                controls=[
                    icon_widget,
                    ft.Text(p["label"], size=10, weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL,
                            color=color, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4, expand=True,
            )
            step_controls.append(step)

            if i < len(phases_order) - 1:
                step_controls.append(ft.Container(
                    width=30, height=2,
                    bgcolor=AppTheme.SUCCESS if done else "#E0E0E0",
                    border_radius=1,
                    margin=ft.Margin(top=16, bottom=0, left=0, right=0),
                ))

        timeline = ft.Container(
            content=ft.Row(controls=step_controls, alignment=ft.MainAxisAlignment.CENTER,
                           vertical_alignment=ft.CrossAxisAlignment.START),
            padding=ft.Padding(left=24, right=24, top=0, bottom=16),
        )

        # ── Recent files feed ──
        feed_items = []
        display_files = list(reversed(self._recent_files[-6:]))
        for idx, fname in enumerate(display_files):
            fi, fc = _icon_for_file(fname)
            opacity = max(0.3, 1.0 - (idx * 0.12))
            feed_items.append(
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Container(
                            content=ft.Icon(fi, size=16, color=fc),
                            width=28, height=28, border_radius=6,
                            bgcolor=ft.Colors.with_opacity(0.1, fc),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(fname, size=12, color=AppTheme.TEXT_SECONDARY,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                        ft.Icon(ft.Icons.CHECK, size=14, color=AppTheme.SUCCESS) if idx > 0
                        else ft.ProgressRing(width=14, height=14, stroke_width=2, color=phase["color"]),
                    ], spacing=8),
                    opacity=opacity,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                    border_radius=6,
                    bgcolor="#FAFAFA" if idx == 0 else None,
                    animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
                )
            )

        if not feed_items:
            feed_items.append(ft.Container(
                content=ft.Row(controls=[
                    ft.ProgressRing(width=14, height=14, stroke_width=2, color=phase["color"]),
                    ft.Text("Starting up...", size=12, color=AppTheme.TEXT_DISABLED, italic=True),
                ], spacing=8),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            ))

        files_processed_text = f"{self._file_count} files processed" if self._file_count > 0 else ""
        feed_section = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.DESCRIPTION, size=14, color=AppTheme.TEXT_SECONDARY),
                    ft.Text("Recent Files", size=12, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_SECONDARY),
                    ft.Container(expand=True),
                    ft.Text(files_processed_text, size=11, color=AppTheme.TEXT_DISABLED),
                ], spacing=6),
                ft.Container(
                    content=ft.Column(controls=feed_items, spacing=2),
                    border=ft.Border.all(1, AppTheme.BORDER_COLOR),
                    border_radius=AppTheme.RADIUS_MEDIUM,
                    padding=10,
                    bgcolor="white",
                    height=200,
                ),
            ], spacing=8),
            padding=ft.Padding(left=16, right=16, top=0, bottom=10),
        )

        # ── Cancel ──
        cancel_btn = ft.Container(
            content=ft.TextButton(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.CANCEL, size=14, color=AppTheme.ERROR),
                    ft.Text("Cancel", color=AppTheme.ERROR, size=12),
                ], spacing=4),
                on_click=self._cancel_scan,
            ),
            alignment=ft.Alignment(1, 0),
            padding=ft.Padding(right=16, top=0, bottom=0, left=0),
        ) if self.on_cancel else ft.Container()

        return ft.Column(
            controls=[cancel_btn, hero, bar_section, timeline, feed_section],
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
        )

    # ── Helpers ─────────────────────────────────────────────────

    def _get_overall_progress(self) -> float:
        weights = {"scanning": 10, "analyzing": 40, "documenting": 25, "reviewing": 25}
        total = 0.0
        for stage, weight in weights.items():
            d = self.progress_data[stage]
            if d["total"] > 0:
                total += (d["current"] / d["total"]) * weight
        return min(total, 100.0)

    def _extract_filename(self, status: str) -> str:
        for prefix in ("Scanning ", "Analyzing ", "Analyzed ", "AI reviewing ",
                        "Documenting ", "Static check: ", "AI reviewing "):
            if status.startswith(prefix):
                return status[len(prefix):]
        return ""

    def _build_paths_list(self) -> ft.Column:
        items = []
        for p in self.selected_paths:
            items.append(ft.Row(controls=[
                ft.Icon(ft.Icons.FOLDER, size=20, color=AppTheme.PRIMARY),
                ft.Text(p, size=AppTheme.FONT_SIZE_NORMAL, expand=True),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, tooltip="Remove",
                              on_click=lambda _, path=p: self._remove_path(path))
            ], spacing=8))
        return ft.Column(controls=items, spacing=8, scroll=ft.ScrollMode.AUTO)

    # ── Event Handlers ──────────────────────────────────────────

    async def _on_browse_click(self, e):
        if self.on_select_folder:
            await self.on_select_folder()

    def _add_typed_path(self, e):
        path = self.path_input.value.strip() if hasattr(self, 'path_input') and self.path_input.value else ""
        if path:
            self.add_path(path)
            self.path_input.value = ""
            self.path_input.update()

    def _remove_path(self, path: str):
        if path in self.selected_paths:
            self.selected_paths.remove(path)
        self.content = self._build_content()
        self.update()

    def _start_analysis(self, e):
        if self.selected_paths:
            self.is_scanning = True
            self._current_phase = "scanning"
            self._current_file = ""
            self._recent_files = []
            self._file_count = 0
            self.content = self._build_content()
            self.update()
            paths = list(self.selected_paths)
            opts = self.option_values.copy()
            self.page.run_thread(lambda: self.on_start_scan(paths, opts))

    def _cancel_scan(self, e):
        if self.on_cancel:
            self.on_cancel()
        self.is_scanning = False
        self.content = self._build_content()
        self.update()

    def update_progress(self, stage: str, current: int, total: int, status: str):
        if stage in self.progress_data:
            self.progress_data[stage] = {"current": current, "total": total, "status": status}

            if stage != self._current_phase:
                self._current_phase = stage

            filename = self._extract_filename(status)
            if filename:
                self._current_file = filename
                self._file_count += 1
                if not self._recent_files or self._recent_files[-1] != filename:
                    self._recent_files.append(filename)
                    if len(self._recent_files) > 30:
                        self._recent_files = self._recent_files[-20:]

            if self.is_scanning:
                self.content = self._build_content()
                self.update()

    def _update_option(self, key: str, value: bool):
        self.option_values[key] = value

    def add_path(self, path: str):
        if path not in self.selected_paths:
            self.selected_paths.append(path)
            self.content = self._build_content()
            self.update()

    def reset(self):
        self.is_scanning = False
        self.selected_paths = []
        self.progress_data = {
            "scanning": {"current": 0, "total": 0, "status": "Pending"},
            "analyzing": {"current": 0, "total": 0, "status": "Pending"},
            "documenting": {"current": 0, "total": 0, "status": "Pending"},
            "reviewing": {"current": 0, "total": 0, "status": "Pending"}
        }
        self._current_phase = "scanning"
        self._current_file = ""
        self._recent_files = []
        self._file_count = 0
        self.content = self._build_content()
        self.update()
