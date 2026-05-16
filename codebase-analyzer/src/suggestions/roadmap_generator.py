"""Generate improvement roadmaps from suggestions."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.suggestion import Suggestion, SuggestionSummary
from .prioritizer import Prioritizer

logger = logging.getLogger(__name__)


class RoadmapGenerator:
    """
    Generate improvement roadmaps from suggestions.
    
    Creates structured roadmaps with prioritized suggestions,
    implementation timelines, and progress tracking.
    """
    
    def __init__(self, prioritizer: Optional[Prioritizer] = None):
        """
        Initialize roadmap generator.
        
        Args:
            prioritizer: Optional prioritizer instance
        """
        self.prioritizer = prioritizer or Prioritizer()
    
    def generate_roadmap(
        self,
        suggestions: List[Suggestion],
        project_name: str,
        output_dir: Path
    ) -> Dict:
        """
        Generate improvement roadmap.
        
        Args:
            suggestions: List of suggestions
            project_name: Name of the project
            output_dir: Directory to save roadmap files
            
        Returns:
            Dictionary with roadmap data
        """
        logger.info(f"Generating roadmap for {len(suggestions)} suggestions")
        
        # Prioritize suggestions
        prioritized = self.prioritizer.prioritize_suggestions(suggestions)
        
        # Create implementation order
        ordered = self.prioritizer.create_implementation_order(prioritized)
        
        # Get categorized recommendations
        recommendations = self.prioritizer.get_recommendations(prioritized)
        
        # Calculate effort and impact
        effort_stats = self.prioritizer.calculate_total_effort(prioritized)
        impact_stats = self.prioritizer.calculate_expected_impact(prioritized)
        
        # Create summary
        summary = SuggestionSummary.from_suggestions(prioritized)
        
        # Build roadmap structure
        roadmap = {
            'projectName': project_name,
            'generatedAt': datetime.now().isoformat(),
            'summary': {
                'totalSuggestions': summary.total_suggestions,
                'quickWins': summary.quick_wins_count,
                'highPriority': summary.high_priority_count,
                'estimatedEffort': effort_stats,
                'expectedImpact': impact_stats,
            },
            'recommendations': {
                'immediate': [self._suggestion_to_dict(s) for s in recommendations['immediate']],
                'shortTerm': [self._suggestion_to_dict(s) for s in recommendations['short_term']],
                'longTerm': [self._suggestion_to_dict(s) for s in recommendations['long_term']],
            },
            'allSuggestions': [self._suggestion_to_dict(s) for s in ordered],
            'byCategory': self._group_by_category(prioritized),
            'byEffort': self._group_by_effort(prioritized),
            'byImpact': self._group_by_impact(prioritized),
        }
        
        # Save JSON roadmap
        json_path = output_dir / 'improvement-suggestions.json'
        self._save_json(roadmap, json_path)
        
        # Generate Markdown roadmap
        md_path = output_dir / 'IMPROVEMENT_ROADMAP.md'
        self._generate_markdown(roadmap, md_path)
        
        logger.info(f"Roadmap saved to {output_dir}")
        
        return roadmap
    
    def _suggestion_to_dict(self, suggestion: Suggestion) -> Dict:
        """Convert suggestion to dictionary."""
        return suggestion.to_dict()
    
    def _group_by_category(self, suggestions: List[Suggestion]) -> Dict:
        """Group suggestions by category."""
        grouped = self.prioritizer.group_by_category(suggestions)
        return {
            category.value: [self._suggestion_to_dict(s) for s in slist]
            for category, slist in grouped.items()
        }
    
    def _group_by_effort(self, suggestions: List[Suggestion]) -> Dict:
        """Group suggestions by effort."""
        grouped = self.prioritizer.group_by_effort(suggestions)
        return {
            effort.value: [self._suggestion_to_dict(s) for s in slist]
            for effort, slist in grouped.items()
        }
    
    def _group_by_impact(self, suggestions: List[Suggestion]) -> Dict:
        """Group suggestions by impact."""
        grouped = self.prioritizer.group_by_impact(suggestions)
        return {
            impact.value: [self._suggestion_to_dict(s) for s in slist]
            for impact, slist in grouped.items()
        }
    
    def _save_json(self, data: Dict, path: Path) -> None:
        """Save roadmap as JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved JSON roadmap to {path}")
    
    def _generate_markdown(self, roadmap: Dict, path: Path) -> None:
        """Generate Markdown roadmap."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self._build_markdown(roadmap))
        
        logger.info(f"Saved Markdown roadmap to {path}")
    
    def _build_markdown(self, roadmap: Dict) -> str:
        """Build Markdown content for roadmap."""
        lines = []
        
        # Header
        lines.append(f"# Improvement Roadmap: {roadmap['projectName']}")
        lines.append("")
        lines.append(f"**Generated:** {roadmap['generatedAt']}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        summary = roadmap['summary']
        lines.append(f"- **Total Suggestions:** {summary['totalSuggestions']}")
        lines.append(f"- **Quick Wins:** {summary['quickWins']}")
        lines.append(f"- **High Priority:** {summary['highPriority']}")
        lines.append("")
        
        effort = summary['estimatedEffort']
        lines.append("### Estimated Effort")
        lines.append(f"- **Total Hours:** {effort['total_hours']}")
        lines.append(f"- **Total Days:** {effort['total_days']}")
        lines.append(f"- **Total Weeks:** {effort['total_weeks']}")
        lines.append(f"- **Low Effort:** {effort['low_effort_count']} suggestions")
        lines.append(f"- **Medium Effort:** {effort['medium_effort_count']} suggestions")
        lines.append(f"- **High Effort:** {effort['high_effort_count']} suggestions")
        lines.append("")
        
        impact = summary['expectedImpact']
        lines.append("### Expected Impact")
        lines.append(f"- **High Impact:** {impact['high_impact_count']} suggestions")
        lines.append(f"- **Medium Impact:** {impact['medium_impact_count']} suggestions")
        lines.append(f"- **Low Impact:** {impact['low_impact_count']} suggestions")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        # Immediate actions
        lines.append("### Immediate Actions (Quick Wins)")
        lines.append("")
        immediate = roadmap['recommendations']['immediate']
        if immediate:
            lines.append("These are low-effort, high-impact improvements that can be implemented immediately:")
            lines.append("")
            for i, suggestion in enumerate(immediate, 1):
                lines.append(f"{i}. **{suggestion['title']}**")
                lines.append(f"   - **Category:** {suggestion['category']}")
                lines.append(f"   - **Effort:** {suggestion['effort']} | **Impact:** {suggestion['impact']}")
                lines.append(f"   - **Priority Score:** {suggestion['priority_score']:.1f}")
                lines.append(f"   - {suggestion['description']}")
                lines.append("")
        else:
            lines.append("No immediate quick wins identified.")
            lines.append("")
        
        # Short-term actions
        lines.append("### Short-Term Actions (1-2 Weeks)")
        lines.append("")
        short_term = roadmap['recommendations']['shortTerm']
        if short_term:
            lines.append("High-priority improvements that should be addressed soon:")
            lines.append("")
            for i, suggestion in enumerate(short_term, 1):
                lines.append(f"{i}. **{suggestion['title']}**")
                lines.append(f"   - **Category:** {suggestion['category']}")
                lines.append(f"   - **Effort:** {suggestion['effort']} | **Impact:** {suggestion['impact']}")
                lines.append(f"   - **Priority Score:** {suggestion['priority_score']:.1f}")
                lines.append("")
        else:
            lines.append("No short-term actions identified.")
            lines.append("")
        
        # Long-term actions
        lines.append("### Long-Term Actions (1+ Months)")
        lines.append("")
        long_term = roadmap['recommendations']['longTerm']
        if long_term:
            lines.append("Strategic improvements requiring significant effort:")
            lines.append("")
            for i, suggestion in enumerate(long_term, 1):
                lines.append(f"{i}. **{suggestion['title']}**")
                lines.append(f"   - **Category:** {suggestion['category']}")
                lines.append(f"   - **Effort:** {suggestion['effort']} | **Impact:** {suggestion['impact']}")
                lines.append(f"   - **Priority Score:** {suggestion['priority_score']:.1f}")
                lines.append("")
        else:
            lines.append("No long-term actions identified.")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Detailed Suggestions
        lines.append("## Detailed Suggestions")
        lines.append("")
        
        for i, suggestion in enumerate(roadmap['allSuggestions'], 1):
            lines.append(f"### {i}. {suggestion['title']}")
            lines.append("")
            lines.append(f"**ID:** `{suggestion['id']}`")
            lines.append(f"**Category:** {suggestion['category']}")
            lines.append(f"**Effort:** {suggestion['effort']} | **Impact:** {suggestion['impact']}")
            lines.append(f"**Priority Score:** {suggestion['priority_score']:.1f}")
            lines.append(f"**Confidence:** {suggestion['confidence']:.2f}")
            lines.append("")
            
            lines.append("#### Description")
            lines.append(suggestion['description'])
            lines.append("")
            
            lines.append("#### Rationale")
            lines.append(suggestion['rationale'])
            lines.append("")
            
            if suggestion.get('benefits'):
                lines.append("#### Benefits")
                for benefit in suggestion['benefits']:
                    lines.append(f"- {benefit}")
                lines.append("")
            
            if suggestion.get('implementation_steps'):
                lines.append("#### Implementation Steps")
                for step in suggestion['implementation_steps']:
                    lines.append(f"{step['order']}. {step['description']}")
                    if step.get('estimated_time'):
                        lines.append(f"   - Estimated time: {step['estimated_time']}")
                lines.append("")
            
            if suggestion.get('considerations'):
                lines.append("#### Considerations")
                for consideration in suggestion['considerations']:
                    lines.append(f"- {consideration}")
                lines.append("")
            
            if suggestion.get('risks'):
                lines.append("#### Risks")
                for risk in suggestion['risks']:
                    lines.append(f"- {risk}")
                lines.append("")
            
            if suggestion.get('related_files'):
                lines.append("#### Related Files")
                for file_path in suggestion['related_files']:
                    lines.append(f"- `{file_path}`")
                lines.append("")
            
            if suggestion.get('related_findings'):
                lines.append("#### Related Findings")
                for finding_id in suggestion['related_findings']:
                    lines.append(f"- `{finding_id}`")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Appendix: By Category
        lines.append("## Appendix: Suggestions by Category")
        lines.append("")
        
        for category, suggestions in roadmap['byCategory'].items():
            lines.append(f"### {category.replace('_', ' ').title()}")
            lines.append(f"**Count:** {len(suggestions)}")
            lines.append("")
            for suggestion in suggestions:
                lines.append(f"- [{suggestion['id']}] {suggestion['title']} "
                           f"(Priority: {suggestion['priority_score']:.1f})")
            lines.append("")
        
        return '\n'.join(lines)


# Made with Bob