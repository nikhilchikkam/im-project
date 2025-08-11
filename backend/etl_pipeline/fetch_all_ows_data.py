#!/usr/bin/env python3
"""
Script to fetch ALL data from OneWorldSync and store in DigitalOcean Spaces
- Fetches ALL products (based on the criteria) in one run
- Automatically handles pagination
- Stores 1000 products per file
- No data duplication
- Clean, simple structure
- Includes lastModifiedDate for tracking product updates
- Filters products by GPC codes from Excel file in Spaces
"""

import os
import json
import time
import boto3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from backend directory
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

def get_spaces_client():
    """Get DigitalOcean Spaces client"""
    spaces_key = os.getenv('SPACES_ACCESS_KEY')
    spaces_secret = os.getenv('SPACES_SECRET_KEY')
    spaces_region = os.getenv('SPACES_REGION', 'sfo3')
    spaces_bucket = os.getenv('SPACES_BUCKET', 'nutrigence-etl')
    
    if not spaces_key or not spaces_secret:
        print("Missing Spaces credentials!")
        return None, None
    
    session = boto3.session.Session()
    client = session.client('s3',
                           region_name=spaces_region,
                           endpoint_url=f'https://{spaces_region}.digitaloceanspaces.com',
                           aws_access_key_id=spaces_key,
                           aws_secret_access_key=spaces_secret)
    
    return client, spaces_bucket

def download_excel_from_spaces(spaces_client, bucket):
    """Download Excel file from Spaces"""
    excel_file_local = "family_class_brick.xlsx"
    excel_file_spaces = "reference/family_class_brick.xlsx"
    
    if os.path.exists(excel_file_local):
        print(f"Using local Excel file: {excel_file_local}")
        return True
    
    try:
        print(f"Downloading Excel file from Spaces: {excel_file_spaces}")
        response = spaces_client.get_object(Bucket=bucket, Key=excel_file_spaces)
        
        with open(excel_file_local, 'wb') as f:
            f.write(response['Body'].read())
        
        print(f"Downloaded Excel file: {excel_file_local}")
        return True
    except Exception as e:
        print(f"Failed to download Excel file: {e}")
        print(f"Please ensure {excel_file_spaces} exists in your Spaces bucket")
        return False

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

def filter_products_by_gpc(products, valid_gpc_codes):
    """Filter products by GPC codes"""
    if not valid_gpc_codes:
        return products  # No filtering if no codes loaded
    
    filtered_products = []
    skipped_count = 0
    found_gpc_codes = set()
    
    for product in products:
        # Extract GPC code from item.globalClassificationCategory.code
        item = product.get("item", {})
        gpc_info = item.get("globalClassificationCategory", {})
        gpc_code = str(gpc_info.get("code", ""))
        
        if gpc_code:
            found_gpc_codes.add(gpc_code)
        
        if gpc_code and gpc_code in valid_gpc_codes:
            filtered_products.append(product)
        else:
            skipped_count += 1
    
    print(f"Filtered {len(products)} products: {len(filtered_products)} valid, {skipped_count} skipped")
    print(f"Found GPC codes in this batch: {sorted(list(found_gpc_codes))}")
    
    return filtered_products

def store_batch(spaces_client, bucket, batch_id, products, criteria, search_after, total_fetched_so_far, batch_number):
    """Store a batch of products in DigitalOcean Spaces"""
    
    # Create the data structure
    batch_data = {
        "batch_id": batch_id,
        "batch_number": batch_number,
        "timestamp": datetime.now().isoformat(),
        "total_products": len(products),
        "criteria": criteria,
        "products": products,
        "search_after": search_after,
        "has_more_data": bool(search_after),
        "total_fetched_so_far": total_fetched_so_far + len(products),
        "is_filtered": True,
        "last_modified_dates": {
            "earliest": None,
            "latest": None,
            "count_with_dates": 0
        }
    }
    
    # Track lastModifiedDate statistics
    last_modified_dates = []
    for product in products:
        last_modified = product.get('lastModifiedDate')
        if last_modified:
            last_modified_dates.append(last_modified)
    
    if last_modified_dates:
        batch_data["last_modified_dates"] = {
            "earliest": min(last_modified_dates),
            "latest": max(last_modified_dates),
            "count_with_dates": len(last_modified_dates)
        }
    
    # Store the batch file
    batch_key = f"filtered_batches/{batch_id}/batch_{batch_number:04d}_products.json"
    spaces_client.put_object(
        Bucket=bucket,
        Key=batch_key,
        Body=json.dumps(batch_data, indent=2).encode('utf-8'),
        ContentType='application/json'
    )
    
    print(f"Batch {batch_number:04d} stored: {batch_key}")
    if batch_data["last_modified_dates"]["count_with_dates"] > 0:
        print(f"LastModifiedDate range: {batch_data['last_modified_dates']['earliest']} to {batch_data['last_modified_dates']['latest']}")
    
    return batch_key

def store_session_metadata(spaces_client, bucket, session_id, total_batches, total_products, start_time, end_time, search_after, total_fetched_raw, total_filtered):
    """Store session metadata"""
    
    session_data = {
        "session_id": session_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "total_batches": total_batches,
        "total_products": total_products,
        "total_fetched_raw": total_fetched_raw,
        "total_filtered": total_filtered,
        "filtering_efficiency": f"{((total_filtered / total_fetched_raw) * 100):.2f}%" if total_fetched_raw > 0 else "0%",
        "is_filtered": True,
        "is_incremental": False,
        "search_after": search_after,
        "notes": "Initial data pull filtered by GPC codes"
    }
    
    session_key = f"sessions/{session_id}/session_info.json"
    spaces_client.put_object(
        Bucket=bucket,
        Key=session_key,
        Body=json.dumps(session_data, indent=2).encode('utf-8'),
        ContentType='application/json'
    )
    
    print(f"Session metadata stored: {session_key}")
    return session_key

def fetch_all_products():
    """Fetch ALL products from OneWorldSync and store in Spaces"""
    
    print("Starting OneWorldSync data fetch (ALL products)...")
    
    # Get clients
    ows_client = get_ows_client()
    if not ows_client:
        print("Failed to create OneWorldSync client")
        return False
    
    spaces_client, bucket = get_spaces_client()
    if not spaces_client:
        print("Failed to create Spaces client")
        return False
    
    # Download Excel file from Spaces
    if not download_excel_from_spaces(spaces_client, bucket):
        print("Failed to get Excel file from Spaces")
        return False
    
    # Load GPC codes
    valid_gpc_codes = load_gpc_codes()
    if not valid_gpc_codes:
        print("No valid GPC codes loaded. Exiting.")
        return False
    
    # Define the fields we need
    fields_include = [
        "gtin", "functionalName", "productDescription", "ingredientStatement",
        "brandName", "productType", "isConsumerUnit", "globalClassificationCategory",
        "lastModifiedDate", "nutrientInformation", "allergenRelatedInformation",
        "foodAndBevDietTypeInfo", "productInformationDetail", "externalFileLink", "dam"
    ]
    
    # Build criteria - always fetch 1000 products per call
    criteria = {
        "targetMarket": "US",
        "fields": {
            "include": fields_include
        },
        "pagination": {
            "limit": 1000,
            "offset": 0
        },
        "sort": [
            {
                "field": "lastModifiedDate",
                "direction": "desc"
            }
        ]
    }
    
    # Initialize variables
    search_after = None
    batch_number = 1
    total_products = 0
    total_fetched_raw = 0
    total_filtered = 0
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    batch_id = f"batch_{session_id}"
    
    start_time = datetime.now()
    
    print(f"Session ID: {session_id}")
    print(f"Start time: {start_time}")
    print(f"Valid GPC codes: {len(valid_gpc_codes)}")
    
    try:
        while True:
            # Add searchAfter if we have one
            if search_after:
                criteria["searchAfter"] = search_after
                print(f"Fetching batch {batch_number:04d} (1000 products)...")
            else:
                print(f"Fetching batch {batch_number:04d} (1000 products)...")
            
            # Make API call
            print(f"Making API call to OneWorldSync...")
            response = ows_client.fetch_products(criteria)
            
            # Extract products from response
            if isinstance(response, dict):
                products = response.get('data', response.get('items', response.get('products', [])))
            else:
                products = response if isinstance(response, list) else []
            
            print(f"Fetched {len(products)} products from OneWorldSync")
            total_fetched_raw += len(products)
            
            if not products:
                print("No products found! Stopping.")
                break
            
            # Filter products by GPC codes
            filtered_products = filter_products_by_gpc(products, valid_gpc_codes)
            total_filtered += len(filtered_products)
            
            # Store batch if we have filtered products
            if filtered_products:
                store_batch(
                    spaces_client, bucket, batch_id, filtered_products,
                    criteria, search_after, total_products, batch_number
                )
                total_products += len(filtered_products)
                batch_number += 1
            else:
                print(f"No valid products in batch {batch_number:04d} (all filtered out)")
            
            # Check for more data
            search_after = response.get('searchAfter')
            if not search_after:
                print("No more data available (reached end)")
                break
            
            print(f"Progress: {total_products:,} products stored so far")
            print(f"Raw fetched: {total_fetched_raw:,}, Filtered: {total_filtered:,}")
            print(f"Next searchAfter: {search_after[:50]}...")
            
            # Small delay to be respectful to the API
            time.sleep(0.1)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\nSession completed!")
        print(f"Total products stored: {total_products:,}")
        print(f"Total products fetched (raw): {total_fetched_raw:,}")
        print(f"Total products filtered: {total_filtered:,}")
        print(f"Filtering efficiency: {((total_filtered / total_fetched_raw) * 100):.2f}%" if total_fetched_raw > 0 else "0%")
        print(f"Total batches created: {batch_number - 1}")
        print(f"Duration: {duration}")
        if total_products > 0:
            print(f"Average speed: {total_products / duration.total_seconds():.1f} products/second")
        
        # Store session metadata
        session_key = store_session_metadata(
            spaces_client, bucket, session_id, batch_number - 1,
            total_products, start_time, end_time, search_after, total_fetched_raw, total_filtered
        )
        
        # Print final summary
        print(f"\nFinal Summary:")
        print(f"  Session ID: {session_id}")
        print(f"  Total products stored: {total_products:,}")
        print(f"  Total products fetched (raw): {total_fetched_raw:,}")
        print(f"  Total products filtered: {total_filtered:,}")
        print(f"  Filtering efficiency: {((total_filtered / total_fetched_raw) * 100):.2f}%" if total_fetched_raw > 0 else "0%")
        print(f"  Total batches: {batch_number - 1}")
        print(f"  Duration: {duration}")
        print(f"  Session metadata: {session_key}")
        print(f"  Batch files: filtered_batches/{batch_id}/")
        print(f"  Mode: Initial data pull (filtered by GPC codes)")
        
        return True
        
    except Exception as e:
        print(f"Error during fetch: {e}")
        
        # Store error metadata
        try:
            error_data = {
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "total_products_fetched": total_products,
                "total_fetched_raw": total_fetched_raw,
                "total_filtered": total_filtered,
                "batch_number": batch_number
            }
            
            error_key = f"sessions/{session_id}/error_info.json"
            spaces_client.put_object(
                Bucket=bucket,
                Key=error_key,
                Body=json.dumps(error_data, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
            print(f"Error metadata stored: {error_key}")
        except:
            print("Failed to store error metadata")
        
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch filtered OneWorldSync data (initial pull)')
    parser.add_argument('--estimate', action='store_true',
                       help='Estimate total products and fetch duration')
    
    args = parser.parse_args()
    
    # Get OneWorldSync client for estimation
    if args.estimate:
        ows_client = get_ows_client()
        if ows_client:
            print("OneWorldSync client created successfully")
        else:
            print("OneWorldSync client failed")
        
        spaces_client, bucket = get_spaces_client()
        if spaces_client:
            print("DigitalOcean Spaces client created successfully")
            print(f"  Bucket: {bucket}")
        else:
            print("DigitalOcean Spaces client failed")
        
        return
    
    # Fetch filtered data
    success = fetch_all_products()
    
    if success:
        print("\nAll data fetch and storage completed successfully!")
    else:
        print("\nData fetch and storage failed!")
        return 1

if __name__ == "__main__":
    main() 