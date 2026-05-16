#!/usr/bin/env python3
"""
Quick test script to verify UI components are working.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all UI components can be imported."""
    print("Testing UI component imports...")
    
    try:
        from ui.components.loading_screen import LoadingScreen, LoadingStage
        print("✓ LoadingScreen imported successfully")
        
        from ui.app import CodebaseAnalyzerApp, run_app
        print("✓ CodebaseAnalyzerApp imported successfully")
        
        from core.orchestrator import AnalysisOrchestrator
        print("✓ AnalysisOrchestrator imported successfully")
        
        from utils.config import Config
        print("✓ Config imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_loading_stages():
    """Test LoadingStage enum."""
    print("\nTesting LoadingStage enum...")
    
    try:
        from ui.components.loading_screen import LoadingStage
        
        stages = [
            LoadingStage.SCANNING,
            LoadingStage.ANALYZING,
            LoadingStage.AI_PROCESSING,
            LoadingStage.GROUPING,
            LoadingStage.DETECTING,
            LoadingStage.FINALIZING,
            LoadingStage.COMPLETE,
        ]
        
        print(f"✓ Found {len(stages)} loading stages:")
        for stage in stages:
            print(f"  - {stage.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from utils.config import Config
        
        config = Config()
        print(f"✓ Config loaded successfully")
        print(f"  - App name: {config.app_name}")
        print(f"  - Cache enabled: {config.cache_enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Codebase Analyzer UI - Component Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Loading Stages", test_loading_stages()))
    results.append(("Configuration", test_config()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! UI is ready to run.")
        print("\nTo start the application, run:")
        print("  python run_ui.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
