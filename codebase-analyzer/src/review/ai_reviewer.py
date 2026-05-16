"""
AI-Powered Code Reviewer

Uses IBM Watson AI to perform deep code analysis, detecting logic errors,
security vulnerabilities, and suggesting improvements.

Made with Bob
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from ..models.finding import Finding, Severity, FindingType, CodeLocation
from ..models.file_info import FileInfo
from ..services.watson_service import WatsonService
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class AIReviewer:
    """
    AI-powered code reviewer using IBM Watson.
    
    Performs deep semantic analysis to detect:
    - Logic errors
    - Security vulnerabilities
    - Performance issues
    - Design problems
    - Best practice violations
    """
    
    def __init__(self, config: Config, watson_service: Optional[WatsonService] = None):
        """
        Initialize AI reviewer.
        
        Args:
            config: Configuration object
            watson_service: Optional Watson service instance (creates new if None)
        """
        self.config = config
        self.watson = watson_service or WatsonService(config)
        self.logger = logger
        self.max_files_for_ai = config.get('ai.max_files', 50)
    
    def review_files(self, files: List[FileInfo]) -> List[Finding]:
        """
        Review files using AI analysis.
        
        Args:
            files: List of FileInfo objects to review
            
        Returns:
            List of Finding objects from AI analysis
        """
        if not self.watson.is_available():
            self.logger.warning("Watson AI not available, skipping AI review")
            return []
        
        self.logger.info(f"Starting AI review on {len(files)} files")
        
        # Select important files for AI review
        selected_files = self._select_files_for_review(files)
        self.logger.info(f"Selected {len(selected_files)} files for AI review")
        
        all_findings = []
        
        for file_info in selected_files:
            try:
                findings = self._review_file(file_info)
                all_findings.extend(findings)
            except Exception as e:
                self.logger.error(f"AI review error on {file_info.path}: {e}")
        
        self.logger.info(f"AI review complete: {len(all_findings)} findings")
        return all_findings
    
    def _select_files_for_review(self, files: List[FileInfo]) -> List[FileInfo]:
        """
        Select most important files for AI review to manage costs.
        
        Prioritizes:
        - High complexity files
        - Large files
        - Entry points
        - Core business logic
        """
        if len(files) <= self.max_files_for_ai:
            return files
        
        # Score files by importance
        scored_files = []
        for file_info in files:
            score = 0
            
            # Complexity score
            complexity = file_info.metrics.complexity
            if complexity > 20:
                score += 50
            elif complexity > 10:
                score += 30
            elif complexity > 5:
                score += 10
            
            # Size score
            loc = file_info.metrics.lines_of_code
            if loc > 500:
                score += 30
            elif loc > 200:
                score += 20
            elif loc > 100:
                score += 10
            
            # Entry point detection
            if any(keyword in str(file_info.path).lower() 
                   for keyword in ['main', 'app', 'server', 'index', 'init']):
                score += 40
            
            # Core functionality
            if any(keyword in str(file_info.path).lower()
                   for keyword in ['auth', 'security', 'payment', 'api', 'database']):
                score += 35
            
            scored_files.append((score, file_info))
        
        # Sort by score and take top files
        scored_files.sort(key=lambda x: x[0], reverse=True)
        return [f[1] for f in scored_files[:self.max_files_for_ai]]
    
    def _review_file(self, file_info: FileInfo) -> List[Finding]:
        """Review a single file using AI"""
        findings = []
        
        # Read file content
        content = self._read_file_content(file_info.path)
        if not content:
            return findings
        
        # Perform different types of AI analysis
        findings.extend(self._detect_bugs(file_info, content))
        findings.extend(self._detect_security_issues(file_info, content))
        findings.extend(self._detect_performance_issues(file_info, content))
        findings.extend(self._detect_design_issues(file_info, content))
        
        return findings
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Could not read {file_path}: {e}")
            return None
    
    def _detect_bugs(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Use AI to detect logic errors and bugs"""
        prompt = self._build_bug_detection_prompt(file_info, content)
        
        try:
            response = self.watson.analyze_code(
                code=content,
                file_path=str(file_info.path),
                analysis_type='bug_detection'
            )
            
            return self._parse_ai_findings(
                response,
                file_info,
                FindingType.BUG,
                'ai-bug-detector'
            )
        except Exception as e:
            self.logger.warning(f"AI bug detection failed for {file_info.path}: {e}")
            return []
    
    def _detect_security_issues(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Use AI to detect security vulnerabilities"""
        prompt = self._build_security_prompt(file_info, content)
        
        try:
            response = self.watson.analyze_code(
                code=content,
                file_path=str(file_info.path),
                analysis_type='security_analysis'
            )
            
            return self._parse_ai_findings(
                response,
                file_info,
                FindingType.SECURITY,
                'ai-security-analyzer'
            )
        except Exception as e:
            self.logger.warning(f"AI security analysis failed for {file_info.path}: {e}")
            return []
    
    def _detect_performance_issues(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Use AI to detect performance problems"""
        prompt = self._build_performance_prompt(file_info, content)
        
        try:
            response = self.watson.analyze_code(
                code=content,
                file_path=str(file_info.path),
                analysis_type='performance_analysis'
            )
            
            return self._parse_ai_findings(
                response,
                file_info,
                FindingType.PERFORMANCE,
                'ai-performance-analyzer'
            )
        except Exception as e:
            self.logger.warning(f"AI performance analysis failed for {file_info.path}: {e}")
            return []
    
    def _detect_design_issues(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Use AI to detect design and architecture issues"""
        prompt = self._build_design_prompt(file_info, content)
        
        try:
            response = self.watson.analyze_code(
                code=content,
                file_path=str(file_info.path),
                analysis_type='design_analysis'
            )
            
            return self._parse_ai_findings(
                response,
                file_info,
                FindingType.MAINTAINABILITY,
                'ai-design-analyzer'
            )
        except Exception as e:
            self.logger.warning(f"AI design analysis failed for {file_info.path}: {e}")
            return []
    
    def _build_bug_detection_prompt(self, file_info: FileInfo, content: str) -> str:
        """Build prompt for bug detection"""
        return f"""Analyze this code for potential bugs and logic errors:

File: {file_info.path}
Language: {file_info.file_type}

Code:
```
{content[:2000]}  # Limit to first 2000 chars
```

Identify:
1. Logic errors (incorrect conditionals, off-by-one errors, etc.)
2. Null/None pointer risks
3. Type mismatches
4. Incorrect async/await usage
5. Race conditions
6. Resource leaks

For each issue found, provide:
- Line number
- Issue description
- Why it matters
- How to fix it
- Severity (critical/high/medium/low)
"""
    
    def _build_security_prompt(self, file_info: FileInfo, content: str) -> str:
        """Build prompt for security analysis"""
        return f"""Analyze this code for security vulnerabilities:

File: {file_info.path}
Language: {file_info.file_type}

Code:
```
{content[:2000]}
```

Identify:
1. SQL injection risks
2. XSS vulnerabilities
3. Authentication/authorization issues
4. Insecure data handling
5. Cryptographic weaknesses
6. Input validation problems
7. Sensitive data exposure

For each vulnerability, provide:
- Line number
- Vulnerability type
- Exploitation scenario
- Impact
- Remediation steps
- Severity (critical/high/medium/low)
"""
    
    def _build_performance_prompt(self, file_info: FileInfo, content: str) -> str:
        """Build prompt for performance analysis"""
        return f"""Analyze this code for performance issues:

File: {file_info.path}
Language: {file_info.file_type}

Code:
```
{content[:2000]}
```

Identify:
1. N+1 query patterns
2. Inefficient algorithms
3. Unnecessary loops or iterations
4. Missing caching opportunities
5. Memory leaks
6. Blocking operations
7. Redundant computations

For each issue, provide:
- Line number
- Performance problem
- Impact on scalability
- Optimization suggestion
- Severity (high/medium/low)
"""
    
    def _build_design_prompt(self, file_info: FileInfo, content: str) -> str:
        """Build prompt for design analysis"""
        return f"""Analyze this code for design and maintainability issues:

File: {file_info.path}
Language: {file_info.file_type}

Code:
```
{content[:2000]}
```

Identify:
1. Violation of SOLID principles
2. Code duplication
3. God classes/functions
4. Tight coupling
5. Missing abstractions
6. Poor naming
7. Lack of error handling

For each issue, provide:
- Line number or section
- Design problem
- Impact on maintainability
- Refactoring suggestion
- Severity (medium/low)
"""
    
    def _parse_ai_findings(
        self,
        ai_response: Dict[str, Any],
        file_info: FileInfo,
        finding_type: FindingType,
        source: str
    ) -> List[Finding]:
        """
        Parse AI response into Finding objects.
        
        Expected AI response format:
        {
            "findings": [
                {
                    "line": 42,
                    "title": "Potential SQL injection",
                    "description": "...",
                    "severity": "high",
                    "explanation": "...",
                    "recommendation": "..."
                }
            ]
        }
        """
        findings = []
        
        # Handle different response formats
        findings_data = []
        if isinstance(ai_response, dict):
            findings_data = ai_response.get('findings', [])
            if not findings_data and 'issues' in ai_response:
                findings_data = ai_response.get('issues', [])
        elif isinstance(ai_response, list):
            findings_data = ai_response
        
        for item in findings_data:
            try:
                finding = self._create_finding_from_ai_data(
                    item,
                    file_info,
                    finding_type,
                    source
                )
                if finding:
                    findings.append(finding)
            except Exception as e:
                self.logger.warning(f"Failed to parse AI finding: {e}")
        
        return findings
    
    def _create_finding_from_ai_data(
        self,
        data: Dict[str, Any],
        file_info: FileInfo,
        finding_type: FindingType,
        source: str
    ) -> Optional[Finding]:
        """Create Finding object from AI response data"""
        
        # Extract line number
        line_num = data.get('line', data.get('line_number', 1))
        
        # Extract severity
        severity_str = data.get('severity', 'medium').lower()
        severity_map = {
            'critical': Severity.CRITICAL,
            'high': Severity.HIGH,
            'medium': Severity.MEDIUM,
            'low': Severity.LOW,
            'info': Severity.INFO
        }
        severity = severity_map.get(severity_str, Severity.MEDIUM)
        
        # Extract confidence
        confidence = data.get('confidence', 0.8)
        if isinstance(confidence, str):
            confidence_map = {'high': 0.9, 'medium': 0.7, 'low': 0.5}
            confidence = confidence_map.get(confidence.lower(), 0.7)
        
        # Read file content for snippet
        content = self._read_file_content(file_info.path)
        code_snippet = self._extract_code_snippet(content, line_num) if content else ""
        
        # Create location
        location = CodeLocation(
            file_path=file_info.path,
            line_start=line_num,
            line_end=data.get('line_end', line_num),
            code_snippet=code_snippet
        )
        
        # Create finding
        finding = Finding(
            id=f"AI-{source}-{file_info.relative_path}-{line_num}",
            title=data.get('title', 'AI-detected issue'),
            description=data.get('description', data.get('message', '')),
            severity=severity,
            finding_type=finding_type,
            confidence=confidence,
            location=location,
            message=data.get('description', data.get('message', '')),
            explanation=data.get('explanation', data.get('why_it_matters', None)),
            impact=data.get('impact', None),
            recommendation=data.get('recommendation', data.get('fix', None)),
            suggested_fix=data.get('suggested_fix', data.get('fix', None)),
            source=source,
            rule_id=data.get('rule_id', None),
            tags=['ai-powered', finding_type.value]
        )
        
        return finding
    
    def _extract_code_snippet(self, content: str, line_num: int, context_lines: int = 2) -> str:
        """Extract code snippet with context"""
        if not content:
            return ""
        
        lines = content.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        return '\n'.join(lines[start:end])

# Made with Bob