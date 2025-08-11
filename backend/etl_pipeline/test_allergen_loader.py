#!/usr/bin/env python3
"""
Test script for the updated AllergenLoader
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_allergen_loader():
    """Test the updated AllergenLoader"""
    try:
        from loaders.allergen_loader import AllergenLoader
        
        print("🧪 Testing Updated AllergenLoader...")
        print("=" * 50)
        
        # Create loader (this will trigger the download from Spaces)
        print("Creating AllergenLoader...")
        loader = AllergenLoader("dummy_database_url")
        
        print(f"✅ AllergenLoader created successfully!")
        print(f"   - Name: {loader.name}")
        print(f"   - Table: {loader.table_name}")
        print(f"   - Allergen mappings loaded: {len(loader.allergen_type_map)}")
        
        if loader.allergen_type_map:
            print("   - Sample mappings:")
            for i, (code, desc) in enumerate(list(loader.allergen_type_map.items())[:3]):
                print(f"     {code}: {desc}")
        else:
            print("   - Warning: No allergen mappings loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    if test_allergen_loader():
        print("\n🎉 AllergenLoader test passed!")
        return 0
    else:
        print("\n❌ AllergenLoader test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 