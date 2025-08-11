#!/usr/bin/env python3
"""
Main script for processing OneWorldSync data from DigitalOcean Spaces
- Downloads batch files from Spaces
- Filters products by GPC codes from Excel file
- Processes products in memory
- Maintains the same filtering logic as the original main.py
"""

import os
import json
import psycopg2
import pandas as pd
import boto3
from dotenv import load_dotenv
from allergen_loader import extract_allergens, insert_allergens

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

DATABASE_URL = os.getenv("DATABASE_URL")

# DigitalOcean Spaces configuration
SPACES_ACCESS_KEY = os.getenv('SPACES_ACCESS_KEY')
SPACES_SECRET_KEY = os.getenv('SPACES_SECRET_KEY')
SPACES_REGION = os.getenv('SPACES_REGION', 'sfo3')
SPACES_BUCKET = os.getenv('SPACES_BUCKET', 'nutrigence-etl')

# Excel file configuration
EXCEL_FILE_LOCAL = "family_class_brick.xlsx"  # Local copy
EXCEL_FILE_SPACES = "reference/family_class_brick.xlsx"  # In Spaces
LOG_FILE = "bad_records.log"

# Globals
success_count = 0
fail_count = 0
skip_count = 0
conn = None
valid_brick_codes = set()

def get_spaces_client():
    """Get DigitalOcean Spaces client"""
    if not SPACES_ACCESS_KEY or not SPACES_SECRET_KEY:
        print("Missing Spaces credentials!")
        return None, None
    
    session = boto3.session.Session()
    client = session.client('s3',
                           region_name=SPACES_REGION,
                           endpoint_url=f'https://{SPACES_REGION}.digitaloceanspaces.com',
                           aws_access_key_id=SPACES_ACCESS_KEY,
                           aws_secret_access_key=SPACES_SECRET_KEY)
    
    return client, SPACES_BUCKET

def download_excel_from_spaces(spaces_client, bucket):
    """Download the Excel file from Spaces if it doesn't exist locally"""
    if os.path.exists(EXCEL_FILE_LOCAL):
        print(f"✅ Using local Excel file: {EXCEL_FILE_LOCAL}")
        return True
    
    try:
        print(f"📥 Downloading Excel file from Spaces: {EXCEL_FILE_SPACES}")
        response = spaces_client.get_object(Bucket=bucket, Key=EXCEL_FILE_SPACES)
        
        with open(EXCEL_FILE_LOCAL, 'wb') as f:
            f.write(response['Body'].read())
        
        print(f"✅ Downloaded Excel file: {EXCEL_FILE_LOCAL}")
        return True
    except Exception as e:
        print(f"❌ Failed to download Excel file: {e}")
        print(f"💡 Please ensure {EXCEL_FILE_SPACES} exists in your Spaces bucket")
        return False

def load_valid_brick_codes():
    """Load valid brick codes from Excel file"""
    try:
        df = pd.read_excel(EXCEL_FILE_LOCAL)
        codes = set(str(code).strip() for code in df["BrickCode"].dropna().astype(str))
        print(f"✅ Loaded {len(codes)} valid brick codes from Excel file")
        return codes
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return set()

def log_bad_record(batch_id, index, error):
    """Log bad records to file"""
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{batch_id} - Record #{index} - Error: {error}\n")

def process_batch_from_spaces(spaces_client, bucket, batch_key, cur):
    """Process a single batch file from Spaces"""
    global success_count, fail_count, skip_count, conn
    
    try:
        print(f"📥 Downloading batch: {batch_key}")
        response = spaces_client.get_object(Bucket=bucket, Key=batch_key)
        batch_data = json.loads(response['Body'].read().decode('utf-8'))
        
        products = batch_data.get('products', [])
        batch_id = batch_data.get('batch_id', 'unknown')
        
        print(f"📊 Processing {len(products)} products from batch: {batch_id}")
        
        for i, product in enumerate(products):
            try:
                # Extract GPC code
                gpc_code = str(product.get("globalClassificationCategory", {}).get("code", ""))
                
                if gpc_code not in valid_brick_codes:
                    skip_count += 1
                    continue
                
                # Process allergens (you can add other loaders here)
                allergen_rows = extract_allergens(product)
                insert_allergens(cur, allergen_rows)
                
                conn.commit()
                success_count += 1
                
            except Exception as e:
                conn.rollback()
                fail_count += 1
                log_bad_record(batch_id, i, str(e))
                print(f"❌ Error in record #{i} of {batch_id}: {e}")
        
        print(f"✅ Completed batch: {batch_id}")
        
    except Exception as e:
        print(f"❌ Error processing batch {batch_key}: {e}")

def list_batch_files(spaces_client, bucket, session_id=None):
    """List all batch files in Spaces"""
    try:
        if session_id:
            # List files for a specific session
            prefix = f"batches/batch_{session_id}/"
        else:
            # List all batch files
            prefix = "batches/"
        
        response = spaces_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix
        )
        
        batch_files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('_products.json'):
                    batch_files.append(obj['Key'])
        
        return sorted(batch_files)
    
    except Exception as e:
        print(f"❌ Error listing batch files: {e}")
        return []

def process_all_batches(spaces_client, bucket, session_id=None):
    """Process all batch files from Spaces"""
    global conn, valid_brick_codes
    
    # Load valid brick codes
    valid_brick_codes = load_valid_brick_codes()
    if not valid_brick_codes:
        print("❌ No valid brick codes loaded. Exiting.")
        return
    
    # List batch files
    batch_files = list_batch_files(spaces_client, bucket, session_id)
    if not batch_files:
        print("❌ No batch files found in Spaces")
        return
    
    print(f"\n📦 Found {len(batch_files)} batch files to process")
    
    # Process files
    with psycopg2.connect(DATABASE_URL) as db_conn:
        conn = db_conn
        with conn.cursor() as cur:
            for i, batch_key in enumerate(batch_files, 1):
                print(f"\n[{i}/{len(batch_files)}] Processing: {batch_key}")
                process_batch_from_spaces(spaces_client, bucket, batch_key, cur)
    
    print(f"\n🎉 All batches processed!")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⏭️  Skipped (Invalid GPC): {skip_count}")
    print(f"📝 Errors logged in: {LOG_FILE}")

def upload_excel_to_spaces(spaces_client, bucket):
    """Upload the Excel file to Spaces for future use"""
    if not os.path.exists(EXCEL_FILE_LOCAL):
        print(f"❌ Local Excel file not found: {EXCEL_FILE_LOCAL}")
        return False
    
    try:
        print(f"📤 Uploading Excel file to Spaces: {EXCEL_FILE_SPACES}")
        with open(EXCEL_FILE_LOCAL, 'rb') as f:
            spaces_client.put_object(
                Bucket=bucket,
                Key=EXCEL_FILE_SPACES,
                Body=f.read(),
                ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        print(f"✅ Uploaded Excel file to Spaces")
        return True
    except Exception as e:
        print(f"❌ Failed to upload Excel file: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process OneWorldSync data from DigitalOcean Spaces')
    parser.add_argument('--session-id', help='Process only files from a specific session')
    parser.add_argument('--upload-excel', action='store_true', help='Upload Excel file to Spaces')
    parser.add_argument('--list-batches', action='store_true', help='List all batch files in Spaces')
    
    args = parser.parse_args()
    
    # Get Spaces client
    spaces_client, bucket = get_spaces_client()
    if not spaces_client:
        print("❌ Failed to create Spaces client")
        return 1
    
    print(f"✅ Connected to Spaces bucket: {bucket}")
    
    # Upload Excel file if requested
    if args.upload_excel:
        upload_excel_to_spaces(spaces_client, bucket)
        return 0
    
    # List batches if requested
    if args.list_batches:
        batch_files = list_batch_files(spaces_client, bucket, args.session_id)
        print(f"\n📋 Batch files in Spaces:")
        for i, batch_file in enumerate(batch_files, 1):
            print(f"  {i}. {batch_file}")
        return 0
    
    # Download Excel file
    if not download_excel_from_spaces(spaces_client, bucket):
        print("❌ Failed to get Excel file. Please ensure it exists in Spaces or locally.")
        return 1
    
    # Process all batches
    process_all_batches(spaces_client, bucket, args.session_id)
    
    return 0

if __name__ == "__main__":
    main() 