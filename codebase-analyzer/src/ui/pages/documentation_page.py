"""
Documentation Page — browse generated docs with project context.
"""

from pathlib import Path
from typing import Optional, List, Dict
import flet as ft

from ...models.project import Project
from ..theme import AppTheme
from ..utils import create_empty_state, create_error_display, format_number, create_badge


CATEGORY_COLORS = {
    "API": "#1565C0",
    "UI": "#7B1FA2",
    "Database": "#00695C",
    "Auth": "#C62828",
    "Config": "#4E342E",
    "Test": "#558B2F",
    "Util": "#F57C00",
    "Service": "#0277BD",
    "Model": "#6A1B9A",
}

class DocumentationPage(ft.Container):

    def __init__(
        self,
        project: Optional[Project] = None,
        docs_dir: Optional[Path] = None
    ):
        self.project = project
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.search_query = ""
        self.doc_files = self._load_doc_files()
        self.selected_file = self.doc_files[0] if self.doc_files else None
        self._nav_mode = "groups"
        self._expanded_groups: set = set()
        self._mounted = False
        self._search_field = ft.TextField(
            hint_text="Search docs...", prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search, dense=True, border_color=AppTheme.BORDER_COLOR,
            text_size=12, value=self.search_query,
        )
        self._nav_panel_container = ft.Container(width=280, bgcolor="#FAFAFA", padding=0)
        self._tab_row_container = ft.Container(padding=ft.Padding(left=12, right=12, top=8, bottom=4))
        self._file_list_container = ft.Container(
            expand=True,
            padding=ft.Padding(left=8, right=8, top=4, bottom=8),
        )
        self._viewer_container = ft.Container(expand=True, padding=0)

        super().__init__(
            content=self._build_content(),
            padding=0,
            expand=True
        )

    def _load_doc_files(self) -> List[Path]:
        if not self.docs_dir or not self.docs_dir.exists():
            return []
        return sorted(p for p in self.docs_dir.rglob("*.md") if p.is_file())

    # ── Main layout ────────────────────────────────────────────

    def _build_content(self) -> ft.Control:
        if not self.project:
            return create_empty_state(
                icon=ft.Icons.DESCRIPTION, title="No Project Loaded",
                description="Start an analysis to browse generated documentation")

        if not self.docs_dir or not self.docs_dir.exists() or not self.doc_files:
            return create_empty_state(
                icon=ft.Icons.FOLDER_OFF, title="No Documentation Found",
                description="Run documentation generation to create files")

        hero = self._build_hero()
        self._nav_panel_container.content = self._build_nav_panel()
        self._tab_row_container.content = self._build_tab_row()
        self._file_list_container.content = self._build_current_nav_list()
        self._viewer_container.content = self._build_viewer()

        body = ft.Row(controls=[
            self._nav_panel_container,
            ft.VerticalDivider(width=1, color=AppTheme.DIVIDER_COLOR),
            self._viewer_container,
        ], spacing=0, expand=True)

        return ft.Column(controls=[hero, body], spacing=0, expand=True)

    # ── Hero section ───────────────────────────────────────────

    def _build_hero(self) -> ft.Container:
        p = self.project
        m = p.metrics

        # Name + description
        name_col = ft.Column(controls=[
            ft.Text(p.name, size=20, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ft.Text(p.description or "Codebase analysis results", size=13,
                    color=AppTheme.TEXT_SECONDARY, max_lines=2),
        ], spacing=2, expand=True)

        # Metric pills
        metrics = [
            (ft.Icons.DESCRIPTION, f"{format_number(m.total_files)} files", AppTheme.PRIMARY),
            (ft.Icons.CODE, f"{format_number(m.total_lines)} lines", "#6A1B9A"),
            (ft.Icons.FUNCTIONS, f"{m.total_functions} functions", "#00695C"),
            (ft.Icons.CLASS_, f"{m.total_classes} classes", "#E65100"),
        ]
        if m.average_complexity and m.average_complexity > 0:
            metrics.append((ft.Icons.SPEED, f"{m.average_complexity:.1f} complexity", "#C62828"))

        metric_widgets = []
        for icon, label, color in metrics:
            metric_widgets.append(
                ft.Container(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(icon, size=14, color=color),
                                ft.Text(
                                    label,
                                    size=11,
                                    color=AppTheme.TEXT_PRIMARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            spacing=4,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                        border=ft.Border.all(1, "#E0E0E0"),
                        border_radius=12,
                    ),
                    expand=True,
                )
            )

        metrics_row = ft.Row(
            controls=metric_widgets,
            spacing=6,
            wrap=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        return ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[name_col], spacing=0),
                metrics_row,
            ], spacing=8),
            padding=ft.Padding(left=24, right=24, top=16, bottom=12),
            bgcolor="white",
            border=ft.Border(bottom=ft.BorderSide(1, AppTheme.DIVIDER_COLOR)),
        )

    # ── Navigation panel ───────────────────────────────────────

    def _build_tab_row(self) -> ft.Row:
        groups_active = self._nav_mode == "groups"
        return ft.Row(controls=[
            ft.Container(
                content=ft.Text("By Group", size=12, weight=ft.FontWeight.BOLD,
                                color=AppTheme.PRIMARY if groups_active else AppTheme.TEXT_SECONDARY),
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                bgcolor="#E3F2FD" if groups_active else None,
                border_radius=6,
                on_click=lambda _: self._set_nav_mode("groups"),
            ),
            ft.Container(
                content=ft.Text("All Files", size=12, weight=ft.FontWeight.BOLD,
                                color=AppTheme.PRIMARY if not groups_active else AppTheme.TEXT_SECONDARY),
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                bgcolor="#E3F2FD" if not groups_active else None,
                border_radius=6,
                on_click=lambda _: self._set_nav_mode("files"),
            ),
        ], spacing=4)

    def _build_current_nav_list(self) -> ft.Control:
        if self._nav_mode == "groups":
            return self._build_group_nav()
        return self._build_flat_nav()

    def _build_nav_panel(self) -> ft.Column:
        return ft.Column(controls=[
            ft.Container(content=self._search_field, padding=ft.Padding(left=12, right=12, top=12, bottom=0)),
            self._tab_row_container,
            ft.Divider(height=1, color=AppTheme.DIVIDER_COLOR),
            self._file_list_container,
        ], spacing=0, expand=True)

    def _build_group_nav(self) -> ft.ListView:
        items = []
        fmap = self.project.functionality_map if self.project else None

        if fmap and fmap.groups:
            categories: Dict[str, list] = {}
            for group in fmap.groups.values():
                cat = getattr(group, 'category', 'Other') or 'Other'
                categories.setdefault(cat, []).append(group)

            for cat_name in sorted(categories.keys()):
                groups = categories[cat_name]
                cat_color = CATEGORY_COLORS.get(cat_name, "#78909C")

                items.append(ft.Container(
                    content=ft.Row(controls=[
                        ft.Container(width=4, height=14, bgcolor=cat_color, border_radius=2),
                        ft.Text(cat_name, size=11, weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_SECONDARY),
                    ], spacing=6),
                    padding=ft.Padding(left=4, right=0, top=8, bottom=2),
                ))

                for group in groups:
                    expanded = group.id in self._expanded_groups
                    group_files = self._get_group_doc_files(group)
                    if self.search_query and not group_files and \
                       self.search_query.lower() not in group.name.lower():
                        continue

                    # Group header
                    items.append(ft.Container(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.EXPAND_LESS if expanded else ft.Icons.EXPAND_MORE,
                                    size=16, color=AppTheme.TEXT_SECONDARY),
                            ft.Icon(ft.Icons.FOLDER, size=14, color=cat_color),
                            ft.Text(group.name, size=12, weight=ft.FontWeight.BOLD,
                                    color=AppTheme.TEXT_PRIMARY, expand=True,
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(str(len(group_files)), size=10, color=AppTheme.TEXT_DISABLED),
                        ], spacing=4),
                        padding=ft.Padding(left=8, right=4, top=4, bottom=4),
                        border_radius=4,
                        bgcolor="#F0F0F0" if expanded else None,
                        on_click=lambda _, gid=group.id: self._toggle_group(gid),
                    ))

                    if expanded:
                        for doc_path in group_files:
                            is_selected = doc_path == self.selected_file
                            items.append(ft.Container(
                                content=ft.Row(controls=[
                                    ft.Icon(ft.Icons.ARTICLE, size=13,
                                            color=AppTheme.PRIMARY if is_selected else AppTheme.TEXT_DISABLED),
                                    ft.Text(doc_path.stem, size=11,
                                            color=AppTheme.PRIMARY if is_selected else AppTheme.TEXT_PRIMARY,
                                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ], spacing=4),
                                padding=ft.Padding(left=32, right=4, top=3, bottom=3),
                                border_radius=4,
                                bgcolor="#E3F2FD" if is_selected else None,
                                on_click=lambda _, p=doc_path: self._select_file(p),
                            ))
        else:
            items = self._build_directory_grouped_items()

        return ft.ListView(controls=items, spacing=1, expand=True)

    def _build_flat_nav(self) -> ft.ListView:
        matching = self._get_matching_files()
        items = []
        for path in matching:
            is_selected = path == self.selected_file
            rel = self._relative_label(path)
            items.append(ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.ARTICLE, size=14,
                            color=AppTheme.PRIMARY if is_selected else AppTheme.TEXT_DISABLED),
                    ft.Text(rel, size=11,
                            color=AppTheme.PRIMARY if is_selected else AppTheme.TEXT_PRIMARY,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ], spacing=6),
                padding=ft.Padding(left=8, right=4, top=4, bottom=4),
                border_radius=4,
                bgcolor="#E3F2FD" if is_selected else None,
                on_click=lambda _, p=path: self._select_file(p),
            ))
        return ft.ListView(controls=items, spacing=1, expand=True)

    def _build_directory_grouped_items(self) -> list:
        items = []
        dirs: Dict[str, List[Path]] = {}
        for f in self._get_matching_files():
            rel = self._relative_label(f)
            parent = str(Path(rel).parent) if '/' in rel or '\\' in rel else "root"
            dirs.setdefault(parent, []).append(f)

        for dir_name in sorted(dirs.keys()):
            items.append(ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(ft.Icons.FOLDER, size=14, color="#78909C"),
                    ft.Text(dir_name, size=11, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_SECONDARY),
                ], spacing=4),
                padding=ft.Padding(left=4, right=0, top=8, bottom=2),
            ))
            for path in dirs[dir_name]:
                is_selected = path == self.selected_file
                items.append(ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.ARTICLE, size=13,
                                color=AppTheme.PRIMARY if is_selected else AppTheme.TEXT_DISABLED),
                        ft.Text(path.stem, size=11,
                                color=AppTheme.PRIMARY if is_selected else AppTheme.TEXT_PRIMARY,
                                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    ], spacing=4),
                    padding=ft.Padding(left=24, right=4, top=3, bottom=3),
                    border_radius=4,
                    bgcolor="#E3F2FD" if is_selected else None,
                    on_click=lambda _, p=path: self._select_file(p),
                ))
        return items

    # ── Document viewer ────────────────────────────────────────

    def _build_viewer(self) -> ft.Control:
        if not self.selected_file:
            return create_empty_state(
                icon=ft.Icons.ARTICLE_OUTLINED, title="Select a Document",
                description="Choose a file from the sidebar")

        try:
            md_content = self.selected_file.read_text(encoding="utf-8")
        except OSError as e:
            return create_error_display(str(e))

        rel_path = self._relative_label(self.selected_file)
        line_count = len(md_content.splitlines())

        # Breadcrumb
        parts = Path(rel_path).parts
        breadcrumb_items = []
        for i, part in enumerate(parts):
            if i > 0:
                breadcrumb_items.append(ft.Text("/", size=12, color=AppTheme.TEXT_DISABLED))
            is_last = i == len(parts) - 1
            breadcrumb_items.append(ft.Text(
                part, size=12,
                color=AppTheme.TEXT_PRIMARY if is_last else AppTheme.TEXT_SECONDARY,
                weight=ft.FontWeight.BOLD if is_last else ft.FontWeight.NORMAL))

        breadcrumb = ft.Row(controls=breadcrumb_items, spacing=4)

        # File info
        info_items = [
            ft.Text(f"{line_count} lines", size=11, color=AppTheme.TEXT_DISABLED),
        ]
        group_name = self._find_group_for_file(self.selected_file)
        if group_name:
            info_items.extend([
                ft.Text("·", size=11, color=AppTheme.TEXT_DISABLED),
                ft.Icon(ft.Icons.FOLDER, size=12, color=AppTheme.TEXT_DISABLED),
                ft.Text(group_name, size=11, color=AppTheme.TEXT_DISABLED),
            ])

        info_row = ft.Row(controls=info_items, spacing=4)

        header = ft.Container(
            content=ft.Column(controls=[breadcrumb, info_row], spacing=4),
            padding=ft.Padding(left=24, right=24, top=14, bottom=10),
            bgcolor="white",
            border=ft.Border(bottom=ft.BorderSide(1, AppTheme.DIVIDER_COLOR)),
        )

        viewer = ft.Container(
            content=ft.Markdown(
                md_content, selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            ),
            padding=ft.Padding(left=24, right=24, top=16, bottom=24),
            expand=True,
        )

        return ft.Column(controls=[header, viewer], spacing=0, expand=True,
                          scroll=ft.ScrollMode.AUTO)

    # ── Helpers ────────────────────────────────────────────────

    def _get_matching_files(self) -> List[Path]:
        if not self.search_query:
            return self.doc_files
        q = self.search_query.lower()
        return [f for f in self.doc_files if q in self._relative_label(f).lower()]

    def _get_group_doc_files(self, group) -> List[Path]:
        group_file_names = set()
        for fp in (group.files or []):
            group_file_names.add(Path(fp).stem)
            group_file_names.add(Path(fp).name)

        matching = []
        for doc_path in self.doc_files:
            stem = doc_path.stem
            for gfn in group_file_names:
                if gfn in stem or stem in gfn:
                    matching.append(doc_path)
                    break

        if self.search_query:
            q = self.search_query.lower()
            matching = [f for f in matching if q in f.name.lower()]

        return matching

    def _find_group_for_file(self, file_path: Path) -> Optional[str]:
        fmap = self.project.functionality_map if self.project else None
        if not fmap:
            return None
        stem = file_path.stem
        for group in fmap.groups.values():
            for fp in (group.files or []):
                if Path(fp).stem in stem or stem in Path(fp).stem:
                    return group.name
        return None

    def _relative_label(self, path: Path) -> str:
        if not self.docs_dir:
            return path.name
        try:
            return str(path.relative_to(self.docs_dir))
        except ValueError:
            return path.name

    # ── Events ─────────────────────────────────────────────────

    def _select_file(self, path: Path):
        self.selected_file = path
        self._viewer_container.content = self._build_viewer()
        self._file_list_container.content = self._build_current_nav_list()
        self._request_update()

    def _on_search(self, event):
        self.search_query = event.control.value or ""
        self._search_field.value = self.search_query
        matches = self._get_matching_files()
        if self.selected_file not in matches:
            self.selected_file = matches[0] if matches else None
        self._file_list_container.content = self._build_current_nav_list()
        self._viewer_container.content = self._build_viewer()
        self._request_update()

    def _set_nav_mode(self, mode: str):
        self._nav_mode = mode
        self._tab_row_container.content = self._build_tab_row()
        self._file_list_container.content = self._build_current_nav_list()
        self._request_update()

    def _toggle_group(self, group_id: str):
        if group_id in self._expanded_groups:
            self._expanded_groups.discard(group_id)
        else:
            self._expanded_groups.add(group_id)
        self._file_list_container.content = self._build_current_nav_list()
        self._request_update()

    def _request_update(self):
        if self._mounted:
            self.update()

    def did_mount(self):
        self._mounted = True

    def did_unmount(self):
        self._mounted = False
