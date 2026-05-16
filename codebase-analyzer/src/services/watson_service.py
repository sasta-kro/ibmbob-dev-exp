"""
IBM Watson AI Service - Integration with IBM watsonx.ai for code analysis.

This module handles communication with IBM Watson AI API for semantic code analysis,
bug detection, and improvement suggestions.
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


@dataclass
class AIAnalysisResult:
    """Result from AI analysis."""
    summary: str
    purpose: str
    functionality: List[str]
    potential_issues: List[str]
    suggestions: List[str]
    confidence: float
    model_used: str


class WatsonService:
    """
    Service for interacting with IBM watsonx.ai API.
    
    Features:
    - Code analysis and understanding
    - Bug detection
    - Improvement suggestions
    - Request batching and caching
    - Retry logic with exponential backoff
    """
    
    # API endpoints
    BASE_URL = "https://us-south.ml.cloud.ibm.com"
    TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
    
    # Model configurations
    MODELS = {
        'granite-code': 'ibm/granite-20b-code-instruct',
        'codellama': 'meta-llama/codellama-34b-instruct',
        'mixtral': 'mistralai/mixtral-8x7b-instruct-v01',
    }
    
    def __init__(self, config: Config):
        """
        Initialize Watson service.
        
        Args:
            config: Configuration object with API credentials
        """
        self.config = config
        self.api_key = config.get('watson_api_key') or os.getenv('WATSON_API_KEY')
        self.project_id = config.get('watson_project_id') or os.getenv('WATSON_PROJECT_ID')
        self.model = config.get('watson_model', 'granite-code')
        
        if not self.api_key:
            logger.warning("Watson API key not configured. AI features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
        
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        
        # Setup session with retry logic
        self.session = self._create_session()
        
        # Cache for AI responses
        self.cache: Dict[str, AIAnalysisResult] = {}
        self.cache_ttl = config.get('ai_cache_ttl', 7 * 24 * 3600)  # 7 days
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get or refresh IBM Cloud access token.
        
        Returns:
            Access token or None if authentication fails
        """
        # Check if token is still valid
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
        
        try:
            logger.info("Requesting new IBM Cloud access token")
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = {
                'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                'apikey': self.api_key,
            }
            
            response = self.session.post(
                self.TOKEN_URL,
                headers=headers,
                data=data,
                timeout=30
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            # Set expiry to 5 minutes before actual expiry for safety
            self.token_expiry = time.time() + token_data.get('expires_in', 3600) - 300
            
            logger.info("Successfully obtained access token")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if Watson service is available.
        
        Returns:
            True if service is configured and accessible
        """
        if not self.enabled:
            return False
        
        token = self._get_access_token()
        return token is not None
    
    def analyze_code(
        self,
        code: str,
        file_path: str,
        language: str,
        use_cache: bool = True
    ) -> Optional[AIAnalysisResult]:
        """
        Analyze code using IBM Watson AI.
        
        Args:
            code: Source code to analyze
            file_path: Path to the file (for context)
            language: Programming language
            use_cache: Whether to use cached results
            
        Returns:
            AIAnalysisResult or None if analysis fails
        """
        if not self.enabled:
            logger.warning("Watson service is not enabled")
            return None
        
        # Check cache
        cache_key = self._get_cache_key(code)
        if use_cache and cache_key in self.cache:
            logger.debug(f"Using cached analysis for {file_path}")
            return self.cache[cache_key]
        
        try:
            # Get access token
            token = self._get_access_token()
            if not token:
                return None
            
            # Prepare prompt
            prompt = self._create_analysis_prompt(code, file_path, language)
            
            # Call Watson API
            result = self._call_watson_api(prompt, token)
            
            if result:
                # Cache the result
                self.cache[cache_key] = result
                logger.info(f"Successfully analyzed {file_path}")
                return result
            
        except Exception as e:
            logger.error(f"Error analyzing code with Watson: {e}")
        
        return None
    
    def detect_bugs(
        self,
        code: str,
        file_path: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Detect potential bugs in code using AI.
        
        Args:
            code: Source code to analyze
            file_path: Path to the file
            language: Programming language
            
        Returns:
            List of detected issues
        """
        if not self.enabled:
            return []
        
        try:
            token = self._get_access_token()
            if not token:
                return []
            
            prompt = self._create_bug_detection_prompt(code, language)
            result = self._call_watson_api(prompt, token)
            
            if result and result.potential_issues:
                return [
                    {
                        'description': issue,
                        'severity': 'medium',
                        'file': file_path,
                    }
                    for issue in result.potential_issues
                ]
            
        except Exception as e:
            logger.error(f"Error detecting bugs: {e}")
        
        return []
    
    def suggest_improvements(
        self,
        code: str,
        file_path: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Get improvement suggestions for code.
        
        Args:
            code: Source code to analyze
            file_path: Path to the file
            language: Programming language
            
        Returns:
            List of improvement suggestions
        """
        if not self.enabled:
            return []
        
        try:
            token = self._get_access_token()
            if not token:
                return []
            
            prompt = self._create_improvement_prompt(code, language)
            result = self._call_watson_api(prompt, token)
            
            if result and result.suggestions:
                return [
                    {
                        'description': suggestion,
                        'priority': 'medium',
                        'file': file_path,
                    }
                    for suggestion in result.suggestions
                ]
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
        
        return []
    
    def _create_analysis_prompt(self, code: str, file_path: str, language: str) -> str:
        """Create prompt for code analysis."""
        return f"""Analyze this {language} code from {file_path} and provide:

1. A brief summary of what the code does
2. The primary purpose/functionality
3. Key functionalities (list 3-5 main features)
4. Potential issues or concerns
5. Suggestions for improvement

Code:
```{language}
{code[:2000]}  # Limit to first 2000 chars
```

Provide your analysis in JSON format with keys: summary, purpose, functionality (array), potential_issues (array), suggestions (array)."""
    
    def _create_bug_detection_prompt(self, code: str, language: str) -> str:
        """Create prompt for bug detection."""
        return f"""Review this {language} code for potential issues:

1. Logic errors and bugs
2. Type mismatches
3. Null/undefined access risks
4. Incorrect error handling
5. Security vulnerabilities

Code:
```{language}
{code[:2000]}
```

List each issue with specific line references if possible. Format as JSON array of issues."""
    
    def _create_improvement_prompt(self, code: str, language: str) -> str:
        """Create prompt for improvement suggestions."""
        return f"""Suggest improvements for this {language} code:

1. Performance optimizations
2. Code quality enhancements
3. Maintainability improvements
4. Security hardening
5. Best practices

Code:
```{language}
{code[:2000]}
```

Prioritize by impact and effort. Format as JSON array of suggestions."""
    
    def _call_watson_api(self, prompt: str, token: str) -> Optional[AIAnalysisResult]:
        """
        Call Watson API with the given prompt.
        
        Args:
            prompt: Analysis prompt
            token: Access token
            
        Returns:
            AIAnalysisResult or None
        """
        try:
            url = f"{self.BASE_URL}/ml/v1/text/generation?version=2023-05-29"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            
            model_id = self.MODELS.get(self.model, self.MODELS['granite-code'])
            
            payload = {
                'model_id': model_id,
                'input': prompt,
                'parameters': {
                    'max_new_tokens': 1000,
                    'temperature': 0.3,
                    'top_p': 0.9,
                    'top_k': 50,
                },
                'project_id': self.project_id,
            }
            
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse response
            generated_text = data['results'][0]['generated_text']
            
            # Try to parse as JSON
            try:
                # Extract JSON from response (might be wrapped in markdown)
                json_start = generated_text.find('{')
                json_end = generated_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = generated_text[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    # Fallback: create structured data from text
                    analysis_data = self._parse_text_response(generated_text)
            except json.JSONDecodeError:
                analysis_data = self._parse_text_response(generated_text)
            
            return AIAnalysisResult(
                summary=analysis_data.get('summary', ''),
                purpose=analysis_data.get('purpose', ''),
                functionality=analysis_data.get('functionality', []),
                potential_issues=analysis_data.get('potential_issues', []),
                suggestions=analysis_data.get('suggestions', []),
                confidence=0.8,  # Default confidence
                model_used=model_id
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Watson API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing Watson response: {e}")
            return None
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        return {
            'summary': text[:200] if text else '',
            'purpose': 'Analysis completed',
            'functionality': [],
            'potential_issues': [],
            'suggestions': [],
        }
    
    def _get_cache_key(self, code: str) -> str:
        """Generate cache key from code content."""
        return hashlib.sha256(code.encode('utf-8')).hexdigest()
    
    def clear_cache(self):
        """Clear the analysis cache."""
        self.cache.clear()
        logger.info("Watson service cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'cached_items': len(self.cache),
            'cache_ttl': self.cache_ttl,
        }

# Made with Bob
