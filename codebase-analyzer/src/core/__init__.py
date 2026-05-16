"""
Core analysis engines for the codebase analyzer.

This package contains the main engines for scanning, analyzing, and grouping code.
"""

from .scanner import Scanner, ScanResult
from .analyzer import AnalyzerEngine
from .grouper import FunctionalityGrouper
from .orchestrator import AnalysisOrchestrator

__all__ = [
    'Scanner',
    'ScanResult',
    'AnalyzerEngine',
    'FunctionalityGrouper',
    'AnalysisOrchestrator',
]

# Made with Bob
