"""Configuration management for the Codebase Analyzer application."""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from loguru import logger


USER_CONFIG_FILENAME = "user_config.json"

DEFAULT_USER_CONFIG = {
    "watson_api_key": "",
    "watson_url": "https://us-south.ml.cloud.ibm.com",
    "watson_project_id": "",
    "watson_model_id": "openai/gpt-oss-120b",
    "watson_max_tokens": 2000,
    "watson_temperature": 0,
    "enable_ai": True,
    "generate_docs": True,
    "perform_review": True,
    "generate_suggestions": True,
    "theme": "light",
}


class Config:
    """Application configuration manager."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config.yaml file. If None, uses default location.
        """
        load_dotenv()

        project_root = Path(__file__).parent.parent.parent

        if config_path is None:
            config_path = project_root / "config" / "config.yaml"

        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()

        self._user_config_path = project_root / "config" / USER_CONFIG_FILENAME
        self._user_config: Dict[str, Any] = {}
        self._load_user_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Config file not found: {self.config_path}. Using defaults.")
                self._config = self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}. Using defaults.")
            self._config = self._get_default_config()

    def _load_user_config(self) -> None:
        """Load user config from JSON. On first run, seed from env vars and save."""
        if self._user_config_path.exists():
            try:
                with open(self._user_config_path, 'r', encoding='utf-8') as f:
                    self._user_config = json.load(f)
                logger.info(f"User config loaded from {self._user_config_path}")
            except Exception as e:
                logger.error(f"Error loading user config: {e}")
                self._user_config = dict(DEFAULT_USER_CONFIG)
        else:
            self._user_config = dict(DEFAULT_USER_CONFIG)
            self._user_config["watson_api_key"] = os.getenv("WATSON_API_KEY", "")
            self._user_config["watson_url"] = os.getenv("WATSON_URL", DEFAULT_USER_CONFIG["watson_url"])
            self._user_config["watson_project_id"] = os.getenv("WATSON_PROJECT_ID", "")
            self._user_config["watson_model_id"] = os.getenv("WATSON_MODEL_ID", DEFAULT_USER_CONFIG["watson_model_id"])
            self._user_config["watson_max_tokens"] = int(os.getenv("WATSON_MAX_TOKENS", str(DEFAULT_USER_CONFIG["watson_max_tokens"])))
            self._user_config["watson_temperature"] = float(os.getenv("WATSON_TEMPERATURE", str(DEFAULT_USER_CONFIG["watson_temperature"])))
            self.save_user_config()
            logger.info("First run detected — user config seeded from env vars")

    @property
    def is_first_run(self) -> bool:
        """True if user config was just created (no API key set)."""
        return not self._user_config.get("watson_api_key")

    @property
    def user_config(self) -> Dict[str, Any]:
        """Get full user config dict."""
        return dict(self._user_config)

    def update_user_config(self, updates: Dict[str, Any]) -> None:
        """Update user config with given key-value pairs and persist."""
        self._user_config.update(updates)
        self.save_user_config()

    def save_user_config(self) -> None:
        """Save user config to JSON."""
        try:
            self._user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._user_config_path, 'w', encoding='utf-8') as f:
                json.dump(self._user_config, f, indent=2)
            logger.info(f"User config saved to {self._user_config_path}")
        except Exception as e:
            logger.error(f"Error saving user config: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'app': {
                'name': 'Codebase Analyzer',
                'version': '1.0.0',
                'log_level': 'INFO'
            },
            'analysis': {
                'max_file_size_mb': 10,
                'max_workers': 4,
                'enable_ai_analysis': True,
                'timeout_seconds': 300
            },
            'cache': {
                'enabled': True,
                'ttl_hours': 24,
                'database_path': '.cache/analyzer.db'
            },
            'ui': {
                'theme': 'light',
                'window_width': 1400,
                'window_height': 900,
                'enable_animations': True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'app.name' or 'analysis.max_workers')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'app.name')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    # Convenience properties for common settings

    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.get('app.name', 'Codebase Analyzer')

    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.get('app.version', '1.0.0')

    @property
    def log_level(self) -> str:
        """Get log level."""
        return os.getenv('LOG_LEVEL', self.get('app.log_level', 'INFO'))

    @property
    def max_file_size_mb(self) -> int:
        """Get maximum file size in MB."""
        return self.get('analysis.max_file_size_mb', 10)

    @property
    def max_workers(self) -> int:
        """Get maximum number of worker threads."""
        return self.get('analysis.max_workers', 4)

    @property
    def enable_ai_analysis(self) -> bool:
        """Check if AI analysis is enabled."""
        return os.getenv('ENABLE_AI_ANALYSIS', str(self.get('analysis.enable_ai_analysis', True))).lower() == 'true'

    @property
    def ignore_patterns(self) -> List[str]:
        """Get ignore patterns."""
        return self.get('ignore_patterns', [])

    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return os.getenv('CACHE_ENABLED', str(self.get('cache.enabled', True))).lower() == 'true'

    @property
    def cache_ttl_hours(self) -> int:
        """Get cache TTL in hours."""
        return int(os.getenv('CACHE_TTL_HOURS', self.get('cache.ttl_hours', 24)))

    @property
    def cache_db_path(self) -> Path:
        """Get cache database path."""
        project_root = Path(__file__).parent.parent.parent
        return project_root / self.get('cache.database_path', '.cache/analyzer.db')

    @property
    def watson_api_key(self) -> Optional[str]:
        return self._user_config.get('watson_api_key') or os.getenv('WATSON_API_KEY')

    @property
    def watson_url(self) -> str:
        return self._user_config.get('watson_url') or os.getenv('WATSON_URL', 'https://us-south.ml.cloud.ibm.com')

    @property
    def watson_project_id(self) -> Optional[str]:
        return self._user_config.get('watson_project_id') or os.getenv('WATSON_PROJECT_ID')

    @property
    def watson_model_id(self) -> str:
        return self._user_config.get('watson_model_id') or os.getenv('WATSON_MODEL_ID', 'openai/gpt-oss-120b')

    @property
    def watson_max_tokens(self) -> int:
        return int(self._user_config.get('watson_max_tokens', 0) or os.getenv('WATSON_MAX_TOKENS', 2048))

    @property
    def watson_temperature(self) -> float:
        return float(self._user_config.get('watson_temperature', 0) or os.getenv('WATSON_TEMPERATURE', 0.7))

    @property
    def window_width(self) -> int:
        """Get UI window width."""
        return int(os.getenv('WINDOW_WIDTH', self.get('ui.window_width', 1400)))

    @property
    def window_height(self) -> int:
        """Get UI window height."""
        return int(os.getenv('WINDOW_HEIGHT', self.get('ui.window_height', 900)))

    @property
    def theme(self) -> str:
        """Get UI theme."""
        return os.getenv('THEME', self.get('ui.theme', 'light'))


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> None:
    """Reload configuration from file."""
    global _config
    _config = Config()

# Made with Bob
