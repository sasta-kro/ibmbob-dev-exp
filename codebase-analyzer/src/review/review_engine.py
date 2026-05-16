"""
Review Engine

Main coordinator for code review process. Integrates static analysis,
AI-powered review, and finding classification to generate comprehensive
code review reports.

Made with Bob
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.finding import Finding, FindingSummary
from ..models.file_info import FileInfo
from ..models.project import Project
from ..utils.logger import get_logger
from ..utils.config import Config
from .static_analyzer import StaticAnalyzer
from .ai_reviewer import AIReviewer
from .finding_classifier import FindingClassifier

logger = get_logger(__name__)


class ReviewEngine:
    """
    Main code review engine that coordinates all review activities.
    
    Workflow:
    1. Run static analysis (pylint, bandit, patterns)
    2. Run AI-powered review (Watson)
    3. Classify and prioritize findings
    4. Generate review reports (JSON and Markdown)
    """
    
    def __init__(self, config: Config):
        """
        Initialize review engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logger
        
        # Initialize components
        self.static_analyzer = StaticAnalyzer(config)
        self.ai_reviewer = AIReviewer(config)
        self.classifier = FindingClassifier(config)
    
    def review_project(
        self,
        project: Project,
        output_dir: Optional[Path] = None,
        enable_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review on a project.
        
        Args:
            project: Project object with analyzed files
            output_dir: Directory to save review reports
            enable_ai: Whether to use AI-powered review
            
        Returns:
            Dictionary with review results and statistics
        """
        self.logger.info(f"Starting code review for project: {project.name}")
        
        # Collect all findings
        all_findings = []
        
        # Convert files dict to list
        files_list = list(project.files.values())
        
        # Run static analysis
        self.logger.info("Running static analysis...")
        static_findings = self.static_analyzer.analyze_files(files_list)
        all_findings.extend(static_findings)
        self.logger.info(f"Static analysis found {len(static_findings)} issues")
        
        # Run AI review if enabled
        if enable_ai:
            self.logger.info("Running AI-powered review...")
            ai_findings = self.ai_reviewer.review_files(files_list)
            all_findings.extend(ai_findings)
            self.logger.info(f"AI review found {len(ai_findings)} issues")
        else:
            self.logger.info("AI review disabled, skipping")
        
        # Deduplicate findings
        unique_findings = self.classifier.deduplicate_findings(all_findings)
        self.logger.info(f"After deduplication: {len(unique_findings)} unique findings")
        
        # Classify and prioritize
        classified = self.classifier.classify_findings(unique_findings)
        prioritized = self.classifier.prioritize_findings(unique_findings)
        summary = classified['summary']
        functionality_areas = self._build_functionality_areas(project, prioritized)
        
        project.findings = prioritized
        project.finding_summary = summary
        
        # Build review result
        review_result = {
            'project_name': project.name,
            'reviewed_at': datetime.now().isoformat(),
            'total_findings': len(unique_findings),
            'findings': prioritized,
            'classification': classified,
            'summary': summary.to_dict(),
            'statistics': classified['statistics'],
            'functionality_areas': functionality_areas
        }
        
        # Generate reports if output directory specified
        if output_dir:
            self._generate_reports(review_result, output_dir, project)
        
        self.logger.info(f"Code review complete: {len(unique_findings)} findings")
        return review_result
    
    def _generate_reports(
        self,
        review_result: Dict[str, Any],
        output_dir: Path,
        project: Project
    ) -> None:
        """Generate review report files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate JSON report
        json_path = output_dir / 'review-findings.json'
        self._generate_json_report(review_result, json_path)
        
        # Generate Markdown report
        md_path = output_dir / 'REVIEW_REPORT.md'
        self._generate_markdown_report(review_result, md_path, project)
        
        self.logger.info(f"Review reports generated in {output_dir}")
    
    def _generate_json_report(
        self,
        review_result: Dict[str, Any],
        output_path: Path
    ) -> None:
        """Generate JSON review report"""
        
        # Convert findings to serializable format
        findings_data = []
        for finding in review_result['findings']:
            finding_dict = finding.to_dict()
            findings_data.append(finding_dict)
        
        # Build JSON structure
        json_data = {
            'projectName': review_result['project_name'],
            'reviewedAt': review_result['reviewed_at'],
            'summary': {
                'totalFindings': review_result['total_findings'],
                'critical': review_result['summary']['critical_count'],
                'high': review_result['summary']['high_count'],
                'medium': review_result['summary']['medium_count'],
                'low': review_result['summary']['low_count'],
                'info': review_result['summary']['info_count'],
                'securityCount': review_result['summary']['security_count'],
                'filesAffected': review_result['statistics']['files_affected']
            },
            'functionalityAreas': review_result['functionality_areas'],
            'findings': findings_data,
            'statistics': review_result['statistics']
        }
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON report saved to {output_path}")
    
    def _generate_markdown_report(
        self,
        review_result: Dict[str, Any],
        output_path: Path,
        project: Project
    ) -> None:
        """Generate human-readable Markdown review report"""
        
        findings = review_result['findings']
        summary = review_result['summary']
        stats = review_result['statistics']
        classification = review_result['classification']
        
        # Build Markdown content
        lines = []
        
        # Header
        lines.append(f"# Code Review Report: {review_result['project_name']}")
        lines.append("")
        lines.append(f"**Review Date:** {review_result['reviewed_at']}")
        lines.append(f"**Total Files Analyzed:** {len(project.files)}")
        lines.append(f"**Total Findings:** {review_result['total_findings']}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        lines.append(f"| Critical | {summary['critical_count']} |")
        lines.append(f"| High | {summary['high_count']} |")
        lines.append(f"| Medium | {summary['medium_count']} |")
        lines.append(f"| Low | {summary['low_count']} |")
        lines.append(f"| Info | {summary['info_count']} |")
        lines.append("")
        
        # Statistics
        lines.append("## Statistics")
        lines.append("")
        lines.append(f"- **Files Affected:** {stats['files_affected']}")
        lines.append(f"- **Average Confidence:** {stats['average_confidence']}")
        lines.append(f"- **Actionable Findings:** {stats['actionable_count']}")
        lines.append(f"- **Security Critical:** {stats['security_critical_count']}")
        lines.append(f"- **Findings per File:** {stats['findings_per_file']}")
        lines.append("")
        
        # Critical Findings
        critical = classification['critical_findings']
        if critical:
            lines.append("## Critical Findings")
            lines.append("")
            lines.append(f"Found {len(critical)} critical issues that require immediate attention:")
            lines.append("")
            for finding in critical:
                lines.append(f"### {finding.title}")
                lines.append(f"**File:** `{finding.location.file_path}`")
                lines.append(f"**Line:** {finding.location.line_start}")
                lines.append(f"**Type:** {finding.finding_type.value}")
                lines.append(f"**Confidence:** {finding.confidence:.0%}")
                lines.append("")
                lines.append(f"**Problem:** {finding.description}")
                lines.append("")
                if finding.explanation:
                    lines.append(f"**Why It Matters:** {finding.explanation}")
                    lines.append("")
                if finding.recommendation:
                    lines.append(f"**Recommendation:** {finding.recommendation}")
                    lines.append("")
                if finding.location.code_snippet:
                    lines.append("**Code:**")
                    lines.append("```")
                    lines.append(finding.location.code_snippet)
                    lines.append("```")
                    lines.append("")
                lines.append("---")
                lines.append("")
        
        # High Priority Findings
        high_priority = classification['high_priority']
        if high_priority and len(high_priority) > len(critical):
            lines.append("## High Priority Findings")
            lines.append("")
            lines.append(f"Found {len(high_priority)} high priority issues:")
            lines.append("")
            
            # Show first 10 high priority (excluding critical already shown)
            non_critical_high = [f for f in high_priority if f not in critical][:10]
            for finding in non_critical_high:
                lines.append(f"### {finding.title}")
                lines.append(f"- **File:** `{finding.location.file_path}` (Line {finding.location.line_start})")
                lines.append(f"- **Severity:** {finding.severity.value}")
                lines.append(f"- **Type:** {finding.finding_type.value}")
                lines.append(f"- **Problem:** {finding.description}")
                if finding.recommendation:
                    lines.append(f"- **Fix:** {finding.recommendation}")
                lines.append("")
        
        # Quick Wins
        quick_wins = classification['quick_wins']
        if quick_wins:
            lines.append("## Quick Wins")
            lines.append("")
            lines.append(f"Found {len(quick_wins)} easy-to-fix issues:")
            lines.append("")
            for finding in quick_wins[:15]:  # Show first 15
                lines.append(f"- **{finding.title}** in `{finding.location.file_path}` (Line {finding.location.line_start})")
                if finding.suggested_fix:
                    lines.append(f"  - Fix: {finding.suggested_fix}")
                lines.append("")
        
        # Findings by Type
        lines.append("## Findings by Type")
        lines.append("")
        for finding_type, type_findings in classification['by_type'].items():
            lines.append(f"### {finding_type.title()}")
            lines.append(f"Count: {len(type_findings)}")
            lines.append("")
        
        # Findings by File
        lines.append("## Findings by File")
        lines.append("")
        lines.append("Files with most issues:")
        lines.append("")
        
        # Sort files by finding count
        file_counts = [(file, len(file_findings)) 
                      for file, file_findings in classification['by_file'].items()]
        file_counts.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, count in file_counts[:20]:  # Top 20 files
            lines.append(f"- `{file_path}`: {count} findings")
        lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        lines.append("### Immediate Actions")
        lines.append("")
        if summary['critical_count'] > 0:
            lines.append(f"1. Address {summary['critical_count']} critical findings immediately")
        if summary['security_count'] > 0:
            lines.append(f"2. Review and fix {summary['security_count']} security issues")
        if summary['high_count'] > 0:
            lines.append(f"3. Plan fixes for {summary['high_count']} high severity issues")
        lines.append("")
        
        lines.append("### Long-term Improvements")
        lines.append("")
        lines.append("1. Implement automated code quality checks in CI/CD")
        lines.append("2. Add pre-commit hooks for static analysis")
        lines.append("3. Schedule regular code review sessions")
        lines.append("4. Update coding standards documentation")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Codebase Analyzer - Made with Bob*")
        
        # Write Markdown file
        content = '\n'.join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Markdown report saved to {output_path}")
    
    def _build_functionality_areas(
        self,
        project: Project,
        findings: List[Finding]
    ) -> List[Dict[str, Any]]:
        """Build review output grouped by project functionality areas"""
        findings_by_file = {}
        for finding in findings:
            relative_path = self._get_relative_finding_path(project, finding)
            findings_by_file.setdefault(relative_path, []).append(finding)
        
        functionality_areas = []
        grouped_files = set()
        
        if project.functionality_map:
            for group in project.functionality_map.get_all_groups():
                related_files = [str(file_path) for file_path in group.files]
                grouped_files.update(related_files)
                group_findings = []
                
                for file_path in related_files:
                    group_findings.extend(findings_by_file.get(file_path, []))
                
                functionality_areas.append({
                    'id': group.id,
                    'name': group.name,
                    'relatedFiles': related_files,
                    'findings': [
                        finding.to_dict()
                        for finding in self.classifier.prioritize_findings(group_findings)
                    ]
                })
        
        ungrouped_findings = [
            finding
            for file_path, file_findings in findings_by_file.items()
            if file_path not in grouped_files
            for finding in file_findings
        ]
        
        if ungrouped_findings:
            functionality_areas.append({
                'id': 'ungrouped',
                'name': 'Ungrouped',
                'relatedFiles': sorted({
                    self._get_relative_finding_path(project, finding)
                    for finding in ungrouped_findings
                }),
                'findings': [
                    finding.to_dict()
                    for finding in self.classifier.prioritize_findings(ungrouped_findings)
                ]
            })
        
        return functionality_areas
    
    def _get_relative_finding_path(self, project: Project, finding: Finding) -> str:
        """Get a finding path relative to the project root when possible"""
        file_path = Path(finding.location.file_path)
        for root_path in project.root_paths:
            try:
                return str(file_path.relative_to(root_path))
            except ValueError:
                continue
        return str(file_path)
    
    def get_findings_for_file(
        self,
        findings: List[Finding],
        file_path: Path
    ) -> List[Finding]:
        """Get all findings for a specific file"""
        return [
            f for f in findings
            if f.location.file_path == file_path
        ]
    
    def get_findings_by_severity(
        self,
        findings: List[Finding],
        severity: str
    ) -> List[Finding]:
        """Get findings of a specific severity"""
        return [
            f for f in findings
            if f.severity.value == severity
        ]

# Made with Bob
