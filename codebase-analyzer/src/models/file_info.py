"""File information data model."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FileType(str, Enum):
    """File type enumeration."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"
    UNKNOWN = "unknown"


class CodeElement(BaseModel):
    """Represents a code element (function, class, method, etc.)."""
    name: str = Field(..., description="Name of the code element")
    type: str = Field(..., description="Type: function, class, method, variable, etc.")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")
    docstring: Optional[str] = Field(None, description="Documentation string")
    complexity: Optional[int] = Field(None, description="Cyclomatic complexity")
    parameters: List[str] = Field(default_factory=list, description="Function/method parameters")
    return_type: Optional[str] = Field(None, description="Return type annotation")
    decorators: List[str] = Field(default_factory=list, description="Decorators applied")
    is_async: bool = Field(False, description="Whether function/method is async")
    is_private: bool = Field(False, description="Whether element is private")
    parent: Optional[str] = Field(None, description="Parent class for methods")


class ImportInfo(BaseModel):
    """Represents an import statement."""
    module: str = Field(..., description="Module being imported")
    names: List[str] = Field(default_factory=list, description="Specific names imported")
    alias: Optional[str] = Field(None, description="Import alias")
    is_relative: bool = Field(False, description="Whether import is relative")
    line_number: int = Field(..., description="Line number of import")


class FileMetrics(BaseModel):
    """Code metrics for a file."""
    lines_of_code: int = Field(default=0, description="Total lines of code")
    blank_lines: int = Field(default=0, description="Number of blank lines")
    comment_lines: int = Field(default=0, description="Number of comment lines")
    complexity: int = Field(default=0, description="Total cyclomatic complexity")
    maintainability_index: Optional[float] = Field(default=None, description="Maintainability index (0-100)")
    functions_count: int = Field(default=0, description="Number of functions")
    classes_count: int = Field(default=0, description="Number of classes")
    methods_count: int = Field(default=0, description="Number of methods")


class FileInfo(BaseModel):
    """Complete information about a source code file."""

    # Basic file information
    path: Path = Field(..., description="Absolute path to the file")
    relative_path: Path = Field(..., description="Path relative to project root")
    name: str = Field(..., description="File name")
    extension: str = Field(..., description="File extension")
    file_type: FileType = Field(..., description="Detected file type")
    size_bytes: int = Field(..., description="File size in bytes")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="File creation time")
    modified_at: Optional[datetime] = Field(None, description="Last modification time")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    # Content
    encoding: str = Field("utf-8", description="File encoding")
    content_hash: Optional[str] = Field(None, description="SHA256 hash of content")

    # Code structure
    imports: List[ImportInfo] = Field(default_factory=list, description="Import statements")
    exports: List[str] = Field(default_factory=list, description="Exported names")
    code_elements: List[CodeElement] = Field(default_factory=list, description="Functions, classes, etc.")

    # Dependencies
    dependencies: List[str] = Field(default_factory=list, description="External dependencies")
    internal_dependencies: List[Path] = Field(default_factory=list, description="Internal file dependencies")

    # Metrics
    metrics: FileMetrics = Field(default_factory=lambda: FileMetrics(), description="Code metrics")

    # Analysis results
    language_features: Dict[str, bool] = Field(default_factory=dict, description="Language features used")
    frameworks_detected: List[str] = Field(default_factory=list, description="Detected frameworks")

    # AI-generated content
    ai_summary: Optional[str] = Field(None, description="AI-generated file summary")
    ai_purpose: Optional[str] = Field(None, description="AI-detected file purpose")

    # Errors and warnings
    parse_errors: List[str] = Field(default_factory=list, description="Parsing errors")
    warnings: List[str] = Field(default_factory=list, description="Analysis warnings")

    model_config = ConfigDict(json_encoders={Path: str, datetime: lambda v: v.isoformat()})

    def get_functions(self) -> List[CodeElement]:
        """Get all functions in the file."""
        return [e for e in self.code_elements if e.type == "function"]

    def get_classes(self) -> List[CodeElement]:
        """Get all classes in the file."""
        return [e for e in self.code_elements if e.type == "class"]

    def get_methods(self) -> List[CodeElement]:
        """Get all methods in the file."""
        return [e for e in self.code_elements if e.type == "method"]

    def get_public_api(self) -> List[CodeElement]:
        """Get public API elements (non-private functions and classes)."""
        return [e for e in self.code_elements if not e.is_private and e.type in ["function", "class"]]

    def has_errors(self) -> bool:
        """Check if file has parsing errors."""
        return len(self.parse_errors) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')

# Made with Bob
