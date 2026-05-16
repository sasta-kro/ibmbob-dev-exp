"""
Documentation Page

Browse generated Markdown documentation.
"""

from pathlib import Path
from typing import Optional

import flet as ft

from ...models.project import Project
from ..theme import AppTheme
from ..utils import create_empty_state, create_error_display


class DocumentationPage(ft.Container):
    """Documentation browser page component."""
    
    def __init__(
        self,
        project: Optional[Project] = None,
        docs_dir: Optional[Path] = None
    ):
        """
        Initialize documentation page.
        
        Args:
            project: Project data to display
            docs_dir: Directory containing generated Markdown files
        """
        self.project = project
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.search_query = ""
        self.doc_files = self._load_doc_files()
        self.selected_file = self.doc_files[0] if self.doc_files else None
        
        super().__init__(
            content=self._build_content(),
            padding=AppTheme.SPACING_LARGE,
            expand=True
        )
    
    def _load_doc_files(self) -> list[Path]:
        """Load generated Markdown documentation files."""
        if not self.docs_dir or not self.docs_dir.exists():
            return []
        
        return sorted(
            path for path in self.docs_dir.rglob("*.md")
            if path.is_file()
        )
    
    def _build_content(self) -> ft.Control:
        """Build documentation browser content."""
        if not self.project:
            return create_empty_state(
                icon=ft.Icons.DESCRIPTION,
                title="No Project Loaded",
                description="Start an analysis to browse generated documentation"
            )
        
        if not self.docs_dir or not self.docs_dir.exists():
            return create_empty_state(
                icon=ft.Icons.FOLDER_OFF,
                title="No Documentation Found",
                description="Run documentation generation to create Markdown files"
            )
        
        if not self.doc_files:
            return create_empty_state(
                icon=ft.Icons.ARTICLE_OUTLINED,
                title="No Markdown Files",
                description="The documentation folder has no Markdown files"
            )
        
        return ft.Row(
            controls=[
                ft.Container(
                    content=self._build_file_panel(),
                    width=320
                ),
                ft.VerticalDivider(width=1, color=AppTheme.DIVIDER_COLOR),
                ft.Container(
                    content=self._build_document_panel(),
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
    
    def _build_file_panel(self) -> ft.Column:
        """Build documentation file list and search."""
        matching_files = self._get_matching_files()
        controls = [
            ft.Text(
                "Documentation",
                size=AppTheme.FONT_SIZE_TITLE,
                weight=ft.FontWeight.BOLD,
                color=AppTheme.TEXT_PRIMARY
            ),
            ft.TextField(
                label="Search documentation",
                prefix_icon=ft.Icons.SEARCH,
                value=self.search_query,
                on_change=self._on_search,
                dense=True,
                border_color=AppTheme.BORDER_COLOR
            ),
            ft.Container(height=AppTheme.SPACING_MEDIUM)
        ]
        
        if not matching_files:
            controls.append(
                create_empty_state(
                    icon=ft.Icons.SEARCH_OFF,
                    title="No Matches",
                    description="Adjust the search query"
                )
            )
        else:
            file_buttons = [
                ft.TextButton(
                    content=self._relative_label(doc_file),
                    icon=ft.Icons.ARTICLE,
                    on_click=lambda _, path=doc_file: self._select_file(path),
                    style=ft.ButtonStyle(
                        color=(
                            AppTheme.PRIMARY
                            if doc_file == self.selected_file
                            else AppTheme.TEXT_PRIMARY
                        )
                    )
                )
                for doc_file in matching_files
            ]
            controls.append(
                ft.ListView(
                    controls=file_buttons,
                    spacing=4,
                    expand=True
                )
            )
        
        return ft.Column(
            controls=controls,
            spacing=8,
            expand=True
        )
    
    def _build_document_panel(self) -> ft.Control:
        """Build selected document viewer."""
        if not self.selected_file:
            return create_empty_state(
                icon=ft.Icons.ARTICLE_OUTLINED,
                title="No Document Selected",
                description="Select a generated documentation file"
            )
        
        try:
            markdown_content = self.selected_file.read_text(encoding="utf-8")
        except OSError as error:
            return create_error_display(str(error))
        
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            self._relative_label(self.selected_file),
                            size=AppTheme.FONT_SIZE_TITLE,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY,
                            expand=True
                        ),
                        ft.Text(
                            f"{len(markdown_content.splitlines())} lines",
                            size=AppTheme.FONT_SIZE_SMALL,
                            color=AppTheme.TEXT_SECONDARY
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=AppTheme.SPACING_MEDIUM),
                ft.Container(
                    content=ft.Markdown(
                        markdown_content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
                    ),
                    border=ft.Border.all(1, AppTheme.BORDER_COLOR),
                    border_radius=AppTheme.RADIUS_MEDIUM,
                    padding=AppTheme.SPACING_MEDIUM,
                    expand=True
                )
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _get_matching_files(self) -> list[Path]:
        """Get files matching the current search query."""
        if not self.search_query:
            return self.doc_files
        
        query = self.search_query.lower()
        return [
            doc_file for doc_file in self.doc_files
            if query in self._relative_label(doc_file).lower()
        ]
    
    def _relative_label(self, path: Path) -> str:
        """Return a documentation path relative to the docs directory."""
        if not self.docs_dir:
            return path.name
        
        try:
            return str(path.relative_to(self.docs_dir))
        except ValueError:
            return path.name
    
    def _select_file(self, path: Path):
        """Select a documentation file."""
        self.selected_file = path
        self.content = self._build_content()
        self.update()
    
    def _on_search(self, event):
        """Update documentation search query."""
        self.search_query = event.control.value or ""
        matches = self._get_matching_files()
        if self.selected_file not in matches:
            self.selected_file = matches[0] if matches else None
        self.content = self._build_content()
        self.update()

# Made with Bob
