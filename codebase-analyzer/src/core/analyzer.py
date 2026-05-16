"""
Analyzer Engine - Orchestrates code analysis using static analysis and AI.

This module coordinates AST parsing, complexity metrics, code quality checks,
and AI-powered semantic analysis.
"""

import ast
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models.file_info import FileInfo, CodeElement, ImportInfo, FileMetrics
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class AnalyzerEngine:
    """
    Main analyzer engine that orchestrates code analysis.
    
    Features:
    - AST parsing for Python and JavaScript
    - Complexity metrics calculation
    - Code quality analysis
    - Parallel processing of files
    - Integration with AI services
    """
    
    def __init__(self, config: Config):
        """
        Initialize the analyzer engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.max_workers = config.get('max_workers', 4)
        
    def analyze_files(self, files: List[FileInfo], progress_callback=None) -> List[FileInfo]:
        """
        Analyze multiple files in parallel.
        
        Args:
            files: List of FileInfo objects to analyze
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of analyzed FileInfo objects with populated analysis data
        """
        logger.info(f"Starting analysis of {len(files)} files")
        
        analyzed_files = []
        total = len(files)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all analysis tasks
            future_to_file = {
                executor.submit(self.analyze_file, file_info): file_info
                for file_info in files
            }
            
            # Process completed tasks
            for idx, future in enumerate(as_completed(future_to_file), 1):
                file_info = future_to_file[future]
                try:
                    analyzed_file = future.result()
                    if analyzed_file:
                        analyzed_files.append(analyzed_file)
                    
                    if progress_callback:
                        progress_callback(f"Analyzed {file_info.name}", idx, total)
                        
                except Exception as e:
                    logger.error(f"Error analyzing {file_info.path}: {e}")
                    file_info.parse_errors.append(str(e))
                    analyzed_files.append(file_info)
        
        logger.info(f"Analysis complete: {len(analyzed_files)} files processed")
        return analyzed_files
    
    def analyze_file(self, file_info: FileInfo) -> Optional[FileInfo]:
        """
        Analyze a single file based on its type.
        
        Args:
            file_info: FileInfo object to analyze
            
        Returns:
            Updated FileInfo with analysis results
        """
        try:
            # Read file content
            content = self._read_file(file_info.path)
            if not content:
                return file_info
            
            # Analyze based on file type
            if file_info.file_type.value == 'python':
                return self._analyze_python(file_info, content)
            elif file_info.file_type.value in ['javascript', 'typescript']:
                return self._analyze_javascript(file_info, content)
            else:
                # For other file types, just update basic metrics
                file_info.metrics = self._calculate_basic_metrics(content)
                return file_info
                
        except Exception as e:
            logger.error(f"Error analyzing file {file_info.path}: {e}")
            file_info.parse_errors.append(str(e))
            return file_info
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read file content safely."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _analyze_python(self, file_info: FileInfo, content: str) -> FileInfo:
        """
        Analyze Python file using AST.
        
        Args:
            file_info: FileInfo object
            content: File content
            
        Returns:
            Updated FileInfo with Python analysis
        """
        try:
            tree = ast.parse(content, filename=str(file_info.path))
            
            # Extract imports
            file_info.imports = self._extract_python_imports(tree)
            
            # Extract code elements (functions, classes, methods)
            file_info.code_elements = self._extract_python_elements(tree)
            
            # Calculate metrics
            file_info.metrics = self._calculate_python_metrics(tree, content)
            
            # Detect language features
            file_info.language_features = self._detect_python_features(tree)
            
            # Extract dependencies
            file_info.dependencies = self._extract_python_dependencies(tree)
            
        except SyntaxError as e:
            file_info.parse_errors.append(f"Syntax error: {e}")
            logger.warning(f"Syntax error in {file_info.path}: {e}")
        except Exception as e:
            file_info.parse_errors.append(f"Parse error: {e}")
            logger.error(f"Error parsing Python file {file_info.path}: {e}")
        
        return file_info
    
    def _extract_python_imports(self, tree: ast.AST) -> List[ImportInfo]:
        """Extract import statements from Python AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        names=[alias.name],
                        alias=alias.asname,
                        is_relative=False,
                        line_number=node.lineno
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = [alias.name for alias in node.names]
                imports.append(ImportInfo(
                    module=module,
                    names=names,
                    alias=None,
                    is_relative=node.level > 0,
                    line_number=node.lineno
                ))
        
        return imports
    
    def _extract_python_elements(self, tree: ast.AST) -> List[CodeElement]:
        """Extract code elements (functions, classes, methods) from Python AST."""
        elements = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                element = self._create_function_element(node)
                elements.append(element)
            elif isinstance(node, ast.ClassDef):
                element = self._create_class_element(node)
                elements.append(element)
        
        return elements
    
    def _create_function_element(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> CodeElement:
        """Create CodeElement from function AST node."""
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Check if private
        is_private = node.name.startswith('_')
        
        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Calculate complexity
        complexity = self._calculate_complexity(node)
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else None
        
        return CodeElement(
            name=node.name,
            type='function',
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            complexity=complexity,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            is_async=is_async,
            is_private=is_private,
            parent=None
        )
    
    def _create_class_element(self, node: ast.ClassDef) -> CodeElement:
        """Create CodeElement from class AST node."""
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Check if private
        is_private = node.name.startswith('_')
        
        # Extract base classes
        bases = [self._get_base_name(base) for base in node.bases]
        
        return CodeElement(
            name=node.name,
            type='class',
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            complexity=None,
            parameters=bases,  # Store base classes in parameters
            return_type=None,
            decorators=decorators,
            is_async=False,
            is_private=is_private,
            parent=None
        )
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return 'unknown'
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return ast.unparse(base) if hasattr(ast, 'unparse') else 'unknown'
        return 'unknown'
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity for a function.
        
        Complexity is increased by:
        - if/elif statements
        - for/while loops
        - except handlers
        - boolean operators (and/or)
        - comprehensions
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def _calculate_python_metrics(self, tree: ast.AST, content: str) -> FileMetrics:
        """Calculate code metrics for Python file."""
        lines = content.split('\n')
        
        # Count different line types
        lines_of_code = 0
        blank_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                lines_of_code += 1
        
        # Count functions and classes
        functions_count = 0
        classes_count = 0
        methods_count = 0
        total_complexity = 0
        
        # First pass: collect all classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        classes_count = len(classes)
        
        # Second pass: count functions and methods
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if it's a method (inside a class)
                is_method = False
                for cls in classes:
                    if hasattr(cls, 'body') and node in cls.body:
                        is_method = True
                        break
                
                if is_method:
                    methods_count += 1
                else:
                    functions_count += 1
                
                total_complexity += self._calculate_complexity(node)
        
        return FileMetrics(
            lines_of_code=lines_of_code,
            blank_lines=blank_lines,
            comment_lines=comment_lines,
            complexity=total_complexity,
            functions_count=functions_count,
            classes_count=classes_count,
            methods_count=methods_count,
            maintainability_index=None  # Can be calculated later
        )
    
    def _detect_python_features(self, tree: ast.AST) -> Dict[str, bool]:
        """Detect Python language features used in the code."""
        features = {
            'async_await': False,
            'type_hints': False,
            'decorators': False,
            'context_managers': False,
            'generators': False,
            'comprehensions': False,
            'f_strings': False,
            'dataclasses': False,
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith)):
                features['async_await'] = True
            
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    features['type_hints'] = True
                if node.decorator_list:
                    features['decorators'] = True
            
            if isinstance(node, (ast.With, ast.AsyncWith)):
                features['context_managers'] = True
            
            if isinstance(node, (ast.Yield, ast.YieldFrom)):
                features['generators'] = True
            
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                features['comprehensions'] = True
            
            if isinstance(node, ast.JoinedStr):  # f-string
                features['f_strings'] = True
        
        return features
    
    def _extract_python_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract external dependencies from Python imports."""
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get top-level package name
                    package = alias.name.split('.')[0]
                    dependencies.add(package)
            elif isinstance(node, ast.ImportFrom):
                if node.module and not node.level:  # Not relative import
                    package = node.module.split('.')[0]
                    dependencies.add(package)
        
        return sorted(list(dependencies))
    
    def _analyze_javascript(self, file_info: FileInfo, content: str) -> FileInfo:
        """
        Analyze JavaScript/TypeScript file.
        
        Note: This is a simplified implementation. For production,
        consider using a proper JavaScript parser like esprima or babel.
        
        Args:
            file_info: FileInfo object
            content: File content
            
        Returns:
            Updated FileInfo with JavaScript analysis
        """
        try:
            # Calculate basic metrics
            file_info.metrics = self._calculate_basic_metrics(content)
            
            # Extract imports (simple regex-based for now)
            file_info.imports = self._extract_js_imports(content)
            
            # Detect frameworks
            file_info.frameworks_detected = self._detect_js_frameworks(content)
            
            # Note: For full AST parsing, we would need a JavaScript parser
            # This is a placeholder for basic analysis
            
        except Exception as e:
            file_info.parse_errors.append(f"JavaScript parse error: {e}")
            logger.error(f"Error parsing JavaScript file {file_info.path}: {e}")
        
        return file_info
    
    def _extract_js_imports(self, content: str) -> List[ImportInfo]:
        """Extract JavaScript imports using simple pattern matching."""
        import re
        imports = []
        
        # Match ES6 imports: import ... from '...'
        import_pattern = r"import\s+(?:{[^}]+}|\*\s+as\s+\w+|\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        matches = re.finditer(import_pattern, content)
        
        for match in matches:
            module = match.group(1)
            imports.append(ImportInfo(
                module=module,
                names=[],
                alias=None,
                is_relative=module.startswith('.'),
                line_number=content[:match.start()].count('\n') + 1
            ))
        
        # Match require: const ... = require('...')
        require_pattern = r"require\(['\"]([^'\"]+)['\"]\)"
        matches = re.finditer(require_pattern, content)
        
        for match in matches:
            module = match.group(1)
            imports.append(ImportInfo(
                module=module,
                names=[],
                alias=None,
                is_relative=module.startswith('.'),
                line_number=content[:match.start()].count('\n') + 1
            ))
        
        return imports
    
    def _detect_js_frameworks(self, content: str) -> List[str]:
        """Detect JavaScript frameworks from imports and code patterns."""
        frameworks = []
        
        framework_patterns = {
            'react': ['react', 'useState', 'useEffect', 'Component'],
            'vue': ['vue', 'createApp', 'defineComponent'],
            'angular': ['@angular', 'Component', 'Injectable'],
            'express': ['express', 'app.get', 'app.post'],
            'nextjs': ['next/', 'getServerSideProps', 'getStaticProps'],
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in content for pattern in patterns):
                frameworks.append(framework)
        
        return frameworks
    
    def _calculate_basic_metrics(self, content: str) -> FileMetrics:
        """Calculate basic metrics for any file type."""
        lines = content.split('\n')
        
        lines_of_code = 0
        blank_lines = 0
        comment_lines = 0
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Handle multi-line comments
            if '/*' in stripped:
                in_multiline_comment = True
            if '*/' in stripped:
                in_multiline_comment = False
                comment_lines += 1
                continue
            
            if in_multiline_comment:
                comment_lines += 1
            elif not stripped:
                blank_lines += 1
            elif stripped.startswith('//') or stripped.startswith('#'):
                comment_lines += 1
            else:
                lines_of_code += 1
        
        return FileMetrics(
            lines_of_code=lines_of_code,
            blank_lines=blank_lines,
            comment_lines=comment_lines,
            complexity=0,
            functions_count=0,
            classes_count=0,
            methods_count=0
        )

# Made with Bob
