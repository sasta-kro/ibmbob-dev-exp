"""
Scanner Engine - File discovery and filtering for codebase analysis.

This module handles recursive directory traversal, gitignore-style pattern matching,
language detection, and file metadata extraction.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import fnmatch
import chardet

from ..models.file_info import FileInfo, FileType, FileMetrics
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


@dataclass
class ScanResult:
    """Result of scanning a project directory."""
    files: List[FileInfo] = field(default_factory=list)
    ignored_count: int = 0
    language_distribution: Dict[str, int] = field(default_factory=dict)
    total_size: int = 0
    total_lines: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class Scanner:
    """
    Scanner Engine for discovering and filtering project files.

    Features:
    - Recursive directory traversal
    - Gitignore-style pattern matching
    - Language/framework detection
    - File metadata extraction
    - Safe handling of large/binary files
    - Progress tracking for UI updates
    """

    # Language detection by file extension
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C/C++',
        '.hpp': 'C++',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.m': 'Objective-C',
        '.sql': 'SQL',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.ps1': 'PowerShell',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'Sass',
        '.less': 'Less',
        '.vue': 'Vue',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.md': 'Markdown',
        '.rst': 'reStructuredText',
    }

    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
        '.mp3', '.mp4', '.avi', '.mov', '.wav',
        '.zip', '.tar', '.gz', '.rar', '.7z',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.pyc', '.pyo', '.class', '.o', '.obj',
    }

    # Maximum file size to process (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, config: Config):
        """
        Initialize the scanner with configuration.

        Args:
            config: Configuration object with ignore patterns and settings
        """
        self.config = config
        self.ignore_patterns = self._load_ignore_patterns()
        self.progress_callback: Optional[Callable[[str, int, int], None]] = None

    def _load_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from config and default ignore file."""
        patterns = []

        # Load default ignore patterns
        default_ignore_path = Path(__file__).parent.parent.parent / 'config' / 'default_ignore.txt'
        if default_ignore_path.exists():
            with open(default_ignore_path, 'r') as f:
                patterns.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])

        # Add user-defined patterns from config
        if hasattr(self.config, 'ignore_patterns'):
            patterns.extend(self.config.ignore_patterns)

        return patterns

    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """
        Set a callback function for progress updates.

        Args:
            callback: Function(message, current, total) to call on progress
        """
        self.progress_callback = callback

    def scan(self, project_path: str) -> ScanResult:
        """
        Scan a project directory and return discovered files.

        Args:
            project_path: Path to the project root directory

        Returns:
            ScanResult containing discovered files and metadata
        """
        logger.info(f"Starting scan of project: {project_path}")

        project_path_obj = Path(project_path).resolve()
        if not project_path_obj.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if not project_path_obj.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        result = ScanResult()

        # Collect all files first for progress tracking
        all_files = list(self._walk_directory(project_path_obj))
        total_files = len(all_files)

        logger.info(f"Found {total_files} files to process")

        for idx, file_path in enumerate(all_files, 1):
            try:
                # Update progress
                if self.progress_callback:
                    self.progress_callback(f"Scanning {file_path.name}", idx, total_files)

                # Check if file should be ignored
                if self._should_ignore(file_path, project_path_obj):
                    result.ignored_count += 1
                    continue

                # Extract file information
                file_info = self._extract_file_info(file_path, project_path_obj)
                if file_info:
                    result.files.append(file_info)
                    result.total_size += file_info.size_bytes
                    result.total_lines += file_info.metrics.lines_of_code

                    # Update language distribution
                    lang = file_info.file_type.value
                    result.language_distribution[lang] = result.language_distribution.get(lang, 0) + 1

            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                logger.error(error_msg)
                result.errors.append(error_msg)

        logger.info(f"Scan complete: {len(result.files)} files, {result.ignored_count} ignored")
        return result

    def _walk_directory(self, root_path: Path) -> List[Path]:
        """
        Recursively walk directory and collect all file paths.

        Args:
            root_path: Root directory to walk

        Returns:
            List of file paths
        """
        files = []
        try:
            for entry in root_path.iterdir():
                if entry.is_file():
                    files.append(entry)
                elif entry.is_dir() and not self._should_ignore_dir(entry, root_path):
                    files.extend(self._walk_directory(entry))
        except PermissionError:
            logger.warning(f"Permission denied: {root_path}")
        except Exception as e:
            logger.error(f"Error walking directory {root_path}: {e}")

        return files

    def _should_ignore_dir(self, dir_path: Path, root_path: Path) -> bool:
        """
        Check if a directory should be ignored.

        Args:
            dir_path: Directory path to check
            root_path: Project root path

        Returns:
            True if directory should be ignored
        """
        dir_name = dir_path.name

        # Common directories to always ignore
        if dir_name in {'.git', '.svn', '.hg', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.codebase-analyzer'}:
            return True

        # Check against ignore patterns
        relative_path = dir_path.relative_to(root_path)
        return self._matches_ignore_pattern(str(relative_path))

    def _should_ignore(self, file_path: Path, root_path: Path) -> bool:
        """
        Check if a file should be ignored based on patterns.

        Args:
            file_path: File path to check
            root_path: Project root path

        Returns:
            True if file should be ignored
        """
        # Check file extension
        if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
            return True

        # Check file size
        try:
            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                logger.warning(f"Skipping large file: {file_path} ({file_path.stat().st_size} bytes)")
                return True
        except Exception:
            return True

        # Check against ignore patterns
        relative_path = file_path.relative_to(root_path)
        return self._matches_ignore_pattern(str(relative_path))

    def _matches_ignore_pattern(self, path: str) -> bool:
        """
        Check if path matches any ignore pattern.

        Args:
            path: Relative path to check

        Returns:
            True if path matches an ignore pattern
        """
        path = path.replace('\\', '/')  # Normalize path separators

        for pattern in self.ignore_patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if path.startswith(pattern) or f"/{pattern}" in f"/{path}/":
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True

        return False

    def _extract_file_info(self, file_path: Path, root_path: Path) -> Optional[FileInfo]:
        """
        Extract metadata and information from a file.

        Args:
            file_path: Path to the file
            root_path: Project root path

        Returns:
            FileInfo object or None if file cannot be processed
        """
        try:
            stat = file_path.stat()
            relative_path = file_path.relative_to(root_path)

            # Detect file type
            file_type = self._detect_file_type(file_path)

            # Read file content
            content = self._read_file_content(file_path)
            if content is None:
                return None

            # Count lines
            line_count = content.count('\n') + 1 if content else 0

            # Calculate hash
            content_hash = hashlib.sha256(content.encode('utf-8', errors='ignore')).hexdigest()

            # Create metrics
            metrics = FileMetrics(lines_of_code=line_count)

            return FileInfo(
                path=file_path,
                relative_path=relative_path,
                name=file_path.name,
                extension=file_path.suffix,
                file_type=file_type,
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                encoding='utf-8',
                content_hash=content_hash,
                metrics=metrics,
                ai_summary=None,
                ai_purpose=None,
            )

        except Exception as e:
            logger.error(f"Error extracting file info for {file_path}: {e}")
            return None

    def _detect_file_type(self, file_path: Path) -> FileType:
        """
        Detect file type from file extension.

        Args:
            file_path: Path to the file

        Returns:
            FileType enum value
        """
        extension = file_path.suffix.lower()

        # Map extensions to FileType enum
        type_map = {
            '.py': FileType.PYTHON,
            '.js': FileType.JAVASCRIPT,
            '.jsx': FileType.JAVASCRIPT,
            '.ts': FileType.TYPESCRIPT,
            '.tsx': FileType.TYPESCRIPT,
            '.json': FileType.JSON,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML,
            '.md': FileType.MARKDOWN,
            '.txt': FileType.TEXT,
        }

        return type_map.get(extension, FileType.UNKNOWN)

    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Safely read file content with encoding detection.

        Args:
            file_path: Path to the file

        Returns:
            File content as string or None if cannot read
        """
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try to detect encoding
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']

                if encoding:
                    return raw_data.decode(encoding, errors='ignore')
            except Exception as e:
                logger.warning(f"Could not read file {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")

        return None

    def detect_framework(self, project_path: str) -> Dict[str, bool]:
        """
        Detect frameworks and technologies used in the project.

        Args:
            project_path: Path to the project root

        Returns:
            Dictionary of detected frameworks
        """
        project_path_obj = Path(project_path)
        frameworks = {
            'react': False,
            'vue': False,
            'angular': False,
            'django': False,
            'flask': False,
            'fastapi': False,
            'express': False,
            'nextjs': False,
            'spring': False,
        }

        # Check for package.json (Node.js projects)
        package_json = project_path_obj / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

                    if 'react' in deps:
                        frameworks['react'] = True
                    if 'vue' in deps:
                        frameworks['vue'] = True
                    if '@angular/core' in deps:
                        frameworks['angular'] = True
                    if 'express' in deps:
                        frameworks['express'] = True
                    if 'next' in deps:
                        frameworks['nextjs'] = True
            except Exception as e:
                logger.warning(f"Error reading package.json: {e}")

        # Check for requirements.txt (Python projects)
        requirements = project_path_obj / 'requirements.txt'

        if requirements.exists():
            try:
                with open(requirements, 'r') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        frameworks['django'] = True
                    if 'flask' in content:
                        frameworks['flask'] = True
                    if 'fastapi' in content:
                        frameworks['fastapi'] = True
            except Exception as e:
                logger.warning(f"Error reading requirements.txt: {e}")

        # Check for pom.xml (Java/Spring projects)
        pom_xml = project_path_obj / 'pom.xml'
        if pom_xml.exists():
            try:
                with open(pom_xml, 'r') as f:
                    content = f.read()
                    if 'spring' in content.lower():
                        frameworks['spring'] = True
            except Exception as e:
                logger.warning(f"Error reading pom.xml: {e}")

        return frameworks

# Made with Bob
