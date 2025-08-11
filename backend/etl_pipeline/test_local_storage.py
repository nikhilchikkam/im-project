#!/usr/bin/env python3
"""
Test script to demonstrate local storage functionality
"""

import os
import json
from etl_orchestrator import ETLOrchestrator

def test_local_storage():
    """Test local storage functionality"""
    print("🧪 Testing Local Storage Functionality...")
    
    # Create orchestrator
    orchestrator = ETLOrchestrator()
    
    # Check initial state
    print("\n📁 Initial Local Storage State:")
    storage_info = orchestrator.get_local_storage_info()
    print(f"  Exists: {storage_info['exists']}")
    print(f"  Size: {storage_info['size_mb']} MB")
    print(f"  Files: {storage_info['file_count']}")
    
    # Create a test batch file locally
    print("\n📝 Creating Test Batch File...")
    test_batch_data = [
        {
            "item": {
                "gtin": "123456789",
                "functionalName": [{"value": "Test Product"}],
                "globalClassificationCategory": {"code": "10000001"}
            }
        }
    ]
    
    # Save test batch locally
    test_batch_key = "test_batch.json"
    orchestrator._save_batch_locally(test_batch_key, test_batch_data)
    
    # Check storage after creating file
    print("\n📁 Local Storage After Creating Test File:")
    storage_info = orchestrator.get_local_storage_info()
    print(f"  Exists: {storage_info['exists']}")
    print(f"  Size: {storage_info['size_mb']} MB")
    print(f"  Files: {storage_info['file_count']}")
    
    # List local files
    if storage_info['exists']:
        print("\n📋 Local Files:")
        local_dir = "downloaded_batches"
        for filename in os.listdir(local_dir):
            filepath = os.path.join(local_dir, filename)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  - {filename} ({size_kb:.1f} KB)")
    
    # Test loading from local file
    print("\n🔄 Testing Local File Loading...")
    local_file = orchestrator._get_local_batch_path(test_batch_key)
    if os.path.exists(local_file):
        with open(local_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"  ✅ Successfully loaded {len(loaded_data)} items from local file")
        print(f"  📄 File path: {local_file}")
    
    print("\n🎉 Local Storage Test Completed!")

if __name__ == "__main__":
    test_local_storage() 