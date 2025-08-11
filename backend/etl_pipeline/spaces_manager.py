"""
DigitalOcean Spaces Manager Module
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import boto3
from .config import ETLConfig

logger = logging.getLogger(__name__)

class SpacesManager:
    """Manager for DigitalOcean Spaces operations"""
    
    def __init__(self):
        """Initialize Spaces client"""
        self.config = ETLConfig()
        self.spaces_client = boto3.client(
            's3',
            endpoint_url=self.config.get_spaces_endpoint(),
            aws_access_key_id=self.config.SPACES_ACCESS_KEY,
            aws_secret_access_key=self.config.SPACES_SECRET_KEY
        )
        self.bucket_name = self.config.SPACES_BUCKET
    
    def setup_bucket_structure(self):
        """Setup folder structure in Spaces bucket"""
        folders = [
            'raw_data/',
            'sync_metadata/',
            'processed_data/',
            'logs/',
            'backups/',
            'temp/'
        ]
        
        logger.info(f"Setting up bucket structure in {self.bucket_name}")
        
        for folder in folders:
            try:
                self.spaces_client.put_object(
                    Bucket=self.bucket_name,
                    Key=folder,
                    Body=''
                )
                logger.info(f"Created folder: {folder}")
            except Exception as e:
                logger.warning(f"Folder {folder} already exists or error: {e}")
    
    def store_batch(self, products: List[Dict], batch_number: int, sync_date: str) -> str:
        """Store a batch of products to Spaces"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"raw_data/{sync_date}/batch_{batch_number:04d}_{timestamp}.json"
            
            # Store to Spaces
            self.spaces_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=json.dumps(products, indent=2),
                ContentType='application/json',
                Metadata={
                    'batch_number': str(batch_number),
                    'product_count': str(len(products)),
                    'sync_date': sync_date,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Stored batch {batch_number}: {len(products)} products to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error storing batch {batch_number}: {e}")
            raise
    
    def store_sync_metadata(self, sync_info: Dict):
        """Store sync metadata to Spaces"""
        try:
            self.spaces_client.put_object(
                Bucket=self.bucket_name,
                Key='sync_metadata/last_sync.json',
                Body=json.dumps(sync_info, indent=2),
                ContentType='application/json'
            )
            logger.info("Stored sync metadata")
        except Exception as e:
            logger.error(f"Error storing sync metadata: {e}")
            raise
    
    def get_sync_metadata(self) -> Optional[Dict]:
        """Get sync metadata from Spaces"""
        try:
            response = self.spaces_client.get_object(
                Bucket=self.bucket_name,
                Key='sync_metadata/last_sync.json'
            )
            return json.loads(response['Body'].read())
        except Exception as e:
            logger.warning(f"No sync metadata found: {e}")
            return None
    
    def list_files(self, prefix: str = '') -> List[Dict]:
        """List files in bucket with prefix"""
        try:
            response = self.spaces_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'size_mb': round(obj['Size'] / (1024 * 1024), 2)
                })
            return files
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def download_file(self, key: str, local_path: str):
        """Download a file from Spaces"""
        try:
            self.spaces_client.download_file(
                self.bucket_name,
                key,
                local_path
            )
            logger.info(f"Downloaded {key} to {local_path}")
        except Exception as e:
            logger.error(f"Error downloading {key}: {e}")
            raise
    
    def upload_file(self, local_path: str, key: str):
        """Upload a file to Spaces"""
        try:
            self.spaces_client.upload_file(
                local_path,
                self.bucket_name,
                key
            )
            logger.info(f"Uploaded {local_path} to {key}")
        except Exception as e:
            logger.error(f"Error uploading {local_path}: {e}")
            raise
    
    def delete_file(self, key: str):
        """Delete a file from Spaces"""
        try:
            self.spaces_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"Deleted {key}")
        except Exception as e:
            logger.error(f"Error deleting {key}: {e}")
            raise
    
    def get_file_info(self, key: str) -> Optional[Dict]:
        """Get file information from Spaces"""
        try:
            response = self.spaces_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            logger.error(f"Error getting file info for {key}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to Spaces"""
        try:
            # Try to list objects in bucket
            response = self.spaces_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            logger.info("Spaces connection successful")
            return True
        except Exception as e:
            logger.error(f"Spaces connection failed: {e}")
            return False
    
    def get_bucket_stats(self) -> Dict:
        """Get bucket statistics"""
        try:
            files = self.list_files()
            
            total_files = len(files)
            total_size = sum(f['size'] for f in files)
            total_size_mb = round(total_size / (1024 * 1024), 2)
            
            # Group by folder
            folders = {}
            for file in files:
                folder = file['key'].split('/')[0] + '/' if '/' in file['key'] else 'root/'
                if folder not in folders:
                    folders[folder] = {'count': 0, 'size_mb': 0}
                folders[folder]['count'] += 1
                folders[folder]['size_mb'] += file['size_mb']
            
            return {
                'total_files': total_files,
                'total_size_mb': total_size_mb,
                'folders': folders
            }
        except Exception as e:
            logger.error(f"Error getting bucket stats: {e}")
            return {} 