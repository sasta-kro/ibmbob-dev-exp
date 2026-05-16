#!/usr/bin/env python3
"""
Test script to verify the installation and basic functionality
"""

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing imports...")
    try:
        from core import AnalysisOrchestrator, Scanner, Analyzer, Grouper
        from services import WatsonService, CacheService
        from models import FileInfo, Finding, Suggestion, Project
        from utils import Config, setup_logger
        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from utils import Config
        config = Config()
        print(f"✓ Configuration loaded successfully")
        print(f"  - App name: {config.app_name}")
        print(f"  - Version: {config.version}")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False

def test_scanner():
    """Test scanner initialization"""
    print("\nTesting scanner...")
    try:
        from core import Scanner
        from utils import Config
        config = Config()
        scanner = Scanner(config)
        print("✓ Scanner initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Scanner failed: {e}")
        return False

def test_cache():
    """Test cache service"""
    print("\nTesting cache service...")
    try:
        from services import CacheService
        from utils import Config
        config = Config()
        cache = CacheService(config)
        stats = cache.get_stats()
        print(f"✓ Cache service initialized successfully")
        print(f"  - Total entries: {stats['total_entries']}")
        return True
    except Exception as e:
        print(f"✗ Cache service failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Codebase Analyzer - Installation Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_scanner,
        test_cache,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ Installation verified successfully!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your IBM Watson API credentials to .env")
        print("3. Run the application (main.py will be created in Phase 6)")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())

# Made with Bob
