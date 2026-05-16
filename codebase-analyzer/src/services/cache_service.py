"""
Cache Service - SQLite-based caching for analysis results.

This module provides persistent caching of file analysis results, AI responses,
and other computed data to improve performance on subsequent runs.
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from contextlib import contextmanager

from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class CacheService:
    """
    SQLite-based cache service for storing analysis results.
    
    Features:
    - Persistent storage of analysis results
    - TTL-based cache invalidation
    - Content hash-based cache keys
    - Automatic cleanup of expired entries
    - Thread-safe operations
    """
    
    def __init__(self, config: Config, cache_dir: Optional[Path] = None):
        """
        Initialize cache service.
        
        Args:
            config: Configuration object
            cache_dir: Directory for cache database (default: .cache)
        """
        self.config = config
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path.cwd() / '.cache'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / 'analysis_cache.db'
        
        # Cache TTL settings (in seconds)
        self.default_ttl = config.get('cache_ttl', 7 * 24 * 3600)  # 7 days
        self.ai_cache_ttl = config.get('ai_cache_ttl', 7 * 24 * 3600)  # 7 days
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Cache service initialized at {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # File analysis cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    analysis_data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    UNIQUE(file_path, content_hash)
                )
            """)
            
            # AI response cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_hash TEXT NOT NULL UNIQUE,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    model TEXT,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            
            # Project metadata cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL UNIQUE,
                    metadata TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_analysis_hash 
                ON file_analysis(content_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_analysis_expires 
                ON file_analysis(expires_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_responses_hash 
                ON ai_responses(prompt_hash)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_responses_expires 
                ON ai_responses(expires_at)
            """)
            
            conn.commit()
            logger.debug("Database tables initialized")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_file_analysis(
        self,
        file_path: str,
        content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached file analysis result.
        
        Args:
            file_path: Path to the file
            content_hash: SHA256 hash of file content
            
        Returns:
            Cached analysis data or None if not found/expired
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                current_time = time.time()
                
                cursor.execute("""
                    SELECT analysis_data, expires_at
                    FROM file_analysis
                    WHERE file_path = ? AND content_hash = ?
                """, (file_path, content_hash))
                
                row = cursor.fetchone()
                
                if row:
                    expires_at = row['expires_at']
                    
                    # Check if expired
                    if current_time < expires_at:
                        analysis_data = json.loads(row['analysis_data'])
                        logger.debug(f"Cache hit for {file_path}")
                        return analysis_data
                    else:
                        # Delete expired entry
                        cursor.execute("""
                            DELETE FROM file_analysis
                            WHERE file_path = ? AND content_hash = ?
                        """, (file_path, content_hash))
                        conn.commit()
                        logger.debug(f"Expired cache entry deleted for {file_path}")
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached analysis: {e}")
            return None
    
    def set_file_analysis(
        self,
        file_path: str,
        content_hash: str,
        analysis_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache file analysis result.
        
        Args:
            file_path: Path to the file
            content_hash: SHA256 hash of file content
            analysis_data: Analysis data to cache
            ttl: Time to live in seconds (default: use config)
            
        Returns:
            True if successfully cached
        """
        try:
            ttl_value = ttl if ttl is not None else self.default_ttl
            
            current_time = time.time()
            expires_at = current_time + ttl_value
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO file_analysis
                    (file_path, content_hash, analysis_data, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    file_path,
                    content_hash,
                    json.dumps(analysis_data),
                    current_time,
                    expires_at
                ))
                
                conn.commit()
                logger.debug(f"Cached analysis for {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error caching analysis: {e}")
            return False
    
    def get_ai_response(self, prompt_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached AI response.
        
        Args:
            prompt_hash: Hash of the prompt
            
        Returns:
            Cached response data or None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                current_time = time.time()
                
                cursor.execute("""
                    SELECT response, model, expires_at
                    FROM ai_responses
                    WHERE prompt_hash = ?
                """, (prompt_hash,))
                
                row = cursor.fetchone()
                
                if row:
                    expires_at = row['expires_at']
                    
                    if current_time < expires_at:
                        return {
                            'response': row['response'],
                            'model': row['model'],
                        }
                    else:
                        # Delete expired entry
                        cursor.execute("""
                            DELETE FROM ai_responses
                            WHERE prompt_hash = ?
                        """, (prompt_hash,))
                        conn.commit()
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached AI response: {e}")
            return None
    
    def set_ai_response(
        self,
        prompt_hash: str,
        prompt: str,
        response: str,
        model: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache AI response.
        
        Args:
            prompt_hash: Hash of the prompt
            prompt: Original prompt text
            response: AI response
            model: Model used
            ttl: Time to live in seconds
            
        Returns:
            True if successfully cached
        """
        try:
            ttl_value = ttl if ttl is not None else self.ai_cache_ttl
            
            current_time = time.time()
            expires_at = current_time + ttl_value
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO ai_responses
                    (prompt_hash, prompt, response, model, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prompt_hash,
                    prompt,
                    response,
                    model,
                    current_time,
                    expires_at
                ))
                
                conn.commit()
                logger.debug(f"Cached AI response")
                return True
                
        except Exception as e:
            logger.error(f"Error caching AI response: {e}")
            return False
    
    def get_project_metadata(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached project metadata.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Cached metadata or None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT metadata, updated_at
                    FROM project_metadata
                    WHERE project_path = ?
                """, (project_path,))
                
                row = cursor.fetchone()
                
                if row:
                    metadata = json.loads(row['metadata'])
                    metadata['cached_at'] = row['updated_at']
                    return metadata
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting project metadata: {e}")
            return None
    
    def set_project_metadata(
        self,
        project_path: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Cache project metadata.
        
        Args:
            project_path: Path to the project
            metadata: Metadata to cache
            
        Returns:
            True if successfully cached
        """
        try:
            current_time = time.time()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO project_metadata
                    (project_path, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    project_path,
                    json.dumps(metadata),
                    current_time,
                    current_time
                ))
                
                conn.commit()
                logger.debug(f"Cached project metadata for {project_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error caching project metadata: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        try:
            current_time = time.time()
            total_deleted = 0
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean file analysis cache
                cursor.execute("""
                    DELETE FROM file_analysis
                    WHERE expires_at < ?
                """, (current_time,))
                deleted = cursor.rowcount
                total_deleted += deleted
                
                # Clean AI responses cache
                cursor.execute("""
                    DELETE FROM ai_responses
                    WHERE expires_at < ?
                """, (current_time,))
                deleted = cursor.rowcount
                total_deleted += deleted
                
                conn.commit()
                
                if total_deleted > 0:
                    logger.info(f"Cleaned up {total_deleted} expired cache entries")
                
                return total_deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM file_analysis")
                cursor.execute("DELETE FROM ai_responses")
                cursor.execute("DELETE FROM project_metadata")
                
                conn.commit()
                
                logger.info("All cache entries cleared")
                return True
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Count file analysis entries
                cursor.execute("SELECT COUNT(*) as count FROM file_analysis")
                file_analysis_count = cursor.fetchone()['count']
                
                # Count AI responses
                cursor.execute("SELECT COUNT(*) as count FROM ai_responses")
                ai_responses_count = cursor.fetchone()['count']
                
                # Count project metadata
                cursor.execute("SELECT COUNT(*) as count FROM project_metadata")
                project_metadata_count = cursor.fetchone()['count']
                
                # Get database size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                return {
                    'file_analysis_entries': file_analysis_count,
                    'ai_response_entries': ai_responses_count,
                    'project_metadata_entries': project_metadata_count,
                    'total_entries': file_analysis_count + ai_responses_count + project_metadata_count,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'database_path': str(self.db_path),
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def vacuum(self) -> bool:
        """
        Optimize database by running VACUUM.
        
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")
                return True
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            return False

# Made with Bob
