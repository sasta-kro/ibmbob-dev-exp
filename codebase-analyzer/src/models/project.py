"""Project data model."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .file_info import FileInfo
from .finding import Finding, FindingSummary
from .functionality import FunctionalityMap
from .suggestion import Suggestion, SuggestionSummary


class ProjectMetrics(BaseModel):
    """Overall project metrics."""
    total_files: int = Field(default=0, description="Total number of files")
    total_lines: int = Field(default=0, description="Total lines of code")
    total_functions: int = Field(default=0, description="Total number of functions")
    total_classes: int = Field(default=0, description="Total number of classes")
    average_complexity: float = Field(default=0.0, description="Average complexity")
    languages: Dict[str, int] = Field(default_factory=dict, description="File count by language")
    frameworks: List[str] = Field(default_factory=list, description="Detected frameworks")


class AnalysisStatus(BaseModel):
    """Status of project analysis."""
    is_scanning: bool = Field(default=False, description="Currently scanning files")
    is_analyzing: bool = Field(default=False, description="Currently analyzing code")
    is_reviewing: bool = Field(default=False, description="Currently reviewing code")
    is_generating_docs: bool = Field(default=False, description="Currently generating documentation")

    scan_progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Scan progress percentage")
    analysis_progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Analysis progress percentage")
    review_progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Review progress percentage")
    docs_progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Documentation progress percentage")

    current_file: Optional[str] = Field(default=None, description="Currently processing file")
    files_processed: int = Field(default=0, description="Number of files processed")
    files_total: int = Field(default=0, description="Total files to process")

    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Warnings")

    started_at: Optional[datetime] = Field(default=None, description="Analysis start time")
    completed_at: Optional[datetime] = Field(default=None, description="Analysis completion time")

    def get_overall_progress(self) -> float:
        """Get overall progress percentage."""
        if self.files_total == 0:
            return 0.0
        return (self.files_processed / self.files_total) * 100.0

    def is_complete(self) -> bool:
        """Check if analysis is complete."""
        return (
            not self.is_scanning and
            not self.is_analyzing and
            not self.is_reviewing and
            not self.is_generating_docs and
            self.completed_at is not None
        )

    def has_errors(self) -> bool:
        """Check if there are errors."""
        return len(self.errors) > 0


class Project(BaseModel):
    """Represents a complete analyzed project."""

    # Identification
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")

    # Paths
    root_paths: List[Path] = Field(..., description="Root directories analyzed")
    output_path: Optional[Path] = Field(None, description="Output directory for generated files")

    # Files
    files: Dict[str, FileInfo] = Field(
        default_factory=dict,
        description="Map of file path to FileInfo"
    )

    # Analysis results
    functionality_map: Optional[FunctionalityMap] = Field(None, description="Functionality groups")
    findings: List[Finding] = Field(default_factory=list, description="Code review findings")
    suggestions: List[Suggestion] = Field(default_factory=list, description="Improvement suggestions")

    # Summaries
    finding_summary: Optional[FindingSummary] = Field(None, description="Findings summary")
    suggestion_summary: Optional[SuggestionSummary] = Field(None, description="Suggestions summary")

    # Metrics
    metrics: ProjectMetrics = Field(default_factory=ProjectMetrics, description="Project metrics")

    # Status
    status: AnalysisStatus = Field(default_factory=AnalysisStatus, description="Analysis status")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Project creation time")
    last_analyzed: Optional[datetime] = Field(None, description="Last analysis time")
    version: str = Field(default="1.0.0", description="Project version")

    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Project-specific configuration")

    model_config = ConfigDict(
        json_encoders={Path: str, datetime: lambda v: v.isoformat()},
        arbitrary_types_allowed=True
    )

    def add_file(self, file_info: FileInfo) -> None:
        """Add a file to the project."""
        self.files[str(file_info.relative_path)] = file_info
        self._update_metrics()

    def get_file(self, path: str) -> Optional[FileInfo]:
        """Get file info by path."""
        return self.files.get(path)

    def get_all_files(self) -> List[FileInfo]:
        """Get all files as a list."""
        return list(self.files.values())

    def add_finding(self, finding: Finding) -> None:
        """Add a code review finding."""
        self.findings.append(finding)
        self._update_finding_summary()

    def add_suggestion(self, suggestion: Suggestion) -> None:
        """Add an improvement suggestion."""
        self.suggestions.append(suggestion)
        self._update_suggestion_summary()

    def get_findings_by_severity(self, severity: str) -> List[Finding]:
        """Get findings filtered by severity."""
        from .finding import Severity
        return [f for f in self.findings if f.severity == Severity(severity)]

    def get_critical_findings(self) -> List[Finding]:
        """Get critical severity findings."""
        from .finding import Severity
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    def get_security_findings(self) -> List[Finding]:
        """Get security-related findings."""
        return [f for f in self.findings if f.is_security_related()]

    def get_quick_win_suggestions(self) -> List[Suggestion]:
        """Get quick win suggestions (low effort, high impact)."""
        return [s for s in self.suggestions if s.is_quick_win()]

    def get_high_priority_suggestions(self) -> List[Suggestion]:
        """Get high priority suggestions."""
        return [s for s in self.suggestions if s.is_high_priority()]

    def _update_metrics(self) -> None:
        """Update project metrics based on current files."""
        self.metrics.total_files = len(self.files)
        self.metrics.total_lines = sum(f.metrics.lines_of_code for f in self.files.values())
        self.metrics.total_functions = sum(f.metrics.functions_count for f in self.files.values())
        self.metrics.total_classes = sum(f.metrics.classes_count for f in self.files.values())

        # Calculate average complexity
        total_complexity = sum(f.metrics.complexity for f in self.files.values())
        self.metrics.average_complexity = total_complexity / len(self.files) if self.files else 0.0

        # Count files by language
        self.metrics.languages = {}
        for file_info in self.files.values():
            lang = file_info.file_type.value
            self.metrics.languages[lang] = self.metrics.languages.get(lang, 0) + 1

        # Collect frameworks
        frameworks = set()
        for file_info in self.files.values():
            frameworks.update(file_info.frameworks_detected)
        self.metrics.frameworks = sorted(list(frameworks))

    def _update_finding_summary(self) -> None:
        """Update finding summary."""
        self.finding_summary = FindingSummary.from_findings(self.findings)

    def _update_suggestion_summary(self) -> None:
        """Update suggestion summary."""
        self.suggestion_summary = SuggestionSummary.from_suggestions(self.suggestions)

    def start_analysis(self) -> None:
        """Mark analysis as started."""
        self.status.started_at = datetime.now()
        self.status.is_scanning = True

    def complete_analysis(self) -> None:
        """Mark analysis as completed."""
        self.status.completed_at = datetime.now()
        self.status.is_scanning = False
        self.status.is_analyzing = False
        self.status.is_reviewing = False
        self.status.is_generating_docs = False
        self.last_analyzed = datetime.now()

    def get_file_count(self) -> int:
        """Get total number of files."""
        return len(self.files)

    def get_total_findings(self) -> int:
        """Get total number of findings."""
        return len(self.findings)

    def get_total_suggestions(self) -> int:
        """Get total number of suggestions."""
        return len(self.suggestions)

    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')

    def save_to_file(self, path: Path) -> None:
        """Save project to JSON file."""
        import json
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, path: Path) -> "Project":
        """Load project from JSON file."""
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

# Made with Bob
