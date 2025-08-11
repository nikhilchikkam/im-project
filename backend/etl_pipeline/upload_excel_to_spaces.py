#!/usr/bin/env python3
"""
Script to upload the Excel file (family_class_brick.xlsx) to DigitalOcean Spaces
This file contains the valid GPC codes for filtering products.
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

# Excel file paths
EXCEL_FILE_LOCAL = "../db scripts/family_class_brick.xlsx"  # Path to local Excel file
EXCEL_FILE_SPACES = "reference/family_class_brick.xlsx"  # Path in Spaces

def get_spaces_client():
    """Get DigitalOcean Spaces client"""
    if not SPACES_ACCESS_KEY or not SPACES_SECRET_KEY:
        print("Missing Spaces credentials!")
        print("Please set SPACES_ACCESS_KEY and SPACES_SECRET_KEY in your .env file")
        return None, None
    
    session = boto3.session.Session()
    client = session.client('s3',
                           region_name=SPACES_REGION,
                           endpoint_url=f'https://{SPACES_REGION}.digitaloceanspaces.com',
                           aws_access_key_id=SPACES_ACCESS_KEY,
                           aws_secret_access_key=SPACES_SECRET_KEY)
    
    return client, SPACES_BUCKET

def upload_excel_to_spaces():
    """Upload the Excel file to Spaces"""
    
    # Check if local file exists
    if not os.path.exists(EXCEL_FILE_LOCAL):
        print(f"Local Excel file not found: {EXCEL_FILE_LOCAL}")
        print("Please ensure the Excel file exists in the db scripts directory")
        return False
    
    # Get Spaces client
    spaces_client, bucket = get_spaces_client()
    if not spaces_client:
        return False
    
    try:
        print(f"Uploading Excel file to Spaces...")
        print(f"  Local file: {EXCEL_FILE_LOCAL}")
        print(f"  Spaces path: {EXCEL_FILE_SPACES}")
        print(f"  Bucket: {bucket}")
        
        # Get file size
        file_size = os.path.getsize(EXCEL_FILE_LOCAL)
        print(f"  File size: {file_size / (1024*1024):.2f} MB")
        
        # Upload file
        with open(EXCEL_FILE_LOCAL, 'rb') as f:
            spaces_client.put_object(
                Bucket=bucket,
                Key=EXCEL_FILE_SPACES,
                Body=f.read(),
                ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        print(f"Successfully uploaded Excel file to Spaces!")
        print(f"You can now use this file with spaces_main.py")
        
        return True
        
    except Exception as e:
        print(f"Failed to upload Excel file: {e}")
        return False

def verify_upload():
    """Verify the file was uploaded successfully"""
    spaces_client, bucket = get_spaces_client()
    if not spaces_client:
        return False
    
    try:
        print(f"Verifying upload...")
        response = spaces_client.head_object(Bucket=bucket, Key=EXCEL_FILE_SPACES)
        
        print(f"File verified in Spaces!")
        print(f"  Size: {response['ContentLength'] / (1024*1024):.2f} MB")
        print(f"  Last Modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"Failed to verify upload: {e}")
        return False

def main():
    """Main function"""
    print("Upload Excel file to DigitalOcean Spaces")
    print("=" * 50)
    
    # Upload file
    if upload_excel_to_spaces():
        # Verify upload
        verify_upload()
        
        print("\nExcel file uploaded successfully!")
        print("\nNext steps:")
        print("1. Run spaces_main.py to process data from Spaces")
        print("2. The script will automatically download this Excel file")
        print("3. Products will be filtered based on the GPC codes in this file")
    else:
        print("\nFailed to upload Excel file")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 