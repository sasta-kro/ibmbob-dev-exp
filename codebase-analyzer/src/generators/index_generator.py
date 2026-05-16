"""
Index Generator - Creates navigation and index documentation.

This module generates index pages, table of contents, and navigation structures
for the generated documentation.
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..models.project import Project
from ..models.functionality import FunctionalityGroup
from ..utils.logger import get_logger

logger = get_logger(__name__)


class IndexGenerator:
    """
    Generates index and navigation documentation.
    
    Features:
    - Main index page with project overview
    - Table of contents for all documentation
    - Cross-reference mapping
    - Reading order suggestions
    - Search keywords generation
    """
    
    def __init__(self):
        """Initialize the index generator."""
        logger.info("Index generator initialized")
    
    def generate_index(
        self,
        project: Project,
        doc_files: Dict[str, Path],
        output_path: Path
    ) -> Path:
        """
        Generate main index page for documentation.
        
        Args:
            project: Project object
            doc_files: Dictionary of generated documentation files
            output_path: Path to write index file
            
        Returns:
            Path to generated index file
        """
        logger.info("Generating documentation index")
        
        output_path = Path(output_path)
        content = self._build_index_content(project, doc_files, output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Index written to {output_path}")
        return output_path
    
    def _build_index_content(
        self,
        project: Project,
        doc_files: Dict[str, Path],
        output_path: Optional[Path] = None
    ) -> str:
        """Build the content for the index page."""
        if output_path is None:
            output_path = Path('.')
        lines = []
        
        # Header
        lines.append(f"# {project.name} - Documentation Index")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Version:** {project.version}")
        lines.append("")
        
        # Project Overview
        lines.append("## Project Overview")
        lines.append("")
        if project.description:
            lines.append(project.description)
            lines.append("")
        
        # Quick Stats
        lines.append("### Quick Statistics")
        lines.append("")
        lines.append(f"- **Total Files:** {project.metrics.total_files}")
        lines.append(f"- **Total Lines of Code:** {project.metrics.total_lines:,}")
        lines.append(f"- **Total Functions:** {project.metrics.total_functions}")
        lines.append(f"- **Total Classes:** {project.metrics.total_classes}")
        lines.append(f"- **Average Complexity:** {project.metrics.average_complexity:.2f}")
        lines.append("")
        
        # Languages
        if project.metrics.languages:
            lines.append("### Languages")
            lines.append("")
            for lang, count in sorted(
                project.metrics.languages.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                lines.append(f"- **{lang}:** {count} files")
            lines.append("")
        
        # Frameworks
        if project.metrics.frameworks:
            lines.append("### Detected Frameworks")
            lines.append("")
            for framework in sorted(project.metrics.frameworks):
                lines.append(f"- {framework}")
            lines.append("")
        
        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")
        
        table_of_contents = []
        
        # Project Overview Link
        if 'overview' in doc_files:
            rel_path = self._get_relative_path(doc_files['overview'], output_path.parent)
            table_of_contents.append(f"[Project Overview]({rel_path})")
        
        # Functionality Groups
        if project.functionality_map and project.functionality_map.groups:
            table_of_contents.append("[Functionality Groups](#functionality-groups)")
        
        if 'api_reference' in doc_files:
            rel_path = self._get_relative_path(doc_files['api_reference'], output_path.parent)
            table_of_contents.append(f"[API Reference]({rel_path})")
        else:
            table_of_contents.append("[API Reference](#api-reference)")
        
        table_of_contents.append("[File Documentation](#file-documentation)")
        
        for index, entry in enumerate(table_of_contents, 1):
            lines.append(f"{index}. {entry}")
        
        lines.append("")
        
        # Functionality Groups Section
        if project.functionality_map and project.functionality_map.groups:
            lines.append("## Functionality Groups")
            lines.append("")
            lines.append("The codebase is organized into the following functional areas:")
            lines.append("")
            
            groups = project.functionality_map.get_all_groups()
            groups_sorted = sorted(groups, key=lambda g: g.name)
            
            for group in groups_sorted:
                group_key = f'group_{group.id}'
                if group_key in doc_files:
                    rel_path = self._get_relative_path(
                        doc_files[group_key],
                        output_path.parent
                    )
                    lines.append(f"### [{group.name}]({rel_path})")
                else:
                    lines.append(f"### {group.name}")
                
                lines.append("")
                if group.description:
                    lines.append(group.description)
                    lines.append("")
                
                lines.append(f"- **Files:** {group.total_files}")
                lines.append(f"- **Lines of Code:** {group.total_lines:,}")
                lines.append(f"- **Complexity Score:** {group.complexity_score:.2f}/10")
                
                if group.category:
                    lines.append(f"- **Category:** {group.category}")
                
                if group.dependencies:
                    lines.append(f"- **Dependencies:** {', '.join(group.dependencies)}")
                
                lines.append("")
        
        # Reading Order Suggestions
        lines.append("## Suggested Reading Order")
        lines.append("")
        reading_order = self._suggest_reading_order(project)
        for idx, (title, description) in enumerate(reading_order, 1):
            lines.append(f"{idx}. **{title}**")
            lines.append(f"   {description}")
            lines.append("")
        
        # API Reference Section
        lines.append("## API Reference")
        lines.append("")
        if 'api_reference' in doc_files:
            rel_path = self._get_relative_path(
                doc_files['api_reference'],
                output_path.parent
            )
            lines.append(f"[Public API documentation]({rel_path}) for the project.")
        else:
            lines.append("Public API documentation for the project.")
        lines.append("")
        
        # File Documentation Section
        lines.append("## File Documentation")
        lines.append("")
        lines.append("Detailed documentation for individual files:")
        lines.append("")
        
        # Group files by directory
        file_groups = self._group_files_by_directory(project)
        
        for directory, files in sorted(file_groups.items()):
            lines.append(f"### {directory}")
            lines.append("")
            
            for file_info in sorted(files, key=lambda f: f.name):
                # Use relative path as key to match markdown_generator
                file_key = f'file_{str(file_info.relative_path).replace("/", "_").replace("\\", "_")}'
                if file_key in doc_files:
                    rel_path = self._get_relative_path(
                        doc_files[file_key],
                        output_path.parent
                    )
                    lines.append(f"- [{file_info.name}]({rel_path})")
                else:
                    lines.append(f"- {file_info.name}")
            
            lines.append("")
        
        # Search Keywords
        lines.append("## Search Keywords")
        lines.append("")
        keywords = self._generate_keywords(project)
        lines.append(", ".join(sorted(keywords)))
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Codebase Analyzer*")
        lines.append("")
        
        return "\n".join(lines)
    
    def _get_relative_path(self, target: Path, base: Path) -> str:
        """Get relative path from base to target."""
        try:
            rel_path = Path(target).relative_to(base)
            return str(rel_path).replace('\\', '/')
        except ValueError:
            # If relative path fails, return absolute path
            return str(target).replace('\\', '/')
    
    def _suggest_reading_order(
        self,
        project: Project
    ) -> List[Tuple[str, str]]:
        """
        Suggest reading order for documentation.
        
        Returns:
            List of (title, description) tuples
        """
        order = [
            (
                "Project Overview",
                "Start here for a high-level understanding of the project structure and goals."
            ),
        ]
        
        # Add entry point groups first
        if project.functionality_map:
            root_groups = project.functionality_map.get_root_groups()
            if root_groups:
                for group in root_groups[:3]:  # Top 3 root groups
                    order.append((
                        f"{group.name} Functionality",
                        f"Core functionality: {group.description or 'Main entry point'}"
                    ))
        
        # Add configuration and utilities
        order.append((
            "Configuration",
            "Understand how the application is configured and customized."
        ))
        
        order.append((
            "API Reference",
            "Detailed reference for all public APIs and interfaces."
        ))
        
        # Add specific functionality areas
        if project.functionality_map:
            for group in project.functionality_map.get_all_groups():
                if group.category in ['API', 'Database', 'Security']:
                    order.append((
                        f"{group.name}",
                        group.description or f"{group.category} implementation details"
                    ))
        
        return order
    
    def _group_files_by_directory(
        self,
        project: Project
    ) -> Dict[str, List]:
        """Group files by their parent directory."""
        groups = {}
        
        for file_info in project.get_all_files():
            parent = str(file_info.relative_path.parent)
            if parent == '.':
                parent = 'Root'
            
            if parent not in groups:
                groups[parent] = []
            
            groups[parent].append(file_info)
        
        return groups
    
    def _generate_keywords(self, project: Project) -> List[str]:
        """Generate search keywords from project data."""
        keywords = set()
        
        # Add languages
        keywords.update(project.metrics.languages.keys())
        
        # Add frameworks
        keywords.update(project.metrics.frameworks)
        
        # Add functionality group names
        if project.functionality_map:
            for group in project.functionality_map.get_all_groups():
                keywords.add(group.name.lower())
                if group.category:
                    keywords.add(group.category.lower())
                keywords.update(group.tags)
        
        # Add common programming concepts
        for file_info in project.get_all_files():
            if file_info.language_features:
                for feature, used in file_info.language_features.items():
                    if used:
                        keywords.add(feature.replace('_', ' '))
        
        return list(keywords)
    
    def generate_toc(
        self,
        project: Project,
        output_path: Path
    ) -> Path:
        """
        Generate a detailed table of contents.
        
        Args:
            project: Project object
            output_path: Path to write TOC file
            
        Returns:
            Path to generated TOC file
        """
        logger.info("Generating table of contents")
        
        lines = []
        
        lines.append("# Table of Contents")
        lines.append("")
        lines.append(f"**Project:** {project.name}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Build hierarchical TOC
        lines.append("## Documentation Structure")
        lines.append("")
        
        # Project level
        lines.append("1. Project Documentation")
        lines.append("   - Overview")
        lines.append("   - Architecture")
        lines.append("   - Metrics")
        lines.append("")
        
        # Functionality groups
        if project.functionality_map:
            lines.append("2. Functionality Groups")
            for idx, group in enumerate(project.functionality_map.get_all_groups(), 1):
                lines.append(f"   {idx}. {group.name}")
                lines.append(f"      - Files: {group.total_files}")
                lines.append(f"      - Complexity: {group.complexity_score:.2f}")
            lines.append("")
        
        # API Reference
        lines.append("3. API Reference")
        lines.append("   - Public Functions")
        lines.append("   - Public Classes")
        lines.append("   - Interfaces")
        lines.append("")
        
        # File Documentation
        lines.append("4. File Documentation")
        file_groups = self._group_files_by_directory(project)
        for directory, files in sorted(file_groups.items()):
            lines.append(f"   - {directory} ({len(files)} files)")
        lines.append("")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding='utf-8')
        
        logger.info(f"Table of contents written to {output_path}")
        return output_path

# Made with Bob
