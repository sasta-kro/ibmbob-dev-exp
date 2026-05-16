"""Functionality group data model."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FunctionalityGroup(BaseModel):
    """Represents a group of related files by functionality."""

    # Identification
    id: str = Field(..., description="Unique group identifier")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")

    # Files
    files: List[Path] = Field(default_factory=list, description="Files in this group")
    primary_files: List[Path] = Field(default_factory=list, description="Main/entry files")

    # Categorization
    category: Optional[str] = Field(None, description="Category (e.g., 'API', 'UI', 'Database')")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")

    # Relationships
    dependencies: List[str] = Field(default_factory=list, description="Other group IDs this depends on")
    dependents: List[str] = Field(default_factory=list, description="Other group IDs that depend on this")

    # Metrics
    total_files: int = Field(default=0, description="Total number of files")
    total_lines: int = Field(default=0, description="Total lines of code")
    complexity_score: float = Field(default=0.0, description="Average complexity")

    # Analysis
    purpose: Optional[str] = Field(None, description="AI-detected purpose")
    key_features: List[str] = Field(default_factory=list, description="Key features/capabilities")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    patterns: List[str] = Field(default_factory=list, description="Design patterns detected")

    # Documentation
    documentation_path: Optional[Path] = Field(None, description="Path to generated documentation")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    analyzed_at: Optional[datetime] = Field(None, description="Last analysis timestamp")

    model_config = ConfigDict(json_encoders={Path: str, datetime: lambda v: v.isoformat()})

    def add_file(self, file_path: Path) -> None:
        """Add a file to this group."""
        if file_path not in self.files:
            self.files.append(file_path)
            self.total_files = len(self.files)

    def remove_file(self, file_path: Path) -> None:
        """Remove a file from this group."""
        if file_path in self.files:
            self.files.remove(file_path)
            self.total_files = len(self.files)

    def add_dependency(self, group_id: str) -> None:
        """Add a dependency on another group."""
        if group_id not in self.dependencies:
            self.dependencies.append(group_id)

    def add_dependent(self, group_id: str) -> None:
        """Add a group that depends on this one."""
        if group_id not in self.dependents:
            self.dependents.append(group_id)

    def get_file_count(self) -> int:
        """Get number of files in group."""
        return len(self.files)

    def has_dependencies(self) -> bool:
        """Check if group has dependencies."""
        return len(self.dependencies) > 0

    def has_dependents(self) -> bool:
        """Check if other groups depend on this."""
        return len(self.dependents) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')


class FunctionalityMap(BaseModel):
    """Map of all functionality groups in a project."""

    groups: Dict[str, FunctionalityGroup] = Field(
        default_factory=dict,
        description="Map of group ID to FunctionalityGroup"
    )
    total_groups: int = Field(default=0, description="Total number of groups")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    def add_group(self, group: FunctionalityGroup) -> None:
        """Add a functionality group."""
        self.groups[group.id] = group
        self.total_groups = len(self.groups)

    def get_group(self, group_id: str) -> Optional[FunctionalityGroup]:
        """Get a group by ID."""
        return self.groups.get(group_id)

    def remove_group(self, group_id: str) -> None:
        """Remove a group by ID."""
        if group_id in self.groups:
            del self.groups[group_id]
            self.total_groups = len(self.groups)

    def get_all_groups(self) -> List[FunctionalityGroup]:
        """Get all groups as a list."""
        return list(self.groups.values())

    def get_groups_by_category(self, category: str) -> List[FunctionalityGroup]:
        """Get all groups in a specific category."""
        return [g for g in self.groups.values() if g.category == category]

    def get_root_groups(self) -> List[FunctionalityGroup]:
        """Get groups with no dependencies (root nodes)."""
        return [g for g in self.groups.values() if not g.has_dependencies()]

    def get_leaf_groups(self) -> List[FunctionalityGroup]:
        """Get groups with no dependents (leaf nodes)."""
        return [g for g in self.groups.values() if not g.has_dependents()]

    def find_file(self, file_path: Path) -> Optional[FunctionalityGroup]:
        """Find which group contains a specific file."""
        for group in self.groups.values():
            if file_path in group.files:
                return group
        return None

    def get_dependency_chain(self, group_id: str) -> List[str]:
        """Get the full dependency chain for a group."""
        chain = []
        visited = set()

        def traverse(gid: str):
            if gid in visited:
                return
            visited.add(gid)
            group = self.get_group(gid)
            if group:
                for dep_id in group.dependencies:
                    traverse(dep_id)
                chain.append(gid)

        traverse(group_id)
        return chain

    def to_dict(self) -> dict:
        """Convert to dictionary with proper serialization."""
        return self.model_dump(mode='json')

# Made with Bob
