"""
Markdown Documentation Generator - Creates structured Markdown documentation.

This module generates comprehensive Markdown documentation for analyzed codebases,
including per-file docs, functionality group docs, and API references.
"""

from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from ..models.project import Project
from ..models.file_info import FileInfo
from ..models.functionality import FunctionalityGroup
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class MarkdownGenerator:
    """
    Generates Markdown documentation from analyzed project data.

    Features:
    - Per-file documentation with code structure
    - Functionality group documentation
    - API reference generation
    - Cross-reference linking
    - Code metrics inclusion
    - Customizable templates
    """

    def __init__(self, config: Config, template_dir: Optional[Path] = None):
        """
        Initialize the Markdown generator.

        Args:
            config: Configuration object
            template_dir: Directory containing Jinja2 templates
        """
        self.config = config

        # Setup template directory
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / 'templates'

        self.template_dir = Path(template_dir)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )

        # Register custom filters
        self._register_filters()

        logger.info("Markdown generator initialized")

    def _register_filters(self):
        """Register custom Jinja2 filters."""
        self.env.filters['format_date'] = self._format_date
        self.env.filters['format_size'] = self._format_size
        self.env.filters['format_complexity'] = self._format_complexity
        self.env.filters['escape_markdown'] = self._escape_markdown

    def _format_date(self, dt: Optional[datetime]) -> str:
        """Format datetime for display."""
        if dt is None:
            return 'N/A'
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _format_complexity(self, complexity: int) -> str:
        """Format complexity score with rating."""
        if complexity <= 5:
            return f"{complexity} (Low)"
        elif complexity <= 10:
            return f"{complexity} (Medium)"
        elif complexity <= 20:
            return f"{complexity} (High)"
        else:
            return f"{complexity} (Very High)"

    def _escape_markdown(self, text: str) -> str:
        """Escape special Markdown characters."""
        if not text:
            return ''

        # Escape common Markdown special characters
        replacements = {
            '\\': '\\\\',
            '`': '\\`',
            '*': '\\*',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '[': '\\[',
            ']': '\\]',
            '(': '\\(',
            ')': '\\)',
            '#': '\\#',
            '+': '\\+',
            '-': '\\-',
            '.': '\\.',
            '!': '\\!',
        }

        for char, escaped in replacements.items():
            text = text.replace(char, escaped)

        return text

    def generate_project_documentation(
        self,
        project: Project,
        output_dir: Path,
        progress_callback=None
    ) -> Dict[str, Path]:
        logger.info(f"Generating documentation for project: {project.name}")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = {}

        overview_path = self._generate_project_overview(project, output_dir)
        generated_files['overview'] = overview_path

        if project.functionality_map:
            groups_dir = output_dir / 'functionality_groups'
            groups_dir.mkdir(exist_ok=True)

            for group in project.functionality_map.get_all_groups():
                group_path = self._generate_group_documentation(
                    group,
                    project,
                    groups_dir
                )
                generated_files[f'group_{group.id}'] = group_path

        files_dir = output_dir / 'files'
        files_dir.mkdir(exist_ok=True)

        all_files = list(project.get_all_files())
        total = len(all_files)
        for idx, file_info in enumerate(all_files, 1):
            if progress_callback:
                progress_callback(f"Documenting {file_info.relative_path.name}", idx, total)
            file_path = self._generate_file_documentation(
                file_info,
                files_dir
            )
            file_key = f'file_{str(file_info.relative_path).replace("/", "_").replace("\\", "_")}'
            generated_files[file_key] = file_path

        logger.info(f"Generated {len(generated_files)} documentation files")
        return generated_files

    def _generate_project_overview(
        self,
        project: Project,
        output_dir: Path
    ) -> Path:
        """Generate project overview documentation."""
        logger.debug("Generating project overview")

        # Prepare template data
        data = {
            'project': project,
            'generated_at': datetime.now(),
            'metrics': project.metrics,
            'total_groups': len(project.functionality_map.groups) if project.functionality_map else 0,
            'total_findings': len(project.findings),
            'total_suggestions': len(project.suggestions),
        }

        # Render template
        content = self._render_template('project_overview.md.j2', data)

        # Write to file
        output_path = output_dir / 'PROJECT_OVERVIEW.md'
        output_path.write_text(content, encoding='utf-8')

        logger.debug(f"Project overview written to {output_path}")
        return output_path

    def _generate_group_documentation(
        self,
        group: FunctionalityGroup,
        project: Project,
        output_dir: Path
    ) -> Path:
        """Generate documentation for a functionality group."""
        logger.debug(f"Generating documentation for group: {group.name}")

        # Get files in this group
        group_files = [
            project.get_file(str(file_path))
            for file_path in group.files
        ]
        group_files = [f for f in group_files if f is not None]

        # Prepare template data
        data = {
            'group': group,
            'files': group_files,
            'generated_at': datetime.now(),
            'project_name': project.name,
        }

        # Render template
        content = self._render_template('functionality_group.md.j2', data)

        # Write to file
        filename = f"{group.id}.md"
        output_path = output_dir / filename
        output_path.write_text(content, encoding='utf-8')

        logger.debug(f"Group documentation written to {output_path}")
        return output_path

    def _generate_file_documentation(
        self,
        file_info: FileInfo,
        output_dir: Path
    ) -> Path:
        """Generate documentation for a single file."""
        logger.debug(f"Generating documentation for file: {file_info.name}")

        # Prepare template data
        data = {
            'file': file_info,
            'generated_at': datetime.now(),
            'functions': file_info.get_functions(),
            'classes': file_info.get_classes(),
            'methods': file_info.get_methods(),
            'public_api': file_info.get_public_api(),
        }

        # Render template
        content = self._render_template('file_documentation.md.j2', data)

        # Create safe filename
        safe_name = str(file_info.relative_path).replace('/', '_').replace('\\', '_')
        filename = f"{safe_name}.md"
        output_path = output_dir / filename

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(content, encoding='utf-8')

        logger.debug(f"File documentation written to {output_path}")
        return output_path

    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with data.

        Args:
            template_name: Name of the template file
            data: Data to pass to the template

        Returns:
            Rendered template content
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            # Return fallback content
            return self._generate_fallback_content(template_name, data)

    def _generate_fallback_content(
        self,
        template_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Generate fallback content when template rendering fails."""
        logger.warning(f"Using fallback content for {template_name}")

        if 'project' in data:
            project = data['project']
            return f"""# {project.name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This documentation was generated automatically.

## Metrics

- Total Files: {project.metrics.total_files}
- Total Lines: {project.metrics.total_lines}
- Total Functions: {project.metrics.total_functions}
- Total Classes: {project.metrics.total_classes}

## Note

Template rendering failed. This is fallback content.
"""

        elif 'group' in data:
            group = data['group']
            return f"""# {group.name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Description

{group.description or 'No description available.'}

## Files

Total files in this group: {group.total_files}

## Note

Template rendering failed. This is fallback content.
"""

        elif 'file' in data:
            file_info = data['file']
            return f"""# {file_info.name}

**Path:** {file_info.relative_path}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Metrics

- Lines of Code: {file_info.metrics.lines_of_code}
- Functions: {file_info.metrics.functions_count}
- Classes: {file_info.metrics.classes_count}
- Complexity: {file_info.metrics.complexity}

## Note

Template rendering failed. This is fallback content.
"""

        return "# Documentation\n\nTemplate rendering failed."

    def generate_api_reference(
        self,
        project: Project,
        output_path: Path
    ) -> Path:
        """
        Generate API reference documentation.

        Args:
            project: Project object
            output_path: Path to write API reference

        Returns:
            Path to generated file
        """
        logger.info("Generating API reference")

        # Collect all public API elements
        api_elements = []

        for file_info in project.get_all_files():
            public_api = file_info.get_public_api()
            if public_api:
                api_elements.append({
                    'file': file_info,
                    'elements': public_api
                })

        # Prepare template data
        data = {
            'project': project,
            'api_elements': api_elements,
            'generated_at': datetime.now(),
        }

        # Render template
        content = self._render_template('api_reference.md.j2', data)

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')

        logger.info(f"API reference written to {output_path}")
        return output_path

# Made with Bob