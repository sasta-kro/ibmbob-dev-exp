"""
Static Code Analyzer

Integrates multiple static analysis tools to detect code quality issues,
security vulnerabilities, and complexity problems.

Made with Bob
"""

import ast
import re
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..models.finding import Finding, Severity, FindingType, CodeLocation
from ..models.file_info import FileInfo, FileType
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StaticAnalysisResult:
    """Result from static analysis tools"""
    findings: List[Finding]
    tool_name: str
    files_analyzed: int
    errors: List[str]


class StaticAnalyzer:
    """
    Static code analyzer that integrates multiple analysis tools.
    
    Supports:
    - Pylint for Python code quality
    - Bandit for security issues
    - Radon for complexity metrics
    - Custom pattern-based detection
    """
    
    def __init__(self, config: Any):
        """
        Initialize static analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logger
        
        # Pattern-based detections
        self.security_patterns = self._init_security_patterns()
        self.bug_patterns = self._init_bug_patterns()
        self.performance_patterns = self._init_performance_patterns()
    
    def analyze_files(self, files: List[FileInfo]) -> List[Finding]:
        """
        Analyze files using all available static analysis tools.
        
        Args:
            files: List of FileInfo objects to analyze
            
        Returns:
            List of Finding objects
        """
        self.logger.info(f"Starting static analysis on {len(files)} files")
        
        all_findings = []
        
        # Run different analysis methods
        all_findings.extend(self._run_pattern_analysis(files))
        all_findings.extend(self._run_pylint_analysis(files))
        all_findings.extend(self._run_bandit_analysis(files))
        all_findings.extend(self._run_complexity_analysis(files))
        all_findings.extend(self._run_ast_analysis(files))
        
        # Deduplicate findings
        unique_findings = self._deduplicate_findings(all_findings)
        
        self.logger.info(f"Static analysis complete: {len(unique_findings)} findings")
        return unique_findings
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Could not read {file_path}: {e}")
            return None
    
    def _run_pattern_analysis(self, files: List[FileInfo]) -> List[Finding]:
        """Run regex pattern-based analysis"""
        findings = []
        
        for file_info in files:
            content = self._read_file_content(file_info.path)
            if not content:
                continue
            
            # Security patterns
            findings.extend(self._check_security_patterns(file_info, content))
            
            # Bug patterns
            findings.extend(self._check_bug_patterns(file_info, content))
            
            # Performance patterns
            findings.extend(self._check_performance_patterns(file_info, content))
        
        return findings
    
    def _check_security_patterns(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Check for security issues using patterns"""
        findings = []
        
        for pattern_name, pattern_data in self.security_patterns.items():
            matches = re.finditer(pattern_data['pattern'], content, re.MULTILINE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = self._extract_code_snippet(content, line_num)
                
                location = CodeLocation(
                    file_path=file_info.path,
                    line_start=line_num,
                    line_end=line_num,
                    code_snippet=code_snippet
                )
                
                finding = Finding(
                    id=f"SEC-{pattern_name}-{file_info.relative_path}-{line_num}",
                    title=pattern_data['title'],
                    description=pattern_data['problem'],
                    severity=Severity(pattern_data['severity']),
                    finding_type=FindingType.SECURITY,
                    confidence=0.9,
                    location=location,
                    message=pattern_data['problem'],
                    explanation=pattern_data['why_it_matters'],
                    impact="Security vulnerability that could be exploited",
                    recommendation=pattern_data['fix'],
                    suggested_fix=pattern_data['fix'],
                    source='pattern-analyzer',
                    rule_id=f"SEC-{pattern_name}",
                    tags=['security', 'pattern-based']
                )
                findings.append(finding)
        
        return findings
    
    def _check_bug_patterns(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Check for common bug patterns"""
        findings = []
        
        for pattern_name, pattern_data in self.bug_patterns.items():
            matches = re.finditer(pattern_data['pattern'], content, re.MULTILINE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = self._extract_code_snippet(content, line_num)
                
                location = CodeLocation(
                    file_path=file_info.path,
                    line_start=line_num,
                    line_end=line_num,
                    code_snippet=code_snippet
                )
                
                finding = Finding(
                    id=f"BUG-{pattern_name}-{file_info.relative_path}-{line_num}",
                    title=pattern_data['title'],
                    description=pattern_data['problem'],
                    severity=Severity(pattern_data['severity']),
                    finding_type=FindingType.BUG,
                    confidence=0.7,
                    location=location,
                    message=pattern_data['problem'],
                    explanation=pattern_data['why_it_matters'],
                    impact="Potential bug that could cause runtime errors",
                    recommendation=pattern_data['fix'],
                    suggested_fix=pattern_data['fix'],
                    source='pattern-analyzer',
                    rule_id=f"BUG-{pattern_name}",
                    tags=['bug', 'pattern-based']
                )
                findings.append(finding)
        
        return findings
    
    def _check_performance_patterns(self, file_info: FileInfo, content: str) -> List[Finding]:
        """Check for performance issues using patterns"""
        findings = []
        
        for pattern_name, pattern_data in self.performance_patterns.items():
            matches = re.finditer(pattern_data['pattern'], content, re.MULTILINE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = self._extract_code_snippet(content, line_num)
                
                location = CodeLocation(
                    file_path=file_info.path,
                    line_start=line_num,
                    line_end=line_num,
                    code_snippet=code_snippet
                )
                
                finding = Finding(
                    id=f"PERF-{pattern_name}-{file_info.relative_path}-{line_num}",
                    title=pattern_data['title'],
                    description=pattern_data['problem'],
                    severity=Severity(pattern_data['severity']),
                    finding_type=FindingType.PERFORMANCE,
                    confidence=0.6,
                    location=location,
                    message=pattern_data['problem'],
                    explanation=pattern_data['why_it_matters'],
                    impact="Performance degradation for large datasets",
                    recommendation=pattern_data['fix'],
                    suggested_fix=pattern_data['fix'],
                    source='pattern-analyzer',
                    rule_id=f"PERF-{pattern_name}",
                    tags=['performance', 'pattern-based']
                )
                findings.append(finding)
        
        return findings
    
    def _extract_code_snippet(self, content: str, line_num: int, context_lines: int = 2) -> str:
        """Extract code snippet with context"""
        lines = content.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        return '\n'.join(lines[start:end])
    
    def _run_pylint_analysis(self, files: List[FileInfo]) -> List[Finding]:
        """Run pylint analysis on Python files"""
        findings = []
        python_files = [f for f in files if f.file_type == FileType.PYTHON]
        
        if not python_files:
            return findings
        
        self.logger.info(f"Running pylint on {len(python_files)} Python files")
        
        for file_info in python_files:
            try:
                result = subprocess.run(
                    ['pylint', '--output-format=json', str(file_info.path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    pylint_results = json.loads(result.stdout)
                    findings.extend(self._parse_pylint_results(pylint_results, file_info))
                    
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Pylint timeout on {file_info.path}")
            except FileNotFoundError:
                self.logger.debug("Pylint not installed, skipping")
                break
            except Exception as e:
                self.logger.warning(f"Pylint error on {file_info.path}: {e}")
        
        return findings
    
    def _parse_pylint_results(self, results: List[Dict], file_info: FileInfo) -> List[Finding]:
        """Parse pylint JSON output into Finding objects"""
        findings = []
        
        severity_map = {
            'error': Severity.HIGH,
            'warning': Severity.MEDIUM,
            'refactor': Severity.LOW,
            'convention': Severity.INFO,
            'info': Severity.INFO
        }
        
        for item in results:
            severity = severity_map.get(item.get('type', 'info'), Severity.INFO)
            line_num = item.get('line', 0)
            
            content = self._read_file_content(file_info.path)
            code_snippet = self._extract_code_snippet(content, line_num) if content else ""
            
            location = CodeLocation(
                file_path=file_info.path,
                line_start=line_num,
                line_end=item.get('endLine', line_num),
                code_snippet=code_snippet
            )
            
            finding = Finding(
                id=f"PYLINT-{item.get('message-id', 'UNKNOWN')}-{file_info.relative_path}-{line_num}",
                title=item.get('message', 'Pylint issue'),
                description=item.get('message', ''),
                severity=severity,
                finding_type=FindingType.STYLE,
                confidence=0.9,
                location=location,
                message=item.get('message', ''),
                explanation='Code quality and maintainability issue',
                impact='Reduced code quality and maintainability',
                recommendation=f"Fix {item.get('message-id', '')} issue",
                source='pylint',
                rule_id=item.get('message-id', ''),
                tags=['pylint', 'code-quality']
            )
            findings.append(finding)
        
        return findings
    
    def _run_bandit_analysis(self, files: List[FileInfo]) -> List[Finding]:
        """Run bandit security analysis on Python files"""
        findings = []
        python_files = [f for f in files if f.file_type == FileType.PYTHON]
        
        if not python_files:
            return findings
        
        self.logger.info(f"Running bandit on {len(python_files)} Python files")
        
        for file_info in python_files:
            try:
                result = subprocess.run(
                    ['bandit', '-f', 'json', str(file_info.path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    bandit_results = json.loads(result.stdout)
                    findings.extend(self._parse_bandit_results(bandit_results, file_info))
                    
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Bandit timeout on {file_info.path}")
            except FileNotFoundError:
                self.logger.debug("Bandit not installed, skipping")
                break
            except Exception as e:
                self.logger.warning(f"Bandit error on {file_info.path}: {e}")
        
        return findings
    
    def _parse_bandit_results(self, results: Dict, file_info: FileInfo) -> List[Finding]:
        """Parse bandit JSON output into Finding objects"""
        findings = []
        
        severity_map = {
            'HIGH': Severity.HIGH,
            'MEDIUM': Severity.MEDIUM,
            'LOW': Severity.LOW
        }
        
        confidence_map = {
            'HIGH': 0.9,
            'MEDIUM': 0.7,
            'LOW': 0.5
        }
        
        for item in results.get('results', []):
            severity = severity_map.get(item.get('issue_severity', 'LOW'), Severity.LOW)
            confidence = confidence_map.get(item.get('issue_confidence', 'MEDIUM'), 0.7)
            line_num = item.get('line_number', 0)
            
            location = CodeLocation(
                file_path=file_info.path,
                line_start=line_num,
                line_end=line_num,
                code_snippet=item.get('code', '').strip()
            )
            
            finding = Finding(
                id=f"BANDIT-{item.get('test_id', 'UNKNOWN')}-{file_info.relative_path}-{line_num}",
                title=item.get('issue_text', 'Security issue'),
                description=item.get('issue_text', ''),
                severity=severity,
                finding_type=FindingType.SECURITY,
                confidence=confidence,
                location=location,
                message=item.get('issue_text', ''),
                explanation='Security vulnerability that could be exploited',
                impact='Potential security breach or data exposure',
                recommendation=item.get('more_info', 'Review security best practices'),
                source='bandit',
                rule_id=item.get('test_id', ''),
                tags=['bandit', 'security']
            )
            findings.append(finding)
        
        return findings
    
    def _run_complexity_analysis(self, files: List[FileInfo]) -> List[Finding]:
        """Analyze code complexity and flag high complexity"""
        findings = []
        
        for file_info in files:
            if file_info.file_type != FileType.PYTHON:
                continue
            
            # Check cyclomatic complexity
            complexity = file_info.metrics.complexity
            if complexity > 10:
                location = CodeLocation(
                    file_path=file_info.path,
                    line_start=1,
                    line_end=file_info.metrics.lines_of_code,
                    code_snippet=f"Total complexity: {complexity}"
                )
                
                finding = Finding(
                    id=f"COMPLEXITY-{file_info.relative_path}",
                    title="High cyclomatic complexity",
                    description=f"File has cyclomatic complexity of {complexity}",
                    severity=Severity.MEDIUM,
                    finding_type=FindingType.MAINTAINABILITY,
                    confidence=1.0,
                    location=location,
                    message=f"File has cyclomatic complexity of {complexity}",
                    explanation='High complexity makes code harder to understand, test, and maintain',
                    impact='Increased maintenance cost and bug risk',
                    recommendation='Consider breaking down complex functions into smaller, more focused functions',
                    source='complexity-analyzer',
                    rule_id='HIGH-COMPLEXITY',
                    tags=['complexity', 'maintainability']
                )
                findings.append(finding)
        
        return findings
    
    def _run_ast_analysis(self, files: List[FileInfo]) -> List[Finding]:
        """Run AST-based analysis for Python files"""
        findings = []
        
        for file_info in files:
            if file_info.file_type != FileType.PYTHON:
                continue
            
            content = self._read_file_content(file_info.path)
            if not content:
                continue
            
            try:
                tree = ast.parse(content)
                findings.extend(self._analyze_ast(tree, file_info, content))
            except SyntaxError:
                pass
            except Exception as e:
                self.logger.warning(f"AST analysis error on {file_info.path}: {e}")
        
        return findings
    
    def _analyze_ast(self, tree: ast.AST, file_info: FileInfo, content: str) -> List[Finding]:
        """Analyze AST for common issues"""
        findings = []
        
        for node in ast.walk(tree):
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                code_snippet = self._extract_code_snippet(content, node.lineno)
                location = CodeLocation(
                    file_path=file_info.path,
                    line_start=node.lineno,
                    line_end=node.lineno,
                    code_snippet=code_snippet
                )
                
                finding = Finding(
                    id=f"AST-BARE-EXCEPT-{file_info.relative_path}-{node.lineno}",
                    title="Bare except clause",
                    description="Using bare 'except:' catches all exceptions including system exits",
                    severity=Severity.MEDIUM,
                    finding_type=FindingType.BUG,
                    confidence=1.0,
                    location=location,
                    message="Using bare 'except:' catches all exceptions including system exits",
                    explanation='Can hide bugs and make debugging difficult',
                    impact='Hidden errors and difficult debugging',
                    recommendation='Use specific exception types: except Exception:',
                    source='ast-analyzer',
                    rule_id='BARE-EXCEPT',
                    tags=['ast', 'error-handling']
                )
                findings.append(finding)
            
            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        code_snippet = self._extract_code_snippet(content, node.lineno)
                        location = CodeLocation(
                            file_path=file_info.path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            code_snippet=code_snippet
                        )
                        
                        finding = Finding(
                            id=f"AST-MUTABLE-DEFAULT-{file_info.relative_path}-{node.lineno}",
                            title="Mutable default argument",
                            description=f"Function '{node.name}' has mutable default argument",
                            severity=Severity.HIGH,
                            finding_type=FindingType.BUG,
                            confidence=1.0,
                            location=location,
                            message=f"Function '{node.name}' has mutable default argument",
                            explanation='Mutable defaults are shared between calls, causing unexpected behavior',
                            impact='Unexpected behavior and hard-to-debug issues',
                            recommendation='Use None as default and create mutable object inside function',
                            source='ast-analyzer',
                            rule_id='MUTABLE-DEFAULT',
                            tags=['ast', 'bug']
                        )
                        findings.append(finding)
        
        return findings
    
    def _deduplicate_findings(self, findings: List[Finding]) -> List[Finding]:
        """Remove duplicate findings based on file, line, and type"""
        seen = set()
        unique = []
        
        for finding in findings:
            key = (
                str(finding.location.file_path),
                finding.location.line_start,
                finding.finding_type,
                finding.title
            )
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        
        return unique
    
    def _init_security_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security detection patterns"""
        return {
            'hardcoded_password': {
                'pattern': r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                'title': 'Hardcoded password detected',
                'severity': 'critical',
                'problem': 'Password is hardcoded in source code',
                'why_it_matters': 'Hardcoded credentials are a security risk and can be exposed in version control',
                'fix': 'Use environment variables or secure credential management'
            },
            'hardcoded_api_key': {
                'pattern': r'(?i)(api[_-]?key|apikey|access[_-]?key)\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
                'title': 'Hardcoded API key detected',
                'severity': 'critical',
                'problem': 'API key is hardcoded in source code',
                'why_it_matters': 'Exposed API keys can lead to unauthorized access and costs',
                'fix': 'Use environment variables or secret management service'
            },
            'sql_injection_risk': {
                'pattern': r'execute\([^)]*%s[^)]*\)|cursor\.execute\([^)]*\+[^)]*\)',
                'title': 'Potential SQL injection vulnerability',
                'severity': 'high',
                'problem': 'SQL query uses string formatting or concatenation',
                'why_it_matters': 'SQL injection can lead to data breaches and unauthorized access',
                'fix': 'Use parameterized queries or ORM'
            },
            'eval_usage': {
                'pattern': r'\beval\s*\(',
                'title': 'Use of eval() detected',
                'severity': 'high',
                'problem': 'eval() executes arbitrary code',
                'why_it_matters': 'Can lead to code injection vulnerabilities',
                'fix': 'Use safer alternatives like ast.literal_eval() or json.loads()'
            },
            'exec_usage': {
                'pattern': r'\bexec\s*\(',
                'title': 'Use of exec() detected',
                'severity': 'high',
                'problem': 'exec() executes arbitrary code',
                'why_it_matters': 'Can lead to code injection vulnerabilities',
                'fix': 'Avoid exec() or carefully validate input'
            }
        }
    
    def _init_bug_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize bug detection patterns"""
        return {
            'comparison_to_none': {
                'pattern': r'==\s*None|None\s*==',
                'title': 'Comparison to None using ==',
                'severity': 'low',
                'problem': 'Using == to compare with None',
                'why_it_matters': 'Should use "is None" for identity comparison',
                'fix': 'Use "is None" instead of "== None"'
            },
            'comparison_to_true': {
                'pattern': r'==\s*True|True\s*==|==\s*False|False\s*==',
                'title': 'Comparison to boolean using ==',
                'severity': 'low',
                'problem': 'Explicitly comparing to True/False',
                'why_it_matters': 'Redundant and less Pythonic',
                'fix': 'Use the value directly in boolean context'
            },
            'empty_except': {
                'pattern': r'except\s*:\s*pass',
                'title': 'Empty except clause',
                'severity': 'medium',
                'problem': 'Exception is caught but not handled',
                'why_it_matters': 'Silently ignoring errors makes debugging difficult',
                'fix': 'Log the exception or handle it appropriately'
            }
        }
    
    def _init_performance_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize performance issue patterns"""
        return {
            'list_comprehension_in_loop': {
                'pattern': r'for\s+\w+\s+in\s+\[.*for.*in.*\]',
                'title': 'List comprehension inside loop',
                'severity': 'low',
                'problem': 'Creating list comprehension in each loop iteration',
                'why_it_matters': 'Can be inefficient for large datasets',
                'fix': 'Consider moving comprehension outside loop or using generator'
            },
            'repeated_string_concat': {
                'pattern': r'(\w+)\s*\+=\s*["\'].*["\']',
                'title': 'String concatenation in loop',
                'severity': 'low',
                'problem': 'Using += for string concatenation',
                'why_it_matters': 'Strings are immutable, creating new objects each time',
                'fix': 'Use list and join() or io.StringIO for better performance'
            }
        }

# Made with Bob
