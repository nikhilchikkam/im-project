#!/usr/bin/env python3
"""
Simple test script for DigitalOcean Spaces connection
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_spaces_connection():
    """Test DigitalOcean Spaces connection"""
    
    # Get configuration from environment
    spaces_key = os.getenv('SPACES_ACCESS_KEY')
    spaces_secret = os.getenv('SPACES_SECRET_KEY')
    spaces_region = os.getenv('SPACES_REGION', 'sfo3')
    spaces_bucket = os.getenv('SPACES_BUCKET', 'nutrigence-etl')
    
    print("Testing DigitalOcean Spaces Connection...")
    print(f"  Region: {spaces_region}")
    print(f"  Bucket: {spaces_bucket}")
    print(f"  Access Key: {spaces_key[:10]}..." if spaces_key else "  Access Key: Not set")
    print(f"  Secret Key: {'Set' if spaces_secret else 'Not set'}")
    
    if not spaces_key or not spaces_secret:
        print("Missing Spaces credentials!")
        print("Please set SPACES_ACCESS_KEY and SPACES_SECRET_KEY environment variables")
        return False
    
    try:
        # Create Spaces client
        session = boto3.session.Session()
        client = session.client('s3',
                               region_name=spaces_region,
                               endpoint_url=f'https://{spaces_region}.digitaloceanspaces.com',
                               aws_access_key_id=spaces_key,
                               aws_secret_access_key=spaces_secret)
        
        # Test bucket access
        print("Testing bucket access...")
        response = client.head_bucket(Bucket=spaces_bucket)
        print("Bucket access successful!")
        
        # Test file upload
        print("Testing file upload...")
        test_content = "Hello from ETL Pipeline Test!"
        client.put_object(
            Bucket=spaces_bucket,
            Key='test/connection_test.txt',
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print("File upload successful!")
        
        # Test file download
        print("Testing file download...")
        response = client.get_object(Bucket=spaces_bucket, Key='test/connection_test.txt')
        downloaded_content = response['Body'].read().decode('utf-8')
        if downloaded_content == test_content:
            print("File download successful!")
        else:
            print("File content mismatch!")
            return False
        
        # Clean up test file
        print("Cleaning up test file...")
        client.delete_object(Bucket=spaces_bucket, Key='test/connection_test.txt')
        print("Test file cleaned up!")
        
        print("All Spaces tests passed!")
        return True
        
    except ClientError as e:
        print(f"Spaces connection failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_spaces_connection() 