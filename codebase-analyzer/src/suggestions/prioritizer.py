"""Prioritize and filter improvement suggestions."""

import logging
from typing import Dict, List, Union

from ..models.suggestion import (
    EffortLevel,
    ImpactLevel,
    Suggestion,
    SuggestionCategory,
)

logger = logging.getLogger(__name__)


class Prioritizer:
    """
    Prioritize and filter improvement suggestions.

    Provides methods to sort, filter, and group suggestions based on
    various criteria like priority, effort, impact, and category.
    """

    def prioritize_suggestions(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Prioritize suggestions by score.

        Args:
            suggestions: List of suggestions

        Returns:
            Sorted list of suggestions (highest priority first)
        """
        logger.info(f"Prioritizing {len(suggestions)} suggestions")

        # Recalculate priority scores
        for suggestion in suggestions:
            suggestion.priority_score = suggestion.calculate_priority_score()

        # Sort by priority score (descending)
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (s.priority_score, s.confidence),
            reverse=True
        )

        return sorted_suggestions

    def get_quick_wins(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Get quick win suggestions (low effort, high impact).

        Args:
            suggestions: List of suggestions

        Returns:
            List of quick win suggestions
        """
        quick_wins = [s for s in suggestions if s.is_quick_win()]
        logger.info(f"Found {len(quick_wins)} quick wins")
        return quick_wins

    def get_high_priority(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """
        Get high priority suggestions (score >= 70).

        Args:
            suggestions: List of suggestions

        Returns:
            List of high priority suggestions
        """
        high_priority = [s for s in suggestions if s.is_high_priority()]
        logger.info(f"Found {len(high_priority)} high priority suggestions")
        return high_priority

    def filter_by_effort(
        self,
        suggestions: List[Suggestion],
        effort_levels: List[EffortLevel]
    ) -> List[Suggestion]:
        """
        Filter suggestions by effort level.

        Args:
            suggestions: List of suggestions
            effort_levels: Effort levels to include

        Returns:
            Filtered list of suggestions
        """
        filtered = [s for s in suggestions if s.effort in effort_levels]
        logger.info(f"Filtered to {len(filtered)} suggestions by effort")
        return filtered

    def filter_by_impact(
        self,
        suggestions: List[Suggestion],
        impact_levels: List[ImpactLevel]
    ) -> List[Suggestion]:
        """
        Filter suggestions by impact level.

        Args:
            suggestions: List of suggestions
            impact_levels: Impact levels to include

        Returns:
            Filtered list of suggestions
        """
        filtered = [s for s in suggestions if s.impact in impact_levels]
        logger.info(f"Filtered to {len(filtered)} suggestions by impact")
        return filtered

    def filter_by_category(
        self,
        suggestions: List[Suggestion],
        categories: List[SuggestionCategory]
    ) -> List[Suggestion]:
        """
        Filter suggestions by category.

        Args:
            suggestions: List of suggestions
            categories: Categories to include

        Returns:
            Filtered list of suggestions
        """
        filtered = [s for s in suggestions if s.category in categories]
        logger.info(f"Filtered to {len(filtered)} suggestions by category")
        return filtered

    def group_by_category(
        self,
        suggestions: List[Suggestion]
    ) -> Dict[SuggestionCategory, List[Suggestion]]:
        """
        Group suggestions by category.

        Args:
            suggestions: List of suggestions

        Returns:
            Dictionary mapping categories to suggestions
        """
        grouped = {}
        for category in SuggestionCategory:
            category_suggestions = [s for s in suggestions if s.category == category]
            if category_suggestions:
                grouped[category] = category_suggestions

        logger.info(f"Grouped suggestions into {len(grouped)} categories")
        return grouped

    def group_by_effort(
        self,
        suggestions: List[Suggestion]
    ) -> Dict[EffortLevel, List[Suggestion]]:
        """
        Group suggestions by effort level.

        Args:
            suggestions: List of suggestions

        Returns:
            Dictionary mapping effort levels to suggestions
        """
        grouped = {}
        for effort in EffortLevel:
            effort_suggestions = [s for s in suggestions if s.effort == effort]
            if effort_suggestions:
                grouped[effort] = effort_suggestions

        logger.info(f"Grouped suggestions into {len(grouped)} effort levels")
        return grouped

    def group_by_impact(
        self,
        suggestions: List[Suggestion]
    ) -> Dict[ImpactLevel, List[Suggestion]]:
        """
        Group suggestions by impact level.

        Args:
            suggestions: List of suggestions

        Returns:
            Dictionary mapping impact levels to suggestions
        """
        grouped = {}
        for impact in ImpactLevel:
            impact_suggestions = [s for s in suggestions if s.impact == impact]
            if impact_suggestions:
                grouped[impact] = impact_suggestions

        logger.info(f"Grouped suggestions into {len(grouped)} impact levels")
        return grouped

    def create_implementation_order(
        self,
        suggestions: List[Suggestion]
    ) -> List[Suggestion]:
        """
        Create recommended implementation order.

        Prioritizes:
        1. Quick wins (low effort, high impact)
        2. High priority suggestions
        3. Security-related suggestions
        4. Other suggestions by priority score

        Args:
            suggestions: List of suggestions

        Returns:
            Ordered list of suggestions
        """
        logger.info("Creating implementation order")

        # Separate into categories
        quick_wins = self.get_quick_wins(suggestions)
        security = [
            s for s in suggestions
            if s.category == SuggestionCategory.SECURITY
            and s not in quick_wins
        ]
        high_priority = [
            s for s in suggestions
            if s.is_high_priority()
            and s not in quick_wins
            and s not in security
        ]
        remaining = [
            s for s in suggestions
            if s not in quick_wins
            and s not in security
            and s not in high_priority
        ]

        # Sort each category by priority score
        quick_wins.sort(key=lambda s: s.priority_score, reverse=True)
        security.sort(key=lambda s: s.priority_score, reverse=True)
        high_priority.sort(key=lambda s: s.priority_score, reverse=True)
        remaining.sort(key=lambda s: s.priority_score, reverse=True)

        # Combine in order
        ordered = quick_wins + security + high_priority + remaining

        logger.info(
            f"Implementation order: {len(quick_wins)} quick wins, "
            f"{len(security)} security, {len(high_priority)} high priority, "
            f"{len(remaining)} remaining"
        )

        return ordered

    def calculate_total_effort(self, suggestions: List[Suggestion]) -> Dict[str, Union[int, float]]:
        """
        Calculate total effort for suggestions.

        Args:
            suggestions: List of suggestions

        Returns:
            Dictionary with effort statistics
        """
        effort_hours = {
            EffortLevel.LOW: 2,      # 2 hours average
            EffortLevel.MEDIUM: 6,   # 6 hours average
            EffortLevel.HIGH: 16,    # 16 hours average (2 days)
        }

        total_hours = sum(effort_hours.get(s.effort, 0) for s in suggestions)

        return {
            'total_hours': total_hours,
            'total_days': round(total_hours / 8, 1),
            'total_weeks': round(total_hours / 40, 1),
            'low_effort_count': sum(1 for s in suggestions if s.effort == EffortLevel.LOW),
            'medium_effort_count': sum(1 for s in suggestions if s.effort == EffortLevel.MEDIUM),
            'high_effort_count': sum(1 for s in suggestions if s.effort == EffortLevel.HIGH),
        }

    def calculate_expected_impact(self, suggestions: List[Suggestion]) -> Dict[str, int]:
        """
        Calculate expected impact of suggestions.

        Args:
            suggestions: List of suggestions

        Returns:
            Dictionary with impact statistics
        """
        return {
            'high_impact_count': sum(1 for s in suggestions if s.impact == ImpactLevel.HIGH),
            'medium_impact_count': sum(1 for s in suggestions if s.impact == ImpactLevel.MEDIUM),
            'low_impact_count': sum(1 for s in suggestions if s.impact == ImpactLevel.LOW),
            'quick_wins_count': len(self.get_quick_wins(suggestions)),
            'high_priority_count': len(self.get_high_priority(suggestions)),
        }

    def get_recommendations(self, suggestions: List[Suggestion]) -> Dict[str, List[Suggestion]]:
        """
        Get categorized recommendations.

        Args:
            suggestions: List of suggestions

        Returns:
            Dictionary with categorized recommendations
        """
        return {
            'immediate': self.get_quick_wins(suggestions)[:5],  # Top 5 quick wins
            'short_term': [
                s for s in suggestions
                if s.effort in [EffortLevel.LOW, EffortLevel.MEDIUM]
                and s.is_high_priority()
            ][:10],  # Top 10 short-term
            'long_term': [
                s for s in suggestions
                if s.effort == EffortLevel.HIGH
                and s.impact == ImpactLevel.HIGH
            ][:5],  # Top 5 long-term
        }


# Made with Bob