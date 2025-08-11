#!/usr/bin/env python3
"""
Simple script to fetch data from OneWorldSync and store in DigitalOcean Spaces
"""

import os
import json
import time
import boto3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from backend directory
load_dotenv('../.env')
load_dotenv('.env')  # Also try local .env if it exists

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

def get_latest_search_after(spaces_client, bucket):
    """Get the latest searchAfter value for continuing pagination"""
    try:
        # List all search_after files
        response = spaces_client.list_objects_v2(
            Bucket=bucket,
            Prefix='search_after/'
        )
        
        if 'Contents' not in response:
            return None
        
        # Get the most recent searchAfter file
        latest_file = None
        latest_time = None
        
        for obj in response['Contents']:
            if obj['Key'].endswith('pagination_state.json'):
                if latest_time is None or obj['LastModified'] > latest_time:
                    latest_time = obj['LastModified']
                    latest_file = obj['Key']
        
        if latest_file:
            # Download and read the latest searchAfter
            response = spaces_client.get_object(Bucket=bucket, Key=latest_file)
            data = json.loads(response['Body'].read().decode('utf-8'))
            
            if data.get('status') == 'active' and data.get('search_after'):
                print(f"Found latest searchAfter from: {latest_file}")
                return data
            else:
                print("Latest searchAfter indicates completed pagination")
                return None
        else:
            return None
            
    except Exception as e:
        print(f"Error getting latest searchAfter: {e}")
        return None

def store_search_after(spaces_client, bucket, batch_id, search_after_value, criteria, total_fetched):
    """Store searchAfter value for a specific batch"""
    search_after_data = {
        "batch_id": batch_id,
        "timestamp": datetime.now().isoformat(),
        "search_after": search_after_value,
        "criteria": criteria,
        "total_fetched_so_far": total_fetched,
        "status": "active" if search_after_value else "completed"
    }
    
    # Store in search_after directory
    key = f"search_after/{batch_id}/pagination_state.json"
    
    try:
        spaces_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(search_after_data, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        print(f"SearchAfter stored: {key}")
        return True
    except Exception as e:
        print(f"Failed to store searchAfter: {e}")
        return False

def fetch_and_store_products(limit=100, continue_from_last=False):
    """Fetch products from OneWorldSync and store in Spaces"""
    
    print("Starting OneWorldSync data fetch...")
    
    # Get clients
    ows_client = get_ows_client()
    spaces_client, bucket = get_spaces_client()
    
    if not ows_client or not spaces_client:
        return False
    
    # Check if we should continue from last position
    search_after = None
    total_fetched_so_far = 0
    
    if continue_from_last:
        latest_data = get_latest_search_after(spaces_client, bucket)
        if latest_data:
            search_after = latest_data.get('search_after')
            total_fetched_so_far = latest_data.get('total_fetched_so_far', 0)
            print(f"Continuing from: {total_fetched_so_far} products already fetched")
            print(f"Using searchAfter: {search_after[:50]}..." if search_after else "No searchAfter")
        else:
            print("No previous searchAfter found, starting fresh")
    
    try:
        # Define the fields we need (optimized list from our analysis)
        fields_include = [
            "gtin", "functionalName", "productDescription", "ingredientStatement",
            "brandName", "productType", "isConsumerUnit", "globalClassificationCategory",
            "lastModifiedDate", "nutrientInformation", "allergenRelatedInformation",
            "foodAndBevDietTypeInfo", "productInformationDetail", "externalFileLink", "dam"
        ]
        
        # Build criteria
        criteria = {
            "fields": {
                "include": fields_include
            },
            "pagination": {
                "limit": limit,
                "offset": 0
            },
            "sort": [
                {
                    "field": "lastModifiedDate",
                    "direction": "desc"
                }
            ]
        }
        
        # Add searchAfter if we have one
        if search_after:
            criteria["searchAfter"] = search_after
            print(f"Fetching next {limit} products from OneWorldSync...")
        else:
            print(f"Fetching up to {limit} products from OneWorldSync...")
        
        print("Making API call to OneWorldSync...")
        response = ows_client.fetch_products(criteria)
        
        print(f"API Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        # Check different possible response structures
        products = []
        if isinstance(response, dict):
            products = response.get('data', response.get('items', response.get('products', [])))
        
        print(f"Fetched {len(products)} products from OneWorldSync")
        
        if not products:
            print("No products found!")
            print("Full API response:")
            print(json.dumps(response, indent=2)[:1000] + "..." if len(str(response)) > 1000 else json.dumps(response, indent=2))
            return False
        
        # Create timestamp for this batch
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if continue_from_last and search_after:
            batch_id = f"batch_{timestamp}_continued"
        else:
            batch_id = f"batch_{timestamp}"
        
        # Store raw data in Spaces
        print("Storing raw data in DigitalOcean Spaces...")
        
        # Store the complete response
        raw_data = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "total_products": len(products),
            "criteria": criteria,
            "products": products,
            "api_response": response,  # Store full API response including searchAfter
            "search_after": response.get('searchAfter'),  # Extract searchAfter for easy access
            "has_more_data": bool(response.get('searchAfter')),  # Flag indicating if more data is available
            "previous_batch_total": total_fetched_so_far if continue_from_last else 0,
            "total_fetched_including_previous": total_fetched_so_far + len(products) if continue_from_last else len(products)
        }
        
        raw_key = f"raw_data/{batch_id}/products.json"
        spaces_client.put_object(
            Bucket=bucket,
            Key=raw_key,
            Body=json.dumps(raw_data, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"Raw data stored: {raw_key}")
        
        # Store individual product files for easier access
        print("Storing individual product files...")
        
        for i, product in enumerate(products):
            gtin = product.get('gtin', f'unknown_{i}')
            product_key = f"products/{batch_id}/{gtin}.json"
            
            spaces_client.put_object(
                Bucket=bucket,
                Key=product_key,
                Body=json.dumps(product, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
        
        print(f"Individual product files stored: products/{batch_id}/")
        
        # Store batch metadata
        metadata = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "total_products": len(products),
            "files_created": [
                raw_key,
                f"products/{batch_id}/ (individual files)"
            ],
            "source": "OneWorldSync API" + (" (continued)" if continue_from_last and search_after else ""),
            "fields_included": fields_include,
            "search_after": response.get('searchAfter'),  # Store searchAfter for pagination
            "has_more_data": bool(response.get('searchAfter')),  # Flag for more data
            "api_response_keys": list(response.keys()) if isinstance(response, dict) else [],
            "previous_batch_total": total_fetched_so_far if continue_from_last else 0,
            "total_fetched_including_previous": total_fetched_so_far + len(products) if continue_from_last else len(products)
        }
        
        metadata_key = f"metadata/{batch_id}/batch_info.json"
        spaces_client.put_object(
            Bucket=bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"Batch metadata stored: {metadata_key}")
        
        # Store searchAfter for pagination
        if response.get('searchAfter'):
            store_search_after(
                spaces_client, bucket, batch_id,
                response.get('searchAfter'),
                criteria,
                total_fetched_so_far + len(products)
            )
            print(f"SearchAfter stored for pagination: {response.get('searchAfter')[:50]}...")
        else:
            print("ℹNo searchAfter value (end of data or single batch)")
        
        # Print summary
        if continue_from_last and search_after:
            print("\nContinuation Summary:")
            print(f"  Additional products fetched: {len(products)}")
            print(f"  Previous total: {total_fetched_so_far}")
            print(f"  New total: {total_fetched_so_far + len(products)}")
        else:
            print("\nFetch Summary:")
            print(f"  Products fetched: {len(products)}")
        
        print(f"  Batch ID: {batch_id}")
        print(f"  Raw data: {raw_key}")
        print(f"  Individual files: products/{batch_id}/")
        print(f"  Metadata: {metadata_key}")
        print(f"  SearchAfter stored: {'Yes' if response.get('searchAfter') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"Error during fetch: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch OneWorldSync data to DigitalOcean Spaces')
    parser.add_argument('--limit', type=int, default=100, help='Number of products to fetch (default: 100)')
    parser.add_argument('--test', action='store_true', help='Test connections only')
    parser.add_argument('--continue', dest='continue_from_last', action='store_true', help='Continue from last searchAfter position')
    parser.add_argument('--list-search-after', action='store_true', help='List all stored searchAfter values')
    
    args = parser.parse_args()
    
    if args.test:
        print("Testing connections...")
        
        # Test OneWorldSync
        ows_client = get_ows_client()
        if ows_client:
            print("OneWorldSync client created successfully")
        else:
            print("OneWorldSync client failed")
        
        # Test Spaces
        spaces_client, bucket = get_spaces_client()
        if spaces_client:
            print("DigitalOcean Spaces client created successfully")
            print(f"  Bucket: {bucket}")
        else:
            print("DigitalOcean Spaces client failed")
        
        return
    
    if args.list_search_after:
        print("📋 Stored SearchAfter Values:")
        print("=" * 50)
        
        spaces_client, bucket = get_spaces_client()
        if not spaces_client:
            return 1
        
        try:
            response = spaces_client.list_objects_v2(
                Bucket=bucket,
                Prefix='search_after/'
            )
            
            if 'Contents' not in response:
                print("No searchAfter files found")
                return
            
            for obj in response['Contents']:
                if obj['Key'].endswith('pagination_state.json'):
                    try:
                        response = spaces_client.get_object(Bucket=bucket, Key=obj['Key'])
                        data = json.loads(response['Body'].read().decode('utf-8'))
                        
                        print(f"{obj['Key']}")
                        print(f"   Batch ID: {data.get('batch_id')}")
                        print(f"   Timestamp: {data.get('timestamp')}")
                        print(f"   Status: {data.get('status')}")
                        print(f"   Total Fetched: {data.get('total_fetched_so_far')}")
                        print(f"   SearchAfter: {str(data.get('search_after'))[:50]}..." if data.get('search_after') else "   SearchAfter: None")
                        print()
                        
                    except Exception as e:
                        print(f"Error reading {obj['Key']}: {e}")
                        print()
        
        except Exception as e:
            print(f"Error listing searchAfter files: {e}")
        
        return
    
    # Fetch and store data
    success = fetch_and_store_products(args.limit, args.continue_from_last)
    
    if success:
        print("\nData fetch and storage completed successfully!")
    else:
        print("\nData fetch and storage failed!")
        return 1

if __name__ == "__main__":
    main() 