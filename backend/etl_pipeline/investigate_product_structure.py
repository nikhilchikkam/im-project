#!/usr/bin/env python3
"""
Investigate OneWorldSync product structure to understand GPC code issue
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

def get_ows_client():
    """Get OneWorldSync client"""
    try:
        from oneworldsync import Content1Client
        return Content1Client()
    except ImportError:
        print("OneWorldSync library not installed!")
        print("Please install: pip install oneworldsync")
        return None

def investigate_product_structure():
    """Investigate the actual structure of OneWorldSync products"""
    
    ows_client = get_ows_client()
    if not ows_client:
        print("Failed to create OneWorldSync client")
        return
    
    print("Fetching sample products to investigate structure...")
    
    # Fetch with minimal fields first
    criteria = {
        "targetMarket": "US",
        "fields": {
            "include": ["gtin", "functionalName"]
        },
        "pagination": {
            "limit": 5,
            "offset": 0
        }
    }
    
    try:
        response = ows_client.fetch_products(criteria)
        
        if isinstance(response, dict):
            products = response.get('data', response.get('items', response.get('products', [])))
        else:
            products = response if isinstance(response, list) else []
        
        print(f"Fetched {len(products)} sample products")
        
        if products:
            print(f"\nSample product structure:")
            print(json.dumps(products[0], indent=2))
            
            # Check what fields are actually available
            print(f"\nAvailable fields in first product:")
            for key, value in products[0].items():
                print(f"  {key}: {type(value).__name__} = {value}")
        
    except Exception as e:
        print(f"Error fetching products: {e}")

def test_different_gpc_fields():
    """Test different possible GPC field names"""
    
    ows_client = get_ows_client()
    if not ows_client:
        return
    
    print("\nTesting different GPC field names...")
    
    # Test different possible field names
    possible_fields = [
        "globalClassificationCategory",
        "gpcCategory", 
        "classificationCategory",
        "productCategory",
        "category",
        "gpc"
    ]
    
    criteria = {
        "targetMarket": "US",
        "fields": {
            "include": ["gtin", "functionalName"] + possible_fields
        },
        "pagination": {
            "limit": 3,
            "offset": 0
        }
    }
    
    try:
        response = ows_client.fetch_products(criteria)
        
        if isinstance(response, dict):
            products = response.get('data', response.get('items', response.get('products', [])))
        else:
            products = response if isinstance(response, list) else []
        
        if products:
            product = products[0]
            print(f"\nTesting GPC fields in first product:")
            
            for field in possible_fields:
                value = product.get(field, "NOT_FOUND")
                print(f"  {field}: {value}")
                
                if isinstance(value, dict):
                    print(f"    Keys: {list(value.keys())}")
                    if "code" in value:
                        print(f"    Code: {value['code']}")
                    if "title" in value:
                        print(f"    Title: {value['title']}")
        
    except Exception as e:
        print(f"Error testing GPC fields: {e}")

def check_api_documentation():
    """Check what fields are available in the API"""
    
    ows_client = get_ows_client()
    if not ows_client:
        return
    
    print("\nChecking API field availability...")
    
    # Try to get product count first
    try:
        count_response = ows_client.count_products({})
        print(f"Product count response: {count_response}")
    except Exception as e:
        print(f"Error getting product count: {e}")
    
    # Try different field combinations
    test_criteria = [
        {"targetMarket": "US", "fields": {"include": ["gtin"]}},
        {"targetMarket": "US", "fields": {"include": ["gtin", "globalClassificationCategory"]}},
        {"targetMarket": "US", "fields": {"include": ["gtin", "gpcCategory"]}},
    ]
    
    for i, criteria in enumerate(test_criteria):
        try:
            print(f"\nTest {i+1}: {criteria['fields']['include']}")
            response = ows_client.fetch_products(criteria)
            
            if isinstance(response, dict):
                products = response.get('data', response.get('items', response.get('products', [])))
            else:
                products = response if isinstance(response, list) else []
            
            if products:
                print(f"  Success: {len(products)} products")
                print(f"  First product keys: {list(products[0].keys())}")
            else:
                print(f"  No products returned")
                
        except Exception as e:
            print(f"  Error: {e}")

def main():
    """Main function"""
    print("OneWorldSync Product Structure Investigation")
    print("=" * 50)
    
    investigate_product_structure()
    test_different_gpc_fields()
    check_api_documentation()
    
    print(f"\nInvestigation complete!")
    print(f"Check the output above to understand the product structure.")

if __name__ == "__main__":
    main() 