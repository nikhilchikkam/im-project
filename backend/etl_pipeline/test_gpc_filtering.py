#!/usr/bin/env python3
"""
Quick test to identify GPC filtering issue
"""

import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

def test_excel_loading():
    """Test Excel file loading"""
    excel_file = "family_class_brick.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
    
    try:
        df = pd.read_excel(excel_file)
        print(f"Excel columns: {list(df.columns)}")
        print(f"Excel shape: {df.shape}")
        
        # Check BrickCode column
        if "BrickCode" in df.columns:
            brick_codes = df["BrickCode"].dropna().astype(str)
            print(f"BrickCode count: {len(brick_codes)}")
            print(f"First 5 BrickCode values: {list(brick_codes.head(5))}")
            print(f"BrickCode types: {brick_codes.dtype}")
            
            # Check for common issues
            print(f"Empty strings: {(brick_codes == '').sum()}")
            print(f"Values with spaces: {(brick_codes.str.contains(' ')).sum()}")
            print(f"Values with leading/trailing spaces: {(brick_codes != brick_codes.str.strip()).sum()}")
            
            # Show some examples
            print(f"\nSample BrickCode values:")
            for i, code in enumerate(brick_codes.head(10)):
                print(f"  {i+1}. '{code}' (length: {len(code)})")
                
        else:
            print("BrickCode column not found!")
            print(f"Available columns: {list(df.columns)}")
            
    except Exception as e:
        print(f"Error reading Excel: {e}")

def test_gpc_extraction():
    """Test GPC code extraction from sample product"""
    
    # Sample product structure (what we expect from OneWorldSync)
    sample_product = {
        "gtin": "1234567890123",
        "functionalName": [{"value": "Sample Product"}],
        "globalClassificationCategory": {
            "code": "10000000",
            "title": "Food and Beverage"
        }
    }
    
    # Extract GPC code
    gpc_info = sample_product.get("globalClassificationCategory", {})
    gpc_code = str(gpc_info.get("code", ""))
    
    print(f"Sample product GPC extraction:")
    print(f"  Raw GPC info: {gpc_info}")
    print(f"  Extracted GPC code: '{gpc_code}' (type: {type(gpc_code)})")
    
    # Test with different formats
    test_codes = ["10000000", "10000000.0", " 10000000 ", "10000000.0", 10000000]
    
    print(f"\nTesting different GPC code formats:")
    for test_code in test_codes:
        clean_code = str(test_code).strip()
        print(f"  '{test_code}' -> '{clean_code}' (type: {type(clean_code)})")

def main():
    """Main function"""
    print("GPC Filtering Test")
    print("=" * 30)
    
    test_excel_loading()
    print()
    test_gpc_extraction()
    
    print(f"\nTest complete!")

if __name__ == "__main__":
    main() 