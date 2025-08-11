#!/usr/bin/env python3
"""
Script to clean existing data from DigitalOcean Spaces
- Deletes all existing batch files
- Deletes all existing session metadata
- Prepares for fresh filtered data download
"""

import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

# DigitalOcean Spaces configuration
SPACES_ACCESS_KEY = os.getenv('SPACES_ACCESS_KEY')
SPACES_SECRET_KEY = os.getenv('SPACES_SECRET_KEY')
SPACES_REGION = os.getenv('SPACES_REGION', 'sfo3')
SPACES_BUCKET = os.getenv('SPACES_BUCKET', 'nutrigence-etl')

def get_spaces_client():
    """Get DigitalOcean Spaces client"""
    if not SPACES_ACCESS_KEY or not SPACES_SECRET_KEY:
        print("❌ Missing Spaces credentials!")
        print("Please set SPACES_ACCESS_KEY and SPACES_SECRET_KEY in your .env file")
        return None, None
    
    session = boto3.session.Session()
    client = session.client('s3',
                           region_name=SPACES_REGION,
                           endpoint_url=f'https://{SPACES_REGION}.digitaloceanspaces.com',
                           aws_access_key_id=SPACES_ACCESS_KEY,
                           aws_secret_access_key=SPACES_SECRET_KEY)
    
    return client, SPACES_BUCKET

def list_objects_in_prefix(spaces_client, bucket, prefix):
    """List all objects with a given prefix"""
    objects = []
    
    try:
        paginator = spaces_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
        
        for page in page_iterator:
            if 'Contents' in page:
                objects.extend([obj['Key'] for obj in page['Contents']])
        
        return objects
    except Exception as e:
        print(f"❌ Error listing objects with prefix '{prefix}': {e}")
        return []

def delete_objects(spaces_client, bucket, object_keys):
    """Delete multiple objects from Spaces"""
    if not object_keys:
        print("No objects to delete")
        return True
    
    try:
        # Delete objects in batches of 1000 (S3 limit)
        batch_size = 1000
        for i in range(0, len(object_keys), batch_size):
            batch = object_keys[i:i + batch_size]
            
            delete_objects_request = {
                'Objects': [{'Key': key} for key in batch],
                'Quiet': True
            }
            
            response = spaces_client.delete_objects(
                Bucket=bucket,
                Delete=delete_objects_request
            )
            
            print(f"Deleted batch {i//batch_size + 1}: {len(batch)} objects")
        
        return True
    except Exception as e:
        print(f"❌ Error deleting objects: {e}")
        return False

def clean_spaces_data():
    """Clean all existing data from Spaces"""
    
    # Get Spaces client
    spaces_client, bucket = get_spaces_client()
    if not spaces_client:
        return False
    
    print(f"🧹 Cleaning data from Spaces bucket: {bucket}")
    print("=" * 50)
    
    # List of prefixes to clean
    prefixes_to_clean = [
        "batches/",
        "filtered_batches/",
        "sessions/",
        "raw_data/",
        "products/",
        "metadata/",
        "search_after/"
    ]
    
    total_deleted = 0
    
    for prefix in prefixes_to_clean:
        print(f"\n📋 Checking prefix: {prefix}")
        
        # List objects in this prefix
        objects = list_objects_in_prefix(spaces_client, bucket, prefix)
        
        if objects:
            print(f"  Found {len(objects)} objects to delete")
            
            # Delete objects
            if delete_objects(spaces_client, bucket, objects):
                total_deleted += len(objects)
                print(f"  ✅ Deleted {len(objects)} objects from {prefix}")
            else:
                print(f"  ❌ Failed to delete objects from {prefix}")
        else:
            print(f"  No objects found in {prefix}")
    
    print(f"\n🎉 Cleanup completed!")
    print(f"Total objects deleted: {total_deleted}")
    
    return True

def verify_cleanup():
    """Verify that cleanup was successful"""
    spaces_client, bucket = get_spaces_client()
    if not spaces_client:
        return False
    
    print(f"\n🔍 Verifying cleanup...")
    
    # Check if any data remains
    prefixes_to_check = [
        "batches/",
        "filtered_batches/",
        "sessions/"
    ]
    
    remaining_objects = 0
    
    for prefix in prefixes_to_check:
        objects = list_objects_in_prefix(spaces_client, bucket, prefix)
        if objects:
            print(f"  ⚠️  Found {len(objects)} remaining objects in {prefix}")
            remaining_objects += len(objects)
        else:
            print(f"  ✅ No objects remaining in {prefix}")
    
    if remaining_objects == 0:
        print(f"\n✅ Cleanup verification successful!")
        print(f"Spaces bucket is ready for fresh filtered data")
        return True
    else:
        print(f"\n⚠️  Cleanup verification: {remaining_objects} objects still remain")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean existing data from DigitalOcean Spaces')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify cleanup without deleting')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if args.verify_only:
        print("🔍 Verification mode - checking existing data")
        verify_cleanup()
        return 0
    
    # Confirmation prompt
    if not args.force:
        print("⚠️  WARNING: This will delete ALL existing data from Spaces!")
        print("This includes:")
        print("  - All batch files")
        print("  - All session metadata")
        print("  - All raw data")
        print("  - All product files")
        print()
        
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Cleanup cancelled")
            return 0
    
    # Perform cleanup
    if clean_spaces_data():
        # Verify cleanup
        verify_cleanup()
        
        print(f"\n🎉 Spaces bucket cleaned successfully!")
        print(f"📝 Next steps:")
        print(f"1. Run fetch_filtered_ows_data.py to download filtered data")
        print(f"2. The new data will be pre-filtered by GPC codes")
        print(f"3. Storage costs will be significantly reduced")
    else:
        print(f"\n❌ Cleanup failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 