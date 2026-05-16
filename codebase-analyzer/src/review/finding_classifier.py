"""
Finding Classifier

Classifies and prioritizes code review findings based on severity,
confidence, type, and impact.

Made with Bob
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from ..models.finding import Finding, Severity, FindingType, FindingSummary
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FindingClassifier:
    """
    Classifies and prioritizes code review findings.

    Features:
    - Severity-based classification
    - Type-based grouping
    - Priority scoring
    - Deduplication
    - Statistical analysis
    """

    def __init__(self, config: Any):
        """
        Initialize finding classifier.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logger

    def classify_findings(self, findings: List[Finding]) -> Dict[str, Any]:
        """
        Classify and organize findings.

        Args:
            findings: List of Finding objects

        Returns:
            Dictionary with classified findings and statistics
        """
        self.logger.info(f"Classifying {len(findings)} findings")

        result = {
            'total_findings': len(findings),
            'by_severity': self._group_by_severity(findings),
            'by_type': self._group_by_type(findings),
            'by_file': self._group_by_file(findings),
            'by_source': self._group_by_source(findings),
            'critical_findings': self._get_critical_findings(findings),
            'high_priority': self._get_high_priority_findings(findings),
            'quick_wins': self._identify_quick_wins(findings),
            'summary': FindingSummary.from_findings(findings),
            'statistics': self._calculate_statistics(findings)
        }

        self.logger.info(f"Classification complete: {result['summary'].total_findings} findings")
        return result

    def prioritize_findings(self, findings: List[Finding]) -> List[Finding]:
        """
        Sort findings by priority.

        Priority factors:
        - Severity (critical > high > medium > low > info)
        - Confidence (higher is more important)
        - Type (security > bug > performance > others)
        - Actionability

        Args:
            findings: List of Finding objects

        Returns:
            Sorted list of findings by priority
        """
        def priority_score(finding: Finding) -> float:
            """Calculate priority score for a finding"""
            score = 0.0

            # Severity score (0-50 points)
            severity_scores = {
                Severity.CRITICAL: 50,
                Severity.HIGH: 40,
                Severity.MEDIUM: 25,
                Severity.LOW: 10,
                Severity.INFO: 0
            }
            score += severity_scores.get(finding.severity, 0)

            # Confidence score (0-20 points)
            score += finding.confidence * 20

            # Type score (0-20 points)
            type_scores = {
                FindingType.SECURITY: 20,
                FindingType.BUG: 18,
                FindingType.PERFORMANCE: 12,
                FindingType.MAINTAINABILITY: 8,
                FindingType.COMPLEXITY: 6,
                FindingType.STYLE: 4,
                FindingType.DOCUMENTATION: 2,
                FindingType.DUPLICATION: 5,
                FindingType.BEST_PRACTICE: 7
            }
            score += type_scores.get(finding.finding_type, 0)

            # Actionability bonus (0-10 points)
            if finding.recommendation:
                score += 5
            if finding.suggested_fix:
                score += 5

            return score

        return sorted(findings, key=priority_score, reverse=True)

    def deduplicate_findings(self, findings: List[Finding]) -> List[Finding]:
        """
        Remove duplicate findings.

        Considers findings duplicate if they have:
        - Same file
        - Same line range
        - Same finding type
        - Similar title

        Args:
            findings: List of Finding objects

        Returns:
            Deduplicated list of findings
        """
        seen = {}
        unique = []

        for finding in findings:
            # Create key for deduplication
            key = (
                str(finding.location.file_path),
                finding.location.line_start,
                finding.location.line_end,
                finding.finding_type,
                finding.title.lower()[:50]  # First 50 chars of title
            )

            if key not in seen:
                seen[key] = finding
                unique.append(finding)
            else:
                # Keep the one with higher confidence
                existing = seen[key]
                if finding.confidence > existing.confidence:
                    unique.remove(existing)
                    unique.append(finding)
                    seen[key] = finding

        removed = len(findings) - len(unique)
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate findings")

        return unique

    def _group_by_severity(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by severity level"""
        groups = defaultdict(list)
        for finding in findings:
            groups[finding.severity.value].append(finding)
        return dict(groups)

    def _group_by_type(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by type"""
        groups = defaultdict(list)
        for finding in findings:
            groups[finding.finding_type.value].append(finding)
        return dict(groups)

    def _group_by_file(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by file"""
        groups = defaultdict(list)
        for finding in findings:
            file_path = str(finding.location.file_path)
            groups[file_path].append(finding)
        return dict(groups)

    def _group_by_source(self, findings: List[Finding]) -> Dict[str, List[Finding]]:
        """Group findings by source tool"""
        groups = defaultdict(list)
        for finding in findings:
            groups[finding.source].append(finding)
        return dict(groups)

    def _get_critical_findings(self, findings: List[Finding]) -> List[Finding]:
        """Get all critical severity findings"""
        return [f for f in findings if f.severity == Severity.CRITICAL]

    def _get_high_priority_findings(self, findings: List[Finding]) -> List[Finding]:
        """
        Get high priority findings.

        Includes:
        - Critical severity
        - High severity with high confidence
        - Security issues
        """
        high_priority = []
        for finding in findings:
            if finding.severity == Severity.CRITICAL:
                high_priority.append(finding)
            elif finding.severity == Severity.HIGH and finding.confidence >= 0.7:
                high_priority.append(finding)
            elif finding.finding_type == FindingType.SECURITY and finding.severity in [Severity.HIGH, Severity.MEDIUM]:
                high_priority.append(finding)

        return high_priority

    def _identify_quick_wins(self, findings: List[Finding]) -> List[Finding]:
        """
        Identify quick win findings.

        Quick wins are:
        - Low to medium severity
        - High confidence
        - Have clear fix suggestions
        - Style or documentation issues
        """
        quick_wins = []
        for finding in findings:
            is_low_severity = finding.severity in [Severity.LOW, Severity.MEDIUM]
            has_fix = finding.suggested_fix is not None
            high_confidence = finding.confidence >= 0.8
            easy_type = finding.finding_type in [
                FindingType.STYLE,
                FindingType.DOCUMENTATION,
                FindingType.BEST_PRACTICE
            ]

            if is_low_severity and has_fix and (high_confidence or easy_type):
                quick_wins.append(finding)

        return quick_wins

    def _calculate_statistics(self, findings: List[Finding]) -> Dict[str, Any]:
        """Calculate statistical information about findings"""
        if not findings:
            return {
                'total': 0,
                'average_confidence': 0.0,
                'severity_distribution': {},
                'type_distribution': {},
                'files_affected': 0,
                'actionable_count': 0,
                'security_critical_count': 0
            }

        # Count files affected
        files_affected = len(set(str(f.location.file_path) for f in findings))

        # Calculate average confidence
        avg_confidence = sum(f.confidence for f in findings) / len(findings)

        # Severity distribution
        severity_dist = {}
        for severity in Severity:
            count = sum(1 for f in findings if f.severity == severity)
            if count > 0:
                severity_dist[severity.value] = count

        # Type distribution
        type_dist = {}
        for finding_type in FindingType:
            count = sum(1 for f in findings if f.finding_type == finding_type)
            if count > 0:
                type_dist[finding_type.value] = count

        # Actionable findings (have recommendations)
        actionable = sum(1 for f in findings if f.recommendation)

        # Security critical (security + high/critical severity)
        security_critical = sum(
            1 for f in findings
            if f.finding_type == FindingType.SECURITY
            and f.severity in [Severity.CRITICAL, Severity.HIGH]
        )

        return {
            'total': len(findings),
            'average_confidence': round(avg_confidence, 2),
            'severity_distribution': severity_dist,
            'type_distribution': type_dist,
            'files_affected': files_affected,
            'actionable_count': actionable,
            'security_critical_count': security_critical,
            'findings_per_file': round(len(findings) / files_affected, 2) if files_affected > 0 else 0
        }

    def filter_findings(
        self,
        findings: List[Finding],
        min_severity: Optional[Severity] = None,
        finding_types: Optional[List[FindingType]] = None,
        min_confidence: Optional[float] = None,
        exclude_resolved: bool = True,
        exclude_false_positives: bool = True
    ) -> List[Finding]:
        """
        Filter findings based on criteria.

        Args:
            findings: List of findings to filter
            min_severity: Minimum severity level
            finding_types: List of finding types to include
            min_confidence: Minimum confidence score
            exclude_resolved: Exclude resolved findings
            exclude_false_positives: Exclude false positives

        Returns:
            Filtered list of findings
        """
        filtered = findings

        # Filter by severity
        if min_severity:
            severity_order = [
                Severity.INFO,
                Severity.LOW,
                Severity.MEDIUM,
                Severity.HIGH,
                Severity.CRITICAL
            ]
            min_index = severity_order.index(min_severity)
            filtered = [
                f for f in filtered
                if severity_order.index(f.severity) >= min_index
            ]

        # Filter by type
        if finding_types:
            filtered = [f for f in filtered if f.finding_type in finding_types]

        # Filter by confidence
        if min_confidence is not None:
            filtered = [f for f in filtered if f.confidence >= min_confidence]

        # Filter resolved
        if exclude_resolved:
            filtered = [f for f in filtered if not f.is_resolved]

        # Filter false positives
        if exclude_false_positives:
            filtered = [f for f in filtered if not f.is_false_positive]

        return filtered

# Made with Bob