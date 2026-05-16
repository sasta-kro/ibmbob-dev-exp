"""Generate improvement suggestions from code review findings."""

import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..models.finding import Finding, FindingType, Severity
from ..models.suggestion import (
    EffortLevel,
    ImpactLevel,
    ImplementationStep,
    Suggestion,
    SuggestionCategory,
)
from ..services.watson_service import WatsonService

logger = logging.getLogger(__name__)


class SuggestionGenerator:
    """
    Generate actionable improvement suggestions from code review findings.
    
    Analyzes findings to identify improvement opportunities, generates
    suggestions with implementation guidance, and provides rationale.
    """
    
    def __init__(self, watson_service: Optional[WatsonService] = None):
        """
        Initialize suggestion generator.
        
        Args:
            watson_service: Optional Watson AI service for enhanced suggestions
        """
        self.watson_service = watson_service
        self._suggestion_counter = 0
    
    def generate_suggestions(
        self,
        findings: List[Finding],
        use_ai: bool = False
    ) -> List[Suggestion]:
        """
        Generate improvement suggestions from findings.
        
        Args:
            findings: List of code review findings
            use_ai: Whether to use AI for enhanced suggestions
            
        Returns:
            List of generated suggestions
        """
        logger.info(f"Generating suggestions from {len(findings)} findings")
        
        suggestions = []
        
        # Group findings by file and type for pattern detection
        grouped_findings = self._group_findings(findings)
        
        # Generate suggestions from individual findings
        for finding in findings:
            if finding.is_false_positive or finding.is_resolved:
                continue
            
            suggestion = self._generate_from_finding(finding)
            if suggestion:
                suggestions.append(suggestion)
        
        # Generate suggestions from patterns
        pattern_suggestions = self._generate_from_patterns(grouped_findings)
        suggestions.extend(pattern_suggestions)
        
        # Enhance with AI if enabled
        if use_ai and self.watson_service:
            suggestions = self._enhance_with_ai(suggestions, findings)
        
        logger.info(f"Generated {len(suggestions)} suggestions")
        return suggestions
    
    def _group_findings(self, findings: List[Finding]) -> Dict:
        """
        Group findings by various dimensions for pattern detection.
        
        Args:
            findings: List of findings
            
        Returns:
            Dictionary with grouped findings
        """
        grouped = {
            'by_file': defaultdict(list),
            'by_type': defaultdict(list),
            'by_severity': defaultdict(list),
            'by_source': defaultdict(list),
        }
        
        for finding in findings:
            if finding.is_false_positive or finding.is_resolved:
                continue
            
            grouped['by_file'][str(finding.location.file_path)].append(finding)
            grouped['by_type'][finding.finding_type].append(finding)
            grouped['by_severity'][finding.severity].append(finding)
            grouped['by_source'][finding.source].append(finding)
        
        return grouped
    
    def _generate_from_finding(self, finding: Finding) -> Optional[Suggestion]:
        """
        Generate a suggestion from a single finding.
        
        Args:
            finding: Code review finding
            
        Returns:
            Suggestion or None if not applicable
        """
        # Map finding type to suggestion category
        category_map = {
            FindingType.BUG: SuggestionCategory.CODE_QUALITY,
            FindingType.SECURITY: SuggestionCategory.SECURITY,
            FindingType.PERFORMANCE: SuggestionCategory.PERFORMANCE,
            FindingType.STYLE: SuggestionCategory.CODE_QUALITY,
            FindingType.MAINTAINABILITY: SuggestionCategory.MAINTAINABILITY,
            FindingType.DOCUMENTATION: SuggestionCategory.DOCUMENTATION,
            FindingType.COMPLEXITY: SuggestionCategory.REFACTORING,
            FindingType.DUPLICATION: SuggestionCategory.REFACTORING,
            FindingType.BEST_PRACTICE: SuggestionCategory.BEST_PRACTICES,
        }
        
        category = category_map.get(finding.finding_type, SuggestionCategory.CODE_QUALITY)
        
        # Estimate effort and impact based on finding characteristics
        effort = self._estimate_effort(finding)
        impact = self._estimate_impact(finding)
        
        # Generate implementation steps
        steps = self._generate_implementation_steps(finding)
        
        # Create suggestion
        self._suggestion_counter += 1
        suggestion_id = f"SUGG-{self._suggestion_counter:04d}"
        
        # Build title
        title = finding.title or f"Fix {finding.finding_type.value} issue"
        
        # Build description
        description = finding.description
        if finding.explanation:
            description += f"\n\n{finding.explanation}"
        
        # Build rationale
        rationale = finding.message
        if finding.impact:
            rationale += f"\n\nImpact: {finding.impact}"
        
        # Build benefits
        benefits = self._generate_benefits(finding)
        
        # Build considerations
        considerations = self._generate_considerations(finding)
        
        # Build risks
        risks = self._generate_risks(finding)
        
        suggestion = Suggestion(
            id=suggestion_id,
            title=title,
            description=description,
            category=category,
            effort=effort,
            impact=impact,
            priority_score=0.0,  # Will be calculated
            related_files=[finding.location.file_path],
            related_findings=[finding.id],
            rationale=rationale,
            benefits=benefits,
            considerations=considerations,
            risks=risks,
            implementation_steps=steps,
            code_example=finding.suggested_fix,
            references=finding.references,
            source=f"Generated from {finding.source}",
            confidence=finding.confidence,
            tags=[finding.finding_type.value, finding.severity.value],
        )
        
        # Calculate priority score
        suggestion.priority_score = suggestion.calculate_priority_score()
        
        return suggestion
    
    def _generate_from_patterns(self, grouped_findings: Dict) -> List[Suggestion]:
        """
        Generate suggestions from patterns in grouped findings.
        
        Args:
            grouped_findings: Findings grouped by various dimensions
            
        Returns:
            List of pattern-based suggestions
        """
        suggestions = []
        
        # Detect files with many issues
        for file_path, file_findings in grouped_findings['by_file'].items():
            if len(file_findings) >= 5:
                suggestion = self._suggest_file_refactor(file_path, file_findings)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Detect repeated security issues
        security_findings = grouped_findings['by_type'].get(FindingType.SECURITY, [])
        if len(security_findings) >= 3:
            suggestion = self._suggest_security_audit(security_findings)
            if suggestion:
                suggestions.append(suggestion)
        
        # Detect performance patterns
        perf_findings = grouped_findings['by_type'].get(FindingType.PERFORMANCE, [])
        if len(perf_findings) >= 3:
            suggestion = self._suggest_performance_review(perf_findings)
            if suggestion:
                suggestions.append(suggestion)
        
        # Detect documentation gaps
        doc_findings = grouped_findings['by_type'].get(FindingType.DOCUMENTATION, [])
        if len(doc_findings) >= 5:
            suggestion = self._suggest_documentation_initiative(doc_findings)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_file_refactor(
        self,
        file_path: str,
        findings: List[Finding]
    ) -> Optional[Suggestion]:
        """Suggest refactoring for files with many issues."""
        self._suggestion_counter += 1
        suggestion_id = f"SUGG-{self._suggestion_counter:04d}"
        
        severity_counts = defaultdict(int)
        for finding in findings:
            severity_counts[finding.severity] += 1
        
        return Suggestion(
            id=suggestion_id,
            title=f"Refactor {Path(file_path).name} to address multiple issues",
            description=f"File has {len(findings)} findings across multiple categories. "
                       f"Consider comprehensive refactoring.",
            category=SuggestionCategory.REFACTORING,
            effort=EffortLevel.HIGH,
            impact=ImpactLevel.HIGH,
            priority_score=0.0,
            related_files=[Path(file_path)],
            related_findings=[f.id for f in findings],
            rationale=f"Multiple issues in single file indicate need for refactoring. "
                     f"Severity breakdown: {dict(severity_counts)}",
            benefits=[
                "Improved code quality across multiple dimensions",
                "Reduced technical debt",
                "Better maintainability",
                "Fewer bugs and issues",
            ],
            considerations=[
                "Requires thorough testing after refactoring",
                "May need to update dependent code",
                "Consider breaking into smaller modules",
            ],
            risks=[
                "Potential for introducing new bugs during refactoring",
                "May require significant time investment",
            ],
            implementation_steps=[
                ImplementationStep(
                    order=1,
                    description="Review all findings and create refactoring plan",
                    estimated_time="1-2 hours"
                ),
                ImplementationStep(
                    order=2,
                    description="Write comprehensive tests before refactoring",
                    estimated_time="2-3 hours"
                ),
                ImplementationStep(
                    order=3,
                    description="Refactor code incrementally, addressing findings",
                    estimated_time="4-8 hours"
                ),
                ImplementationStep(
                    order=4,
                    description="Run tests and verify all findings are resolved",
                    estimated_time="1 hour"
                ),
            ],
            estimated_time="8-14 hours",
            source="Pattern detection",
            confidence=0.85,
            tags=["refactoring", "high-priority", "multiple-issues"],
        )
    
    def _suggest_security_audit(self, findings: List[Finding]) -> Optional[Suggestion]:
        """Suggest security audit for multiple security issues."""
        self._suggestion_counter += 1
        suggestion_id = f"SUGG-{self._suggestion_counter:04d}"
        
        affected_files = set(str(f.location.file_path) for f in findings)
        
        return Suggestion(
            id=suggestion_id,
            title="Conduct comprehensive security audit",
            description=f"Found {len(findings)} security issues across {len(affected_files)} files. "
                       f"Recommend thorough security review.",
            category=SuggestionCategory.SECURITY,
            effort=EffortLevel.MEDIUM,
            impact=ImpactLevel.HIGH,
            priority_score=0.0,
            related_files=[Path(f) for f in affected_files],
            related_findings=[f.id for f in findings],
            rationale="Multiple security findings indicate potential systemic security issues",
            benefits=[
                "Improved application security",
                "Reduced vulnerability risk",
                "Better security practices",
                "Compliance with security standards",
            ],
            considerations=[
                "May require security expertise",
                "Consider using security scanning tools",
                "Review authentication and authorization",
            ],
            risks=[
                "May discover additional security issues",
                "Could require significant code changes",
            ],
            implementation_steps=[
                ImplementationStep(
                    order=1,
                    description="Review all security findings and prioritize",
                    estimated_time="2 hours"
                ),
                ImplementationStep(
                    order=2,
                    description="Run security scanning tools (bandit, safety)",
                    estimated_time="1 hour"
                ),
                ImplementationStep(
                    order=3,
                    description="Address critical security issues first",
                    estimated_time="4-6 hours"
                ),
                ImplementationStep(
                    order=4,
                    description="Implement security best practices",
                    estimated_time="2-4 hours"
                ),
            ],
            estimated_time="9-13 hours",
            tools=["bandit", "safety", "semgrep"],
            source="Pattern detection",
            confidence=0.90,
            tags=["security", "high-priority", "audit"],
        )
    
    def _suggest_performance_review(self, findings: List[Finding]) -> Optional[Suggestion]:
        """Suggest performance review for multiple performance issues."""
        self._suggestion_counter += 1
        suggestion_id = f"SUGG-{self._suggestion_counter:04d}"
        
        affected_files = set(str(f.location.file_path) for f in findings)
        
        return Suggestion(
            id=suggestion_id,
            title="Conduct performance optimization review",
            description=f"Found {len(findings)} performance issues. "
                       f"Recommend systematic performance optimization.",
            category=SuggestionCategory.PERFORMANCE,
            effort=EffortLevel.MEDIUM,
            impact=ImpactLevel.MEDIUM,
            priority_score=0.0,
            related_files=[Path(f) for f in affected_files],
            related_findings=[f.id for f in findings],
            rationale="Multiple performance findings suggest optimization opportunities",
            benefits=[
                "Improved application performance",
                "Better user experience",
                "Reduced resource usage",
                "Better scalability",
            ],
            considerations=[
                "Profile before and after optimization",
                "Focus on high-impact optimizations first",
                "Consider caching strategies",
            ],
            risks=[
                "Premature optimization can reduce readability",
                "May introduce complexity",
            ],
            implementation_steps=[
                ImplementationStep(
                    order=1,
                    description="Profile application to identify bottlenecks",
                    estimated_time="2 hours"
                ),
                ImplementationStep(
                    order=2,
                    description="Prioritize optimizations by impact",
                    estimated_time="1 hour"
                ),
                ImplementationStep(
                    order=3,
                    description="Implement optimizations incrementally",
                    estimated_time="4-6 hours"
                ),
                ImplementationStep(
                    order=4,
                    description="Measure performance improvements",
                    estimated_time="1 hour"
                ),
            ],
            estimated_time="8-10 hours",
            tools=["cProfile", "line_profiler", "memory_profiler"],
            source="Pattern detection",
            confidence=0.80,
            tags=["performance", "optimization"],
        )
    
    def _suggest_documentation_initiative(
        self,
        findings: List[Finding]
    ) -> Optional[Suggestion]:
        """Suggest documentation initiative for multiple doc issues."""
        self._suggestion_counter += 1
        suggestion_id = f"SUGG-{self._suggestion_counter:04d}"
        
        affected_files = set(str(f.location.file_path) for f in findings)
        
        return Suggestion(
            id=suggestion_id,
            title="Launch documentation improvement initiative",
            description=f"Found {len(findings)} documentation gaps. "
                       f"Recommend systematic documentation effort.",
            category=SuggestionCategory.DOCUMENTATION,
            effort=EffortLevel.MEDIUM,
            impact=ImpactLevel.MEDIUM,
            priority_score=0.0,
            related_files=[Path(f) for f in affected_files],
            related_findings=[f.id for f in findings],
            rationale="Multiple documentation gaps affect code maintainability",
            benefits=[
                "Improved code understanding",
                "Easier onboarding for new developers",
                "Better maintainability",
                "Reduced knowledge silos",
            ],
            considerations=[
                "Focus on public APIs first",
                "Use consistent documentation style",
                "Consider auto-generating docs",
            ],
            risks=[
                "Documentation can become outdated",
                "Requires ongoing maintenance",
            ],
            implementation_steps=[
                ImplementationStep(
                    order=1,
                    description="Establish documentation standards",
                    estimated_time="1 hour"
                ),
                ImplementationStep(
                    order=2,
                    description="Document public APIs and interfaces",
                    estimated_time="3-4 hours"
                ),
                ImplementationStep(
                    order=3,
                    description="Add docstrings to functions and classes",
                    estimated_time="4-6 hours"
                ),
                ImplementationStep(
                    order=4,
                    description="Generate API documentation",
                    estimated_time="1 hour"
                ),
            ],
            estimated_time="9-12 hours",
            tools=["sphinx", "mkdocs", "pydoc"],
            source="Pattern detection",
            confidence=0.75,
            tags=["documentation", "maintainability"],
        )
    
    def _estimate_effort(self, finding: Finding) -> EffortLevel:
        """
        Estimate implementation effort for a finding.
        
        Args:
            finding: Code review finding
            
        Returns:
            Estimated effort level
        """
        # Base effort on severity and type
        if finding.severity in [Severity.CRITICAL, Severity.HIGH]:
            if finding.finding_type in [FindingType.SECURITY, FindingType.BUG]:
                return EffortLevel.HIGH
            return EffortLevel.MEDIUM
        elif finding.severity == Severity.MEDIUM:
            return EffortLevel.MEDIUM
        else:
            return EffortLevel.LOW
    
    def _estimate_impact(self, finding: Finding) -> ImpactLevel:
        """
        Estimate impact of fixing a finding.
        
        Args:
            finding: Code review finding
            
        Returns:
            Estimated impact level
        """
        # Base impact on severity and type
        if finding.severity == Severity.CRITICAL:
            return ImpactLevel.HIGH
        elif finding.severity == Severity.HIGH:
            if finding.finding_type in [FindingType.SECURITY, FindingType.BUG]:
                return ImpactLevel.HIGH
            return ImpactLevel.MEDIUM
        elif finding.severity == Severity.MEDIUM:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _generate_implementation_steps(
        self,
        finding: Finding
    ) -> List[ImplementationStep]:
        """
        Generate implementation steps for a finding.
        
        Args:
            finding: Code review finding
            
        Returns:
            List of implementation steps
        """
        steps = []
        
        # Step 1: Review the issue
        steps.append(ImplementationStep(
            order=1,
            description=f"Review {finding.finding_type.value} issue in {finding.location.file_path.name}",
            estimated_time="15 minutes"
        ))
        
        # Step 2: Implement fix
        if finding.recommendation:
            steps.append(ImplementationStep(
                order=2,
                description=finding.recommendation,
                code_example=finding.suggested_fix,
                estimated_time="30 minutes"
            ))
        else:
            steps.append(ImplementationStep(
                order=2,
                description=f"Implement fix for {finding.finding_type.value} issue",
                estimated_time="30 minutes"
            ))
        
        # Step 3: Test
        steps.append(ImplementationStep(
            order=3,
            description="Test the fix and verify issue is resolved",
            estimated_time="15 minutes"
        ))
        
        return steps
    
    def _generate_benefits(self, finding: Finding) -> List[str]:
        """Generate benefits of fixing a finding."""
        benefits = []
        
        if finding.finding_type == FindingType.SECURITY:
            benefits.append("Improved security posture")
            benefits.append("Reduced vulnerability risk")
        elif finding.finding_type == FindingType.BUG:
            benefits.append("Improved reliability")
            benefits.append("Fewer runtime errors")
        elif finding.finding_type == FindingType.PERFORMANCE:
            benefits.append("Better performance")
            benefits.append("Improved user experience")
        elif finding.finding_type == FindingType.MAINTAINABILITY:
            benefits.append("Easier to maintain")
            benefits.append("Better code readability")
        
        if finding.severity in [Severity.CRITICAL, Severity.HIGH]:
            benefits.append("Addresses high-priority issue")
        
        return benefits
    
    def _generate_considerations(self, finding: Finding) -> List[str]:
        """Generate considerations for fixing a finding."""
        considerations = []
        
        considerations.append("Test thoroughly after making changes")
        
        if finding.finding_type == FindingType.SECURITY:
            considerations.append("Review security implications")
            considerations.append("Consider security best practices")
        elif finding.finding_type == FindingType.PERFORMANCE:
            considerations.append("Profile before and after changes")
            considerations.append("Avoid premature optimization")
        
        return considerations
    
    def _generate_risks(self, finding: Finding) -> List[str]:
        """Generate risks of fixing a finding."""
        risks = []
        
        if finding.severity in [Severity.CRITICAL, Severity.HIGH]:
            risks.append("Changes to critical code require careful testing")
        
        if finding.finding_type == FindingType.PERFORMANCE:
            risks.append("Optimization may reduce code readability")
        
        return risks
    
    def _enhance_with_ai(
        self,
        suggestions: List[Suggestion],
        findings: List[Finding]
    ) -> List[Suggestion]:
        """
        Enhance suggestions using AI.
        
        Args:
            suggestions: Generated suggestions
            findings: Original findings
            
        Returns:
            Enhanced suggestions
        """
        logger.info("Enhancing suggestions with AI")
        
        # For now, return suggestions as-is
        # AI enhancement can be added in future iterations
        
        return suggestions


# Made with Bob