"""Improvement suggestion data model."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EffortLevel(str, Enum):
    """Effort required to implement suggestion."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ImpactLevel(str, Enum):
    """Expected impact of implementing suggestion."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SuggestionCategory(str, Enum):
    """Categories of improvement suggestions."""
    REFACTORING = "refactoring"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"


class SuggestionStatus(str, Enum):
    """Status of suggestion implementation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class ImplementationStep(BaseModel):
    """A step in implementing a suggestion."""
    order: int = Field(..., description="Step order")
    description: str = Field(..., description="Step description")
    code_example: Optional[str] = Field(None, description="Code example for this step")
    estimated_time: Optional[str] = Field(None, description="Estimated time (e.g., '30 minutes')")


class Suggestion(BaseModel):
    """Represents an improvement suggestion."""

    # Identification
    id: str = Field(..., description="Unique suggestion identifier")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Detailed description")

    # Classification
    category: SuggestionCategory = Field(..., description="Suggestion category")
    effort: EffortLevel = Field(..., description="Implementation effort")
    impact: ImpactLevel = Field(..., description="Expected impact")
    priority_score: float = Field(..., ge=0.0, le=100.0, description="Priority score (0-100)")

    # Context
    related_files: List[Path] = Field(default_factory=list, description="Files affected")
    related_findings: List[str] = Field(default_factory=list, description="Related finding IDs")

    # Details
    rationale: str = Field(..., description="Why this improvement is needed")
    benefits: List[str] = Field(default_factory=list, description="Expected benefits")
    considerations: List[str] = Field(default_factory=list, description="Things to consider")
    risks: List[str] = Field(default_factory=list, description="Potential risks")

    # Implementation
    implementation_steps: List[ImplementationStep] = Field(
        default_factory=list,
        description="Step-by-step implementation guide"
    )
    code_example: Optional[str] = Field(None, description="Example implementation")
    estimated_time: Optional[str] = Field(None, description="Total estimated time")

    # Resources
    references: List[str] = Field(default_factory=list, description="Reference links")
    tools: List[str] = Field(default_factory=list, description="Recommended tools")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies to install")

    # Source
    source: str = Field(..., description="Source of suggestion (AI, static analysis, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    # Status
    status: SuggestionStatus = Field(default=SuggestionStatus.PENDING, description="Implementation status")
    assigned_to: Optional[str] = Field(None, description="Person assigned")
    notes: Optional[str] = Field(None, description="User notes")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(json_encoders={Path: str, datetime: lambda v: v.isoformat()})

    def get_effort_score(self) -> int:
        """
        Get numeric effort score.

        Returns:
            Effort score (3=high, 1=low)
        """
        effort_scores = {
            EffortLevel.HIGH: 3,
            EffortLevel.MEDIUM: 2,
            EffortLevel.LOW: 1
        }
        return effort_scores.get(self.effort, 0)

    def get_impact_score(self) -> int:
        """
        Get numeric impact score.

        Returns:
            Impact score (3=high, 1=low)
        """
        impact_scores = {
            ImpactLevel.HIGH: 3,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.LOW: 1
        }
        return impact_scores.get(self.impact, 0)

    def is_quick_win(self) -> bool:
        """Check if this is a quick win (low effort, high impact)."""
        return self.effort == EffortLevel.LOW and self.impact == ImpactLevel.HIGH

    def is_high_priority(self) -> bool:
        """Check if this is high priority (score >= 70)."""
        return self.priority_score >= 70.0

    def calculate_priority_score(self) -> float:
        """
        Calculate priority score based on effort and impact.

        Returns:
            Priority score (0-100)
        """
        impact_score = self.get_impact_score()
        effort_score = self.get_effort_score()

        # Higher impact and lower effort = higher priority
        # Formula: (impact * 30) + ((4 - effort) * 20) + (confidence * 20)
        score = (impact_score * 30) + ((4 - effort_score) * 20) + (self.confidence * 20)
        return min(100.0, max(0.0, score))

    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')


class SuggestionSummary(BaseModel):
    """Summary of suggestions for a project."""
    total_suggestions: int = Field(default=0, description="Total number of suggestions")
    by_category: dict[SuggestionCategory, int] = Field(default_factory=dict, description="Count by category")
    by_effort: dict[EffortLevel, int] = Field(default_factory=dict, description="Count by effort")
    by_impact: dict[ImpactLevel, int] = Field(default_factory=dict, description="Count by impact")
    by_status: dict[SuggestionStatus, int] = Field(default_factory=dict, description="Count by status")
    quick_wins_count: int = Field(default=0, description="Number of quick wins")
    high_priority_count: int = Field(default=0, description="Number of high priority suggestions")
    pending_count: int = Field(default=0, description="Number of pending suggestions")
    completed_count: int = Field(default=0, description="Number of completed suggestions")

    @classmethod
    def from_suggestions(cls, suggestions: List[Suggestion]) -> "SuggestionSummary":
        """
        Create summary from list of suggestions.

        Args:
            suggestions: List of suggestions

        Returns:
            SuggestionSummary instance
        """
        summary = cls()
        summary.total_suggestions = len(suggestions)

        # Count by category
        for category in SuggestionCategory:
            summary.by_category[category] = sum(1 for s in suggestions if s.category == category)

        # Count by effort
        for effort in EffortLevel:
            summary.by_effort[effort] = sum(1 for s in suggestions if s.effort == effort)

        # Count by impact
        for impact in ImpactLevel:
            summary.by_impact[impact] = sum(1 for s in suggestions if s.impact == impact)

        # Count by status
        for status in SuggestionStatus:
            summary.by_status[status] = sum(1 for s in suggestions if s.status == status)

        # Special counts
        summary.quick_wins_count = sum(1 for s in suggestions if s.is_quick_win())
        summary.high_priority_count = sum(1 for s in suggestions if s.is_high_priority())
        summary.pending_count = summary.by_status.get(SuggestionStatus.PENDING, 0)
        summary.completed_count = summary.by_status.get(SuggestionStatus.COMPLETED, 0)

        return summary

# Made with Bob
