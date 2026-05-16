"""
Orchestrator - Main coordinator for the codebase analysis pipeline.

This module coordinates all analysis engines and services to provide a unified
interface for analyzing codebases.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from .scanner import Scanner, ScanResult
from .analyzer import AnalyzerEngine
from .grouper import FunctionalityGrouper
from ..services.watson_service import WatsonService
from ..services.cache_service import CacheService
from ..generators.markdown_generator import MarkdownGenerator
from ..generators.index_generator import IndexGenerator
from ..models.project import Project
from ..models.file_info import FileInfo
from ..models.functionality import FunctionalityGroup, FunctionalityMap
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class AnalysisOrchestrator:
    """
    Main orchestrator for codebase analysis.
    
    Coordinates:
    - File scanning and discovery
    - Static code analysis
    - AI-powered semantic analysis
    - Functionality grouping
    - Result caching
    - Progress tracking
    """
    
    def __init__(self, config: Config):
        """
        Initialize the orchestrator with all required services.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize core engines
        self.scanner = Scanner(config)
        self.analyzer = AnalyzerEngine(config)
        self.grouper = FunctionalityGrouper(config)
        
        # Initialize services
        self.watson_service = WatsonService(config)
        self.cache_service = CacheService(config)
        
        # Initialize generators
        self.markdown_generator = MarkdownGenerator(config)
        self.index_generator = IndexGenerator()
        
        # Progress tracking
        self.progress_callback: Optional[Callable[[str, int, int], None]] = None
        
        logger.info("Analysis orchestrator initialized")
    
    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """
        Set callback for progress updates.
        
        Args:
            callback: Function(message, current, total) to call on progress
        """
        self.progress_callback = callback
        self.scanner.set_progress_callback(callback)
    
    def analyze_project(
        self,
        project_path: str,
        use_cache: bool = True,
        use_ai: bool = True
    ) -> Project:
        """
        Perform complete analysis of a project.
        
        Args:
            project_path: Path to the project root directory
            use_cache: Whether to use cached results
            use_ai: Whether to use AI-powered analysis
            
        Returns:
            Project object with complete analysis results
        """
        logger.info(f"Starting project analysis: {project_path}")
        start_time = datetime.now()
        
        project_path_obj = Path(project_path).resolve()
        
        # Check cache for project metadata
        if use_cache:
            cached_metadata = self.cache_service.get_project_metadata(str(project_path_obj))
            if cached_metadata:
                logger.info("Found cached project metadata")
                # Could return cached project here if desired
        
        # Step 1: Scan project files
        self._update_progress("Scanning project files...", 0, 100)
        scan_result = self.scanner.scan(str(project_path_obj))
        
        if not scan_result.files:
            logger.warning("No files found to analyze")
            return self._create_empty_project(project_path_obj)
        
        logger.info(f"Scanned {len(scan_result.files)} files")
        
        # Step 2: Analyze files
        self._update_progress("Analyzing code structure...", 20, 100)
        analyzed_files = self._analyze_files(scan_result.files, use_cache)
        
        # Step 3: AI-powered analysis (if enabled)
        if use_ai and self.watson_service.is_available():
            self._update_progress("Running AI analysis...", 50, 100)
            analyzed_files = self._enhance_with_ai(analyzed_files, use_cache)
        else:
            logger.info("Skipping AI analysis (disabled or unavailable)")
        
        # Step 4: Group files by functionality
        self._update_progress("Grouping functionality...", 70, 100)
        functionality_groups = self.grouper.group_files(analyzed_files, str(project_path_obj))
        
        # Step 5: Detect frameworks and technologies
        self._update_progress("Detecting frameworks...", 85, 100)
        frameworks = self.scanner.detect_framework(str(project_path_obj))
        
        # Step 6: Create project object
        self._update_progress("Finalizing analysis...", 95, 100)
        project = self._create_project(
            project_path_obj,
            analyzed_files,
            functionality_groups,
            frameworks,
            scan_result
        )
        
        # Cache project metadata
        if use_cache:
            self._cache_project_metadata(project)
        
        # Cleanup expired cache entries
        self.cache_service.cleanup_expired()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Project analysis completed in {duration:.2f} seconds")
        self._update_progress("Analysis complete!", 100, 100)
        return project
        
    
    def generate_documentation(
        self,
        project: Project,
        output_dir: Optional[str] = None
    ) -> Path:
        """
        Generate documentation for the analyzed project.
        
        Args:
            project: Analyzed project object
            output_dir: Optional output directory path (defaults to './docs')
            
        Returns:
            Path to generated documentation directory
        """
        logger.info("Starting documentation generation")
        
        # Use default output directory if not specified
        if output_dir is None:
            output_dir = './docs'
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate markdown documentation
        doc_files = self.markdown_generator.generate_project_documentation(project, output_path)
        api_reference_path = self.markdown_generator.generate_api_reference(
            project,
            output_path / 'API_REFERENCE.md'
        )
        doc_files['api_reference'] = api_reference_path
        
        # Generate index file
        index_path = output_path / 'INDEX.md'
        self.index_generator.generate_index(project, doc_files, index_path)
        
        logger.info(f"Documentation generated at: {output_path}")
        return output_path
    
    def _analyze_files(
        self,
        files: list[FileInfo],
        use_cache: bool
    ) -> list[FileInfo]:
        """
        Analyze files with caching support.
        
        Args:
            files: List of FileInfo objects
            use_cache: Whether to use cache
            
        Returns:
            List of analyzed FileInfo objects
        """
        analyzed_files = []
        
        for file_info in files:
            # Check cache
            if use_cache and file_info.content_hash:
                cached = self.cache_service.get_file_analysis(
                    str(file_info.relative_path),
                    file_info.content_hash
                )
                if cached:
                    # Reconstruct FileInfo from cached data
                    # For now, just use the analyzer
                    pass
            
            # Analyze file
            analyzed = self.analyzer.analyze_file(file_info)
            if analyzed:
                analyzed_files.append(analyzed)
                
                # Cache the result
                if use_cache and analyzed.content_hash:
                    self.cache_service.set_file_analysis(
                        str(analyzed.relative_path),
                        analyzed.content_hash,
                        analyzed.to_dict()
                    )
        
        return analyzed_files
    
    def _enhance_with_ai(
        self,
        files: list[FileInfo],
        use_cache: bool
    ) -> list[FileInfo]:
        """
        Enhance file analysis with AI insights.
        
        Args:
            files: List of analyzed FileInfo objects
            use_cache: Whether to use cache
            
        Returns:
            List of FileInfo objects with AI enhancements
        """
        enhanced_files = []
        
        # Only analyze a subset of important files to save API calls
        important_files = self._select_important_files(files)
        
        logger.info(f"Running AI analysis on {len(important_files)} important files")
        
        for file_info in files:
            if file_info in important_files:
                try:
                    # Read file content
                    with open(file_info.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Get AI analysis
                    ai_result = self.watson_service.analyze_code(
                        content,
                        str(file_info.relative_path),
                        file_info.file_type.value,
                        use_cache=use_cache
                    )
                    
                    if ai_result:
                        file_info.ai_summary = ai_result.summary
                        file_info.ai_purpose = ai_result.purpose
                        
                        # Add detected frameworks
                        if ai_result.functionality:
                            file_info.frameworks_detected.extend(ai_result.functionality)
                    
                except Exception as e:
                    logger.error(f"Error in AI analysis for {file_info.path}: {e}")
            
            enhanced_files.append(file_info)
        
        return enhanced_files
    
    def _select_important_files(self, files: list[FileInfo]) -> list[FileInfo]:
        """
        Select important files for AI analysis to optimize API usage.
        
        Args:
            files: All files
            
        Returns:
            Subset of important files
        """
        important = []
        
        for file_info in files:
            # Include files with high complexity
            if file_info.metrics.complexity > 10:
                important.append(file_info)
                continue
            
            # Include files with many functions/classes
            if file_info.metrics.functions_count + file_info.metrics.classes_count > 5:
                important.append(file_info)
                continue
            
            # Include main entry points
            if 'main' in file_info.name.lower() or '__init__' in file_info.name:
                important.append(file_info)
                continue
        
        # Limit to top 50 files
        return important[:50]
    
    def _create_project(
        self,
        project_path: Path,
        files: list[FileInfo],
        functionality_groups: list[FunctionalityGroup],
        frameworks: Dict[str, bool],
        scan_result: ScanResult
    ) -> Project:
        """
        Create a Project object from analysis results.
        
        Args:
            project_path: Project root path
            files: Analyzed files
            functionality_groups: Functionality groups
            frameworks: Detected frameworks
            scan_result: Scan results
            
        Returns:
            Project object
        """
        # Create functionality map
        func_map = FunctionalityMap()
        for group in functionality_groups:
            func_map.add_group(group)
        
        # Get detected frameworks
        detected_frameworks = [name for name, detected in frameworks.items() if detected]
        
        # Create project with required fields
        project = Project(
            id=f"project_{project_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=project_path.name,
            description=f"Codebase analysis of {project_path.name}",
            root_paths=[project_path],
            output_path=None,
            functionality_map=func_map,
            finding_summary=None,
            suggestion_summary=None,
            last_analyzed=datetime.now(),
        )
        
        # Add all files to project
        for file_info in files:
            project.add_file(file_info)
        
        # Metrics will be auto-updated by add_file
        
        return project
    
    def _create_empty_project(self, project_path: Path) -> Project:
        """Create an empty project object."""
        return Project(
            id=f"project_{project_path.name}_empty",
            name=project_path.name,
            description=f"Empty project: {project_path.name}",
            root_paths=[project_path],
            output_path=None,
            functionality_map=FunctionalityMap(),
            finding_summary=None,
            suggestion_summary=None,
            last_analyzed=None,
        )
    
    def _detect_primary_language(self, language_dist: Dict[str, int]) -> str:
        """Detect primary programming language from distribution."""
        if not language_dist:
            return "unknown"
        
        # Find language with most files
        primary = max(language_dist.items(), key=lambda x: x[1])
        return primary[0]
    
    def _cache_project_metadata(self, project: Project):
        """Cache project metadata."""
        try:
            metadata = {
                'id': project.id,
                'name': project.name,
                'root_paths': [str(p) for p in project.root_paths],
                'total_files': project.metrics.total_files,
                'total_lines': project.metrics.total_lines,
                'frameworks': project.metrics.frameworks,
                'last_analyzed': project.last_analyzed.isoformat() if project.last_analyzed else None,
            }
            root_path = str(project.root_paths[0]) if project.root_paths else ''
            self.cache_service.set_project_metadata(root_path, metadata)
        except Exception as e:
            logger.error(f"Error caching project metadata: {e}")
    
    def _update_progress(self, message: str, current: int, total: int):
        """Update progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(message, current, total)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache_service.get_stats()
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache_service.clear_all()
        self.watson_service.clear_cache()
        logger.info("All caches cleared")

# Made with Bob
