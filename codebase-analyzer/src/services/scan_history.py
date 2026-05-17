"""Scan History Service - Persist and retrieve past scan results."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..models.project import Project
from ..utils.logger import get_logger

logger = get_logger(__name__)

HISTORY_DIR = Path.home() / ".codebase-analyzer" / "history"
INDEX_FILE = HISTORY_DIR / "index.json"


class ScanHistoryService:
    """Manages persistent storage of scan results."""

    def __init__(self, history_dir: Optional[Path] = None):
        self.history_dir = history_dir or HISTORY_DIR
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.history_dir / "index.json"
        self._index = self._load_index()

    def _load_index(self) -> List[dict]:
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                logger.warning("Corrupted history index, starting fresh")
        return []

    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self._index, f, indent=2)

    def save_scan(self, project: Project) -> None:
        """Save a completed scan to history."""
        scan_file = self.history_dir / f"{project.id}.json"
        project.save_to_file(scan_file)

        entry = {
            "id": project.id,
            "name": project.name,
            "path": str(project.root_paths[0]) if project.root_paths else "",
            "file_count": project.get_file_count(),
            "findings_count": project.get_total_findings(),
            "suggestions_count": project.get_total_suggestions(),
            "last_analyzed": datetime.now().isoformat(),
        }

        self._index = [e for e in self._index if e["id"] != project.id]
        self._index.insert(0, entry)
        self._index = self._index[:20]
        self._save_index()
        logger.info("Saved scan history for %s", project.name)

    def list_scans(self) -> List[dict]:
        """Return recent scan summaries (newest first)."""
        return list(self._index)

    def load_scan(self, project_id: str) -> Optional[Project]:
        """Load a full project from history."""
        scan_file = self.history_dir / f"{project_id}.json"
        if not scan_file.exists():
            logger.warning("Scan file not found: %s", scan_file)
            return None
        try:
            return Project.load_from_file(scan_file)
        except Exception as e:
            logger.error("Failed to load scan %s: %s", project_id, e)
            return None

    def delete_scan(self, project_id: str) -> None:
        """Remove a scan from history."""
        scan_file = self.history_dir / f"{project_id}.json"
        if scan_file.exists():
            scan_file.unlink()
        self._index = [e for e in self._index if e["id"] != project_id]
        self._save_index()
