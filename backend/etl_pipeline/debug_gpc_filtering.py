#!/usr/bin/env python3
"""
Debug script to analyze GPC code filtering issues
- Loads GPC codes from Excel
- Analyzes sample products from OneWorldSync
- Shows what GPC codes are being found vs expected
"""

import os
import json
import pandas as pd
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

def load_gpc_codes():
    """Load valid GPC codes from Excel file"""
    excel_file = "family_class_brick.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return set()
    
    try:
        df = pd.read_excel(excel_file)
        codes = set(str(code).strip() for code in df["BrickCode"].dropna().astype(str))
        print(f"Loaded {len(codes)} valid GPC codes from Excel file")
        return codes
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return set()

def analyze_sample_products():
    """Analyze sample products to understand GPC code structure"""
    
    # Get OneWorldSync client
    ows_client = get_ows_client()
    if not ows_client:
        print("Failed to create OneWorldSync client")
        return
    
    # Load GPC codes
    valid_gpc_codes = load_gpc_codes()
    print(f"\nValid GPC codes loaded: {len(valid_gpc_codes)}")
    
    # Show first 10 valid GPC codes
    print(f"First 10 valid GPC codes: {list(valid_gpc_codes)[:10]}")
    
    # Fetch sample products
    print(f"\nFetching sample products from OneWorldSync...")
    
    criteria = {
        "targetMarket": "US",
        "fields": {
            "include": ["gtin", "functionalName", "globalClassificationCategory"]
        },
        "pagination": {
            "limit": 100,
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
        
        # Analyze GPC codes in products
        found_gpc_codes = set()
        product_gpc_analysis = []
        
        for i, product in enumerate(products[:20]):  # Analyze first 20 products
            gpc_info = product.get("globalClassificationCategory", {})
            gpc_code = str(gpc_info.get("code", ""))
            gpc_title = gpc_info.get("title", "")
            
            found_gpc_codes.add(gpc_code)
            
            is_valid = gpc_code in valid_gpc_codes
            
            product_gpc_analysis.append({
                "product_index": i,
                "gtin": product.get("gtin", ""),
                "name": product.get("functionalName", [{}])[0].get("value", "") if product.get("functionalName") else "",
                "gpc_code": gpc_code,
                "gpc_title": gpc_title,
                "is_valid": is_valid
            })
        
        print(f"\nFound {len(found_gpc_codes)} unique GPC codes in sample products")
        print(f"GPC codes found: {sorted(list(found_gpc_codes))}")
        
        # Show product analysis
        print(f"\nProduct GPC Analysis (first 20 products):")
        print("-" * 80)
        for analysis in product_gpc_analysis:
            status = "VALID" if analysis["is_valid"] else "INVALID"
            print(f"{analysis['product_index']:2d}. {analysis['gtin']} | {analysis['gpc_code']} | {analysis['gpc_title'][:50]} | {status}")
        
        # Check overlap
        overlap = found_gpc_codes.intersection(valid_gpc_codes)
        print(f"\nOverlap Analysis:")
        print(f"  Valid GPC codes: {len(valid_gpc_codes)}")
        print(f"  Found GPC codes: {len(found_gpc_codes)}")
        print(f"  Overlap: {len(overlap)}")
        print(f"  Overlap percentage: {(len(overlap) / len(found_gpc_codes) * 100):.2f}%" if found_gpc_codes else "0%")
        
        if overlap:
            print(f"  Overlapping codes: {sorted(list(overlap))}")
        else:
            print(f"  No overlapping codes found!")
            print(f"  This explains why 0 products are being stored.")
        
        # Show some examples of valid codes that weren't found
        not_found = valid_gpc_codes - found_gpc_codes
        if not_found:
            print(f"\nValid codes not found in sample: {sorted(list(not_found))[:10]}...")
        
        # Show some examples of found codes that aren't valid
        invalid_found = found_gpc_codes - valid_gpc_codes
        if invalid_found:
            print(f"\nFound codes not in valid list: {sorted(list(invalid_found))[:10]}...")
        
    except Exception as e:
        print(f"Error fetching sample products: {e}")

def check_excel_structure():
    """Check the structure of the Excel file"""
    excel_file = "family_class_brick.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
    
    try:
        df = pd.read_excel(excel_file)
        print(f"\nExcel file structure:")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Rows: {len(df)}")
        print(f"  BrickCode column sample values:")
        
        brick_codes = df["BrickCode"].dropna().astype(str)
        print(f"  First 10 BrickCode values: {list(brick_codes.head(10))}")
        print(f"  BrickCode data types: {brick_codes.dtype}")
        
        # Check for any formatting issues
        print(f"\nBrickCode analysis:")
        print(f"  Total BrickCode values: {len(brick_codes)}")
        print(f"  Unique BrickCode values: {len(brick_codes.unique())}")
        print(f"  Empty strings: {(brick_codes == '').sum()}")
        print(f"  Values with spaces: {(brick_codes.str.contains(' ')).sum()}")
        
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")

def main():
    """Main function"""
    print("GPC Code Filtering Debug Analysis")
    print("=" * 50)
    
    # Check Excel structure
    check_excel_structure()
    
    # Analyze sample products
    analyze_sample_products()
    
    print(f"\nDebug analysis complete!")
    print(f"Check the output above to understand why filtering is failing.")

if __name__ == "__main__":
    main() 