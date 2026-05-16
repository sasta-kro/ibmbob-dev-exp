"""Code review finding data model."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(str, Enum):
    """Types of code review findings."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    BEST_PRACTICE = "best_practice"


class CodeLocation(BaseModel):
    """Location of code in a file."""
    file_path: Path = Field(..., description="Path to the file")
    line_start: int = Field(..., description="Starting line number")
    line_end: int = Field(..., description="Ending line number")
    column_start: Optional[int] = Field(None, description="Starting column")
    column_end: Optional[int] = Field(None, description="Ending column")
    code_snippet: Optional[str] = Field(None, description="Code snippet")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {Path: str}


class Finding(BaseModel):
    """Represents a code review finding."""
    
    # Identification
    id: str = Field(..., description="Unique finding identifier")
    title: str = Field(..., description="Short title of the finding")
    description: str = Field(..., description="Detailed description")
    
    # Classification
    severity: Severity = Field(..., description="Severity level")
    finding_type: FindingType = Field(..., description="Type of finding")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    
    # Location
    location: CodeLocation = Field(..., description="Code location")
    
    # Details
    message: str = Field(..., description="Detailed message")
    explanation: Optional[str] = Field(None, description="Why this is an issue")
    impact: Optional[str] = Field(None, description="Potential impact")
    
    # Remediation
    recommendation: Optional[str] = Field(None, description="How to fix")
    suggested_fix: Optional[str] = Field(None, description="Suggested code fix")
    references: List[str] = Field(default_factory=list, description="Reference links")
    
    # Source
    source: str = Field(..., description="Tool/analyzer that found this (e.g., pylint, bandit, AI)")
    rule_id: Optional[str] = Field(None, description="Rule or check ID")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.now, description="When finding was created")
    
    # Status
    is_false_positive: bool = Field(default=False, description="Marked as false positive")
    is_resolved: bool = Field(default=False, description="Marked as resolved")
    notes: Optional[str] = Field(None, description="User notes")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }
    
    def get_severity_score(self) -> int:
        """
        Get numeric severity score for sorting.
        
        Returns:
            Severity score (5=critical, 1=info)
        """
        severity_scores = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1
        }
        return severity_scores.get(self.severity, 0)
    
    def is_actionable(self) -> bool:
        """Check if finding requires action (not info level)."""
        return self.severity != Severity.INFO
    
    def is_security_related(self) -> bool:
        """Check if finding is security-related."""
        return self.finding_type == FindingType.SECURITY
    
    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')


class FindingSummary(BaseModel):
    """Summary of findings for a project or file."""
    total_findings: int = Field(default=0, description="Total number of findings")
    by_severity: dict[Severity, int] = Field(default_factory=dict, description="Count by severity")
    by_type: dict[FindingType, int] = Field(default_factory=dict, description="Count by type")
    critical_count: int = Field(default=0, description="Number of critical findings")
    high_count: int = Field(default=0, description="Number of high severity findings")
    medium_count: int = Field(default=0, description="Number of medium severity findings")
    low_count: int = Field(default=0, description="Number of low severity findings")
    info_count: int = Field(default=0, description="Number of info findings")
    security_count: int = Field(default=0, description="Number of security findings")
    resolved_count: int = Field(default=0, description="Number of resolved findings")
    false_positive_count: int = Field(default=0, description="Number of false positives")
    
    @classmethod
    def from_findings(cls, findings: List[Finding]) -> "FindingSummary":
        """
        Create summary from list of findings.
        
        Args:
            findings: List of findings
            
        Returns:
            FindingSummary instance
        """
        summary = cls()
        summary.total_findings = len(findings)
        
        # Count by severity
        for severity in Severity:
            summary.by_severity[severity] = sum(1 for f in findings if f.severity == severity)
        
        # Count by type
        for finding_type in FindingType:
            summary.by_type[finding_type] = sum(1 for f in findings if f.finding_type == finding_type)
        
        # Individual counts
        summary.critical_count = summary.by_severity.get(Severity.CRITICAL, 0)
        summary.high_count = summary.by_severity.get(Severity.HIGH, 0)
        summary.medium_count = summary.by_severity.get(Severity.MEDIUM, 0)
        summary.low_count = summary.by_severity.get(Severity.LOW, 0)
        summary.info_count = summary.by_severity.get(Severity.INFO, 0)
        
        summary.security_count = summary.by_type.get(FindingType.SECURITY, 0)
        summary.resolved_count = sum(1 for f in findings if f.is_resolved)
        summary.false_positive_count = sum(1 for f in findings if f.is_false_positive)
        
        return summary
    
    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')

# Made with Bob
