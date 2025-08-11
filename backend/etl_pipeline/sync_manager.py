"""
Sync Management Module
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from .spaces_manager import SpacesManager

logger = logging.getLogger(__name__)

class SyncManager:
    """Manages sync operations and metadata"""
    
    def __init__(self, spaces_manager: SpacesManager):
        """Initialize sync manager"""
        self.spaces_manager = spaces_manager
    
    def get_last_sync_info(self) -> Optional[Dict]:
        """Get last sync information from Spaces"""
        return self.spaces_manager.get_sync_metadata()
    
    def get_last_sync_date(self) -> Optional[datetime]:
        """Get last sync date as datetime object"""
        sync_info = self.get_last_sync_info()
        if sync_info and sync_info.get('last_sync_date'):
            try:
                return datetime.fromisoformat(sync_info['last_sync_date'])
            except ValueError as e:
                logger.warning(f"Invalid sync date format: {e}")
                return None
        return None
    
    def update_sync_metadata(self, sync_info: Dict):
        """Update sync metadata in Spaces"""
        self.spaces_manager.store_sync_metadata(sync_info)
    
    def create_sync_info(self, 
                        sync_type: str = 'incremental',
                        files_stored: int = 0,
                        products_processed: int = 0,
                        duration_seconds: float = 0,
                        status: str = 'completed',
                        error: Optional[str] = None) -> Dict:
        """Create sync information dictionary"""
        sync_info = {
            'last_sync_date': datetime.now().isoformat(),
            'sync_type': sync_type,
            'files_stored': files_stored,
            'products_processed': products_processed,
            'status': status,
            'duration_seconds': duration_seconds,
            'spaces_bucket': self.spaces_manager.bucket_name
        }
        
        if error:
            sync_info['error'] = error
        
        return sync_info
    
    def is_sync_needed(self, hours_threshold: int = 24) -> bool:
        """Check if sync is needed based on time threshold"""
        last_sync = self.get_last_sync_date()
        
        if not last_sync:
            logger.info("No previous sync found - sync needed")
            return True
        
        time_since_sync = datetime.now() - last_sync
        hours_since_sync = time_since_sync.total_seconds() / 3600
        
        if hours_since_sync >= hours_threshold:
            logger.info(f"Last sync was {hours_since_sync:.1f} hours ago - sync needed")
            return True
        else:
            logger.info(f"Last sync was {hours_since_sync:.1f} hours ago - no sync needed")
            return False
    
    def get_sync_summary(self) -> Dict:
        """Get summary of sync operations"""
        sync_info = self.get_last_sync_info()
        
        if not sync_info:
            return {
                'status': 'no_sync_data',
                'message': 'No sync data available'
            }
        
        summary = {
            'last_sync_date': sync_info.get('last_sync_date'),
            'sync_type': sync_info.get('sync_type', 'unknown'),
            'status': sync_info.get('status', 'unknown'),
            'files_stored': sync_info.get('files_stored', 0),
            'products_processed': sync_info.get('products_processed', 0),
            'duration_seconds': sync_info.get('duration_seconds', 0)
        }
        
        # Calculate time since last sync
        if sync_info.get('last_sync_date'):
            try:
                last_sync = datetime.fromisoformat(sync_info['last_sync_date'])
                time_since_sync = datetime.now() - last_sync
                summary['hours_since_sync'] = round(time_since_sync.total_seconds() / 3600, 1)
            except ValueError:
                summary['hours_since_sync'] = None
        
        return summary
    
    def mark_sync_failed(self, error: str):
        """Mark sync as failed"""
        sync_info = self.create_sync_info(
            status='failed',
            error=error
        )
        self.update_sync_metadata(sync_info)
        logger.error(f"Sync marked as failed: {error}")
    
    def cleanup_old_sync_data(self, days_to_keep: int = 30):
        """Clean up old sync data files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            files = self.spaces_manager.list_files('raw_data/')
            
            deleted_count = 0
            for file in files:
                if file['last_modified'] < cutoff_date:
                    self.spaces_manager.delete_file(file['key'])
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old sync files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old sync data: {e}")
    
    def validate_sync_data(self) -> Dict:
        """Validate sync data integrity"""
        try:
            files = self.spaces_manager.list_files('raw_data/')
            
            validation_result = {
                'total_files': len(files),
                'total_size_mb': sum(f['size_mb'] for f in files),
                'file_count_by_date': {},
                'errors': []
            }
            
            # Group files by date
            for file in files:
                # Extract date from filename like 'raw_data/2024/01/batch_0001_20240115_020000.json'
                parts = file['key'].split('/')
                if len(parts) >= 3:
                    date_key = f"{parts[1]}/{parts[2]}"
                    if date_key not in validation_result['file_count_by_date']:
                        validation_result['file_count_by_date'][date_key] = 0
                    validation_result['file_count_by_date'][date_key] += 1
            
            # Check for potential issues
            if not files:
                validation_result['errors'].append("No raw data files found")
            
            if not self.get_last_sync_info():
                validation_result['errors'].append("No sync metadata found")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating sync data: {e}")
            return {
                'errors': [f"Validation failed: {str(e)}"]
            } 