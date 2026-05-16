"""
Functionality Grouper - Groups related files into logical functionality areas.

This module analyzes code structure, imports, and semantic relationships to
group files into cohesive functionality groups.
"""

from pathlib import Path
from typing import List, Dict, Set, Optional
from collections import defaultdict
import re

from ..models.file_info import FileInfo
from ..models.functionality import FunctionalityGroup
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class FunctionalityGrouper:
    """
    Groups related files into logical functionality areas.

    Grouping strategies:
    1. Structural hints (folder names, file naming)
    2. Code analysis (imports, dependencies)
    3. Semantic understanding (AI-powered)
    4. Framework conventions (MVC, API routes, etc.)
    """

    def __init__(self, config: Config):
        """
        Initialize the functionality grouper.

        Args:
            config: Configuration object
        """
        self.config = config

        # Common functionality patterns
        self.functionality_patterns = {
            'authentication': ['auth', 'login', 'signup', 'register', 'session', 'jwt', 'token'],
            'database': ['db', 'database', 'model', 'schema', 'migration', 'orm'],
            'api': ['api', 'endpoint', 'route', 'controller', 'handler'],
            'ui': ['ui', 'view', 'component', 'page', 'template', 'frontend'],
            'testing': ['test', 'spec', 'mock', 'fixture'],
            'configuration': ['config', 'settings', 'env', 'constants'],
            'utilities': ['util', 'helper', 'common', 'shared', 'lib'],
            'security': ['security', 'crypto', 'hash', 'encrypt', 'permission'],
            'payment': ['payment', 'billing', 'invoice', 'subscription', 'stripe', 'paypal'],
            'notification': ['notification', 'email', 'sms', 'push', 'alert'],
            'analytics': ['analytics', 'tracking', 'metrics', 'stats', 'report'],
            'admin': ['admin', 'dashboard', 'management'],
            'user': ['user', 'profile', 'account'],
            'search': ['search', 'query', 'filter', 'index'],
            'storage': ['storage', 'file', 'upload', 'download', 's3', 'blob'],
        }

    def group_files(
        self,
        files: List[FileInfo],
        project_path: str
    ) -> List[FunctionalityGroup]:
        """
        Group files into functionality areas.

        Args:
            files: List of FileInfo objects to group
            project_path: Root path of the project

        Returns:
            List of FunctionalityGroup objects
        """
        logger.info(f"Grouping {len(files)} files into functionality areas")

        # Step 1: Group by directory structure
        dir_groups = self._group_by_directory(files)

        # Step 2: Analyze imports and dependencies
        dependency_graph = self._build_dependency_graph(files)

        # Step 3: Detect functionality patterns
        pattern_groups = self._detect_functionality_patterns(files)

        # Step 4: Merge and refine groups
        groups = self._merge_groups(dir_groups, pattern_groups, dependency_graph)

        # Step 5: Create FunctionalityGroup objects
        functionality_groups = self._create_functionality_groups(groups, files, dependency_graph)

        logger.info(f"Created {len(functionality_groups)} functionality groups")
        return functionality_groups

    def _group_by_directory(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """
        Group files by their directory structure.

        Args:
            files: List of FileInfo objects

        Returns:
            Dictionary mapping directory paths to file lists
        """
        groups = defaultdict(list)

        for file_info in files:
            # Get the parent directory
            parent_dir = Path(file_info.relative_path).parent
            dir_key = str(parent_dir) if parent_dir != Path('.') else 'root'
            groups[dir_key].append(file_info)

        return dict(groups)

    def _build_dependency_graph(self, files: List[FileInfo]) -> Dict[str, Set[str]]:
        """
        Build a dependency graph from file imports.

        Args:
            files: List of FileInfo objects

        Returns:
            Dictionary mapping file paths to their dependencies
        """
        graph = defaultdict(set)
        file_map = {str(f.relative_path): f for f in files}

        for file_info in files:
            file_path = str(file_info.relative_path)

            # Analyze imports
            for import_info in file_info.imports:
                # Try to resolve internal imports
                if import_info.is_relative:
                    # Resolve relative import
                    resolved = self._resolve_relative_import(
                        file_path,
                        import_info.module
                    )
                    if resolved and resolved in file_map:
                        graph[file_path].add(resolved)
                else:
                    # Check if it's an internal module
                    for potential_file in file_map.keys():
                        if self._is_internal_import(import_info.module, potential_file):
                            graph[file_path].add(potential_file)

        return dict(graph)

    def _resolve_relative_import(self, file_path: str, module: str) -> Optional[str]:
        """
        Resolve a relative import to an absolute file path.

        Args:
            file_path: Path of the importing file
            module: Relative module path

        Returns:
            Resolved file path or None
        """
        try:
            base_path = Path(file_path).parent

            # Count leading dots
            level = len(module) - len(module.lstrip('.'))
            module_path = module.lstrip('.')

            # Go up directories based on level
            for _ in range(level - 1):
                base_path = base_path.parent

            # Construct potential file paths
            if module_path:
                potential_paths = [
                    base_path / f"{module_path}.py",
                    base_path / module_path / "__init__.py",
                ]
            else:
                potential_paths = [base_path / "__init__.py"]

            for path in potential_paths:
                if path.exists():
                    return str(path)

        except Exception as e:
            logger.debug(f"Error resolving relative import: {e}")

        return None

    def _is_internal_import(self, module: str, file_path: str) -> bool:
        """
        Check if an import refers to an internal file.

        Args:
            module: Module name from import
            file_path: Potential file path

        Returns:
            True if the import refers to this file
        """
        # Convert module path to file path
        module_as_path = module.replace('.', '/')

        # Check if file path contains the module path
        return module_as_path in file_path or file_path.startswith(module_as_path)

    def _detect_functionality_patterns(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """
        Detect functionality patterns in file names and paths.

        Args:
            files: List of FileInfo objects

        Returns:
            Dictionary mapping functionality names to file lists
        """
        groups = defaultdict(list)

        for file_info in files:
            file_path_lower = str(file_info.relative_path).lower()
            file_name_lower = file_info.name.lower()

            # Check against known patterns
            matched = False
            for functionality, patterns in self.functionality_patterns.items():
                for pattern in patterns:
                    if pattern in file_path_lower or pattern in file_name_lower:
                        groups[functionality].append(file_info)
                        matched = True
                        break
                if matched:
                    break

            # If no pattern matched, try to infer from directory name
            if not matched:
                parent_dir = Path(file_info.relative_path).parent.name.lower()
                if parent_dir and parent_dir not in ['.', 'src', 'lib']:
                    groups[parent_dir].append(file_info)

        return dict(groups)

    def _merge_groups(
        self,
        dir_groups: Dict[str, List[FileInfo]],
        pattern_groups: Dict[str, List[FileInfo]],
        dependency_graph: Dict[str, Set[str]]
    ) -> Dict[str, List[FileInfo]]:
        """
        Merge different grouping strategies into final groups.

        Args:
            dir_groups: Groups based on directory structure
            pattern_groups: Groups based on functionality patterns
            dependency_graph: File dependency relationships

        Returns:
            Merged groups with lists of FileInfo objects
        """
        merged = defaultdict(list)

        # Track which files have been grouped using file paths
        grouped_file_paths = set()

        # Start with pattern groups (higher priority)
        for group_name, files in pattern_groups.items():
            for file_info in files:
                file_path = str(file_info.relative_path)
                if file_path not in grouped_file_paths:
                    merged[group_name].append(file_info)
                    grouped_file_paths.add(file_path)

        # Add directory groups for files not yet grouped
        for dir_name, files in dir_groups.items():
            ungrouped = []
            for file_info in files:
                file_path = str(file_info.relative_path)
                if file_path not in grouped_file_paths:
                    ungrouped.append(file_info)
                    grouped_file_paths.add(file_path)

            if ungrouped:
                # Use directory name as group name
                group_name = self._normalize_group_name(dir_name)
                merged[group_name].extend(ungrouped)

        return dict(merged)

    def _normalize_group_name(self, name: str) -> str:
        """
        Normalize group name for consistency.

        Args:
            name: Raw group name

        Returns:
            Normalized group name
        """
        # Remove special characters and convert to lowercase
        normalized = re.sub(r'[^a-z0-9]+', '_', name.lower())
        normalized = normalized.strip('_')

        # Handle common abbreviations
        replacements = {
            'auth': 'authentication',
            'db': 'database',
            'util': 'utilities',
            'config': 'configuration',
        }

        return replacements.get(normalized, normalized)

    def _create_functionality_groups(
        self,
        groups: Dict[str, List[FileInfo]],
        all_files: List[FileInfo],
        dependency_graph: Dict[str, Set[str]]
    ) -> List[FunctionalityGroup]:
        """
        Create FunctionalityGroup objects from grouped files.

        Args:
            groups: Merged file groups (dict of group_id to list of FileInfo)
            all_files: All files in the project
            dependency_graph: File dependencies

        Returns:
            List of FunctionalityGroup objects
        """
        functionality_groups = []

        for group_id, files in groups.items():
            if not files:
                continue

            files_list = list(files)

            # Generate description
            description = self._generate_group_description(group_id, files_list)

            # Find entry points (files with no internal dependencies)
            entry_points = self._find_entry_points(files_list, dependency_graph)

            # Find dependencies (other groups this group depends on)
            dependencies = self._find_group_dependencies(files_list, groups, dependency_graph)

            # Calculate complexity score
            complexity_score = self._calculate_group_complexity(files_list)

            # Get file paths
            file_paths = [f.relative_path for f in files_list]

            # Determine category
            category = self._determine_category(group_id)

            group = FunctionalityGroup(
                id=group_id,
                name=self._format_group_name(group_id),
                description=description,
                files=file_paths,
                primary_files=file_paths[:3] if len(file_paths) > 3 else file_paths,  # First 3 as primary
                category=category,
                dependencies=dependencies,
                total_files=len(files_list),
                total_lines=sum(f.metrics.lines_of_code for f in files_list),
                complexity_score=complexity_score,
                purpose=description,
                key_features=entry_points[:5],  # Use entry points as key features
                documentation_path=None,
                analyzed_at=None,
            )

            functionality_groups.append(group)

        return functionality_groups

    def _generate_group_description(self, group_id: str, files: List[FileInfo]) -> str:
        """Generate a description for a functionality group."""
        # Use common patterns to generate description
        descriptions = {
            'authentication': 'User authentication, login, and session management',
            'database': 'Database models, schemas, and data access layer',
            'api': 'API endpoints, routes, and request handlers',
            'ui': 'User interface components and views',
            'testing': 'Test suites, fixtures, and testing utilities',
            'configuration': 'Application configuration and settings',
            'utilities': 'Utility functions and helper modules',
            'security': 'Security features, encryption, and access control',
            'payment': 'Payment processing and billing functionality',
            'notification': 'Notification system for emails, SMS, and push notifications',
        }

        if group_id in descriptions:
            return descriptions[group_id]

        # Generate generic description
        return f"Functionality group containing {len(files)} files"

    def _find_entry_points(
        self,
        files: List[FileInfo],
        dependency_graph: Dict[str, Set[str]]
    ) -> List[str]:
        """Find entry point files in a group."""
        entry_points = []
        file_paths = {str(f.relative_path) for f in files}

        for file_info in files:
            file_path = str(file_info.relative_path)

            # Check if file has main function or is a script
            has_main = any(
                elem.name in ['main', '__main__']
                for elem in file_info.code_elements
            )

            # Check if file has few internal dependencies
            deps = dependency_graph.get(file_path, set())
            internal_deps = deps & file_paths

            if has_main or len(internal_deps) == 0:
                # Extract function names for entry points
                functions = [elem.name for elem in file_info.get_functions()]
                if functions:
                    entry_points.extend([f"{file_path}:{func}" for func in functions[:3]])
                else:
                    entry_points.append(file_path)

        return entry_points[:5]  # Limit to top 5

    def _find_group_dependencies(
        self,
        files: List[FileInfo],
        all_groups: Dict[str, List[FileInfo]],
        dependency_graph: Dict[str, Set[str]]
    ) -> List[str]:
        """Find dependencies between functionality groups."""
        file_paths = {str(f.relative_path) for f in files}
        dependencies = set()

        # Build reverse mapping: file -> group
        file_to_group = {}
        for group_id, group_files in all_groups.items():
            for file_info in group_files:
                file_to_group[str(file_info.relative_path)] = group_id

        # Find external dependencies
        for file_info in files:
            file_path = str(file_info.relative_path)
            deps = dependency_graph.get(file_path, set())

            for dep in deps:
                if dep not in file_paths:  # External to this group
                    dep_group = file_to_group.get(dep)
                    if dep_group:
                        dependencies.add(dep_group)

        return sorted(list(dependencies))

    def _calculate_group_complexity(self, files: List[FileInfo]) -> float:
        """Calculate complexity score for a group."""
        if not files:
            return 0.0

        total_complexity = sum(f.metrics.complexity for f in files)
        total_files = len(files)
        total_lines = sum(f.metrics.lines_of_code for f in files)

        # Normalize to 0-10 scale
        avg_complexity_per_file = total_complexity / total_files if total_files > 0 else 0
        size_factor = min(total_lines / 1000, 5)  # Cap at 5

        complexity_score = min((avg_complexity_per_file / 10) + size_factor, 10)

        return round(complexity_score, 2)

    def _determine_category(self, group_id: str) -> str:
        """Determine category for a group based on its ID."""
        category_map = {
            'authentication': 'Security',
            'database': 'Data',
            'api': 'API',
            'ui': 'UI',
            'testing': 'Testing',
            'configuration': 'Configuration',
            'utilities': 'Utilities',
            'security': 'Security',
            'payment': 'Business Logic',
            'notification': 'Communication',
        }

        return category_map.get(group_id, 'General')

    def _format_group_name(self, group_id: str) -> str:
        """Format group ID into a readable name."""
        # Convert snake_case to Title Case
        words = group_id.replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in words)

# Made with Bob
