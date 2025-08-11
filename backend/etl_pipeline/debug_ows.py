#!/usr/bin/env python3
"""
Debug script for OneWorldSync API connection issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment variables...")
    
    # Check for common OneWorldSync environment variables
    ows_vars = [
        'ONEWORLDSYNC_API_KEY',
        'ONEWORLDSYNC_SECRET',
        'ONEWORLDSYNC_USERNAME',
        'ONEWORLDSYNC_PASSWORD',
        'OWS_API_KEY',
        'OWS_SECRET',
        'OWS_USERNAME',
        'OWS_PASSWORD'
    ]
    
    found_vars = []
    for var in ows_vars:
        value = os.getenv(var)
        if value:
            found_vars.append(var)
            print(f"  ✅ {var}: {'*' * len(value)}")
        else:
            print(f"  ❌ {var}: Not set")
    
    if not found_vars:
        print("\n⚠️  No OneWorldSync credentials found!")
        print("The OneWorldSync client may be using a configuration file or different environment variables.")
    
    return found_vars

def test_ows_import():
    """Test OneWorldSync library import"""
    print("\n🔍 Testing OneWorldSync library import...")
    
    try:
        from oneworldsync import Content1Client
        print("✅ OneWorldSync library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import OneWorldSync: {e}")
        print("Please install: pip install oneworldsync")
        return False

def test_ows_client_creation():
    """Test OneWorldSync client creation"""
    print("\n🔍 Testing OneWorldSync client creation...")
    
    try:
        from oneworldsync import Content1Client
        
        # Try to create client
        client = Content1Client()
        print("✅ OneWorldSync client created successfully")
        
        # Try to get client info
        print("🔍 Checking client configuration...")
        
        # Check if client has any configuration attributes
        client_attrs = [attr for attr in dir(client) if not attr.startswith('_')]
        print(f"  Client attributes: {len(client_attrs)} found")
        
        # Look for configuration-related attributes
        config_attrs = [attr for attr in client_attrs if 'config' in attr.lower() or 'auth' in attr.lower()]
        if config_attrs:
            print(f"  Configuration attributes: {config_attrs}")
        
        return client
        
    except Exception as e:
        print(f"❌ Failed to create OneWorldSync client: {e}")
        return None

def test_ows_api_call(client):
    """Test a simple OneWorldSync API call"""
    print("\n🔍 Testing OneWorldSync API call...")
    
    if not client:
        print("❌ No client available for testing")
        return False
    
    try:
        # Try a simple count query
        print("🔄 Testing count_products()...")
        
        criteria = {
            "targetMarket": "US",
            "pullHierarchy": False
        }
        
        count = client.count_products(criteria)
        print(f"✅ API call successful! Total products: {count}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
        # Check if it's an authentication error
        if "auth" in str(e).lower() or "unauthorized" in str(e).lower():
            print("\n🔍 This appears to be an authentication issue.")
            print("Please check your OneWorldSync credentials.")
        
        return False

def check_config_files():
    """Check for configuration files"""
    print("\n🔍 Checking for configuration files...")
    
    config_files = [
        '.oneworldsync',
        '.oneworldsync.json',
        '.oneworldsync.yaml',
        '.oneworldsync.yml',
        'oneworldsync.json',
        'oneworldsync.yaml',
        'oneworldsync.yml',
        'config.json',
        'config.yaml',
        'config.yml'
    ]
    
    found_files = []
    for file in config_files:
        if os.path.exists(file):
            found_files.append(file)
            print(f"  ✅ Found: {file}")
        else:
            print(f"  ❌ Not found: {file}")
    
    return found_files

def main():
    """Main debug function"""
    print("🐛 OneWorldSync API Debug Tool")
    print("=" * 40)
    
    # Check environment variables
    env_vars = check_environment()
    
    # Check configuration files
    config_files = check_config_files()
    
    # Test library import
    if not test_ows_import():
        return
    
    # Test client creation
    client = test_ows_client_creation()
    
    # Test API call
    if client:
        test_ows_api_call(client)
    
    # Summary
    print("\n📊 Debug Summary:")
    print(f"  Environment variables found: {len(env_vars)}")
    print(f"  Configuration files found: {len(config_files)}")
    print(f"  Library import: {'✅' if test_ows_import() else '❌'}")
    print(f"  Client creation: {'✅' if client else '❌'}")
    
    if not env_vars and not config_files:
        print("\n💡 Recommendations:")
        print("1. Check OneWorldSync documentation for required credentials")
        print("2. Set up environment variables or configuration file")
        print("3. Contact OneWorldSync support if you need help with authentication")

if __name__ == "__main__":
    main() 