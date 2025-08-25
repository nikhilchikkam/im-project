"""
ETL Utilities Module
"""

import os
import json
import boto3
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')  # backend/.env

def get_spaces_client():
    """Get DigitalOcean Spaces client"""
    spaces_access_key = os.getenv('SPACES_ACCESS_KEY')
    spaces_secret_key = os.getenv('SPACES_SECRET_KEY')
    spaces_region = os.getenv('SPACES_REGION', 'sfo3')
    spaces_bucket = os.getenv('SPACES_BUCKET', 'nutrigence-etl')
    
    if not spaces_access_key or not spaces_secret_key:
        raise ValueError("SPACES_ACCESS_KEY and SPACES_SECRET_KEY are required")
    
    session = boto3.session.Session()
    client = session.client('s3',
        region_name=spaces_region,
        endpoint_url=f'https://{spaces_region}.digitaloceanspaces.com',
        aws_access_key_id=spaces_access_key,
        aws_secret_access_key=spaces_secret_key)
    
    return client, spaces_bucket

def download_excel_from_spaces():
    """Download Excel file from Spaces"""
    excel_file_local = "family_class_brick.xlsx"
    excel_file_spaces = "reference/family_class_brick.xlsx"
    
    if os.path.exists(excel_file_local):
        print(f"Using local Excel file: {excel_file_local}")
        return True
        
    try:
        spaces_client, bucket = get_spaces_client()
        print(f"Downloading Excel file from Spaces: {excel_file_spaces}")
        
        response = spaces_client.get_object(Bucket=bucket, Key=excel_file_spaces)
        with open(excel_file_local, 'wb') as f:
            f.write(response['Body'].read())
            
        print(f"Downloaded Excel file: {excel_file_local}")
        return True
    except Exception as e:
        print(f"Failed to download Excel file: {e}")
        return False

def load_gpc_codes():
    """Load valid GPC codes from Excel file"""
    # Try multiple paths for the Excel file
    possible_paths = [
        "family_class_brick.xlsx",  # Current directory (for backward compatibility)
        "../reference_files/family_class_brick.xlsx",  # Reference files directory
        "reference_files/family_class_brick.xlsx",  # Reference files from etl_pipeline
        "../../reference_files/family_class_brick.xlsx"  # Reference files from initial_load
    ]
    
    excel_file = None
    for path in possible_paths:
        if os.path.exists(path):
            excel_file = path
            break
    
    if not excel_file:
        print(f"Excel file not found in any of these locations: {possible_paths}")
        return set()
        
    try:
        df = pd.read_excel(excel_file)
        gpc_codes = set(str(code).strip() for code in df["BrickCode"].dropna().astype(str))
        print(f"Loaded {len(gpc_codes)} valid GPC codes from {excel_file}")
        return gpc_codes
    except Exception as e:
        print(f"Error loading Excel file {excel_file}: {e}")
        return set()

def filter_products_by_gpc(products, valid_gpc_codes):
    """Filter products by GPC codes"""
    if not valid_gpc_codes:
        return products
        
    filtered_products = []
    for product in products:
        item = product.get("item", {})
        gpc_info = item.get("globalClassificationCategory", {})
        gpc_code = str(gpc_info.get("code", ""))
        
        if gpc_code and gpc_code in valid_gpc_codes:
            filtered_products.append(product)
            
    # Removed verbose logging for performance - filtering completed
    return filtered_products

def get_batch_files_from_spaces(session_id=None):
    """Get batch files from Spaces"""
    try:
        spaces_client, bucket = get_spaces_client()
        
        # List objects in filtered_batches
        prefix = "filtered_batches/"
        if session_id:
            prefix += f"batch_{session_id}/"
            
        response = spaces_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        batch_files = []
        
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('_products.json'):
                batch_files.append(obj['Key'])
                
        print(f"Found {len(batch_files)} batch files in Spaces")
        return batch_files
        
    except Exception as e:
        print(f"Error listing batch files: {e}")
        return []

def download_batch_from_spaces(batch_key):
    """Download a batch file from Spaces"""
    try:
        spaces_client, bucket = get_spaces_client()
        response = spaces_client.get_object(Bucket=bucket, Key=batch_key)
        
        batch_data = json.loads(response['Body'].read().decode('utf-8'))
        return batch_data.get('products', [])
        
    except Exception as e:
        print(f"Error downloading batch {batch_key}: {e}")
        return [] 