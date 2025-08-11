#!/usr/bin/env python3
"""
Test script for the ETL Orchestrator
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        from etl_orchestrator import ETLOrchestrator
        from loaders.product_loader import ProductLoader
        from loaders.allergen_loader import AllergenLoader
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_loader_creation():
    """Test if loaders can be created"""
    try:
        from loaders.product_loader import ProductLoader
        from loaders.allergen_loader import AllergenLoader
        from loaders.nutrition_loader import NutritionLoader
        
        # Use a dummy database URL for testing
        test_db_url = "postgresql://test:test@localhost:5432/test"
        
        product_loader = ProductLoader(test_db_url)
        allergen_loader = AllergenLoader(test_db_url)
        nutrition_loader = NutritionLoader(test_db_url)
        
        print("✅ All loaders created successfully!")
        print(f"  - ProductLoader: {product_loader.name}")
        print(f"  - AllergenLoader: {allergen_loader.name}")
        print(f"  - NutritionLoader: {nutrition_loader.name}")
        return True
    except Exception as e:
        print(f"❌ Loader creation failed: {e}")
        return False

def test_orchestrator_creation():
    """Test if orchestrator can be created"""
    try:
        from etl_orchestrator import ETLOrchestrator
        
        orchestrator = ETLOrchestrator()
        print("✅ ETL Orchestrator created successfully!")
        return True
    except Exception as e:
        print(f"❌ Orchestrator creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing ETL Orchestrator...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Loader Creation Test", test_loader_creation),
        ("Orchestrator Creation Test", test_orchestrator_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ETL Orchestrator is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 