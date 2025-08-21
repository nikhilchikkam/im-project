"""
Incremental Loader for ETL Scheduler
Reuses initial_load infrastructure with modified criteria for date filtering
Works directly on DigitalOcean App Platform without local file operations
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Iterator
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Import from initial_load to reuse existing code - using absolute imports
try:
    from initial_load.config import ETLConfig
    from initial_load.utils import get_spaces_client, filter_products_by_gpc
    from initial_load.loaders.batch_loader import BatchLoader
except ImportError:
    # Fallback for when running as standalone script
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from initial_load.config import ETLConfig
    from initial_load.utils import get_spaces_client, filter_products_by_gpc
    from initial_load.loaders.batch_loader import BatchLoader

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

logger = logging.getLogger(__name__)

class IncrementalLoader:
    """Handles incremental loading by reusing initial_load infrastructure - no local files"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or ETLConfig.DATABASE_URL
        self.connection = None
        self.cursor = None
        self.spaces_client = None
        self.spaces_bucket = ETLConfig.SPACES_BUCKET
        self.batch_loader = None
        
    def connect(self):
        """Create database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.debug("Database connection closed")
    
    def setup_spaces_client(self):
        """Setup DigitalOcean Spaces client using initial_load utils"""
        try:
            self.spaces_client, self.spaces_bucket = get_spaces_client()
            logger.info("DigitalOcean Spaces client configured")
        except Exception as e:
            logger.error(f"Failed to setup Spaces client: {e}")
            raise
    
    def setup_batch_loader(self):
        """Setup batch loader from initial_load"""
        try:
            self.batch_loader = BatchLoader(self.database_url)
            logger.info("Batch loader configured")
        except Exception as e:
            logger.error(f"Failed to setup batch loader: {e}")
            raise
    
    def get_last_update_timestamp(self) -> datetime:
        """Get the timestamp of the last successful update"""
        try:
            self.cursor.execute("""
                SELECT MAX(created_at) as last_update 
                FROM etl_update_log 
                WHERE status = 'success'
            """)
            result = self.cursor.fetchone()
            
            if result and result['last_update']:
                return result['last_update']
            else:
                # Default to 7 days ago if no previous update
                return datetime.now() - timedelta(days=7)
                
        except Exception as e:
            logger.warning(f"Could not get last update timestamp: {e}")
            return datetime.now() - timedelta(days=7)
    
    def build_incremental_criteria(self, start_date: datetime, end_date: datetime = None) -> Dict[str, Any]:
        """Build incremental criteria with date range - reuses initial_load query structure"""
        if end_date is None:
            end_date = datetime.now()
            
        # Start with the base query from initial_load
        base_query = {
            "targetMarket": "US",
            "pullHierarchy": False,
            "sortFields": [
                {"field": "lastModifiedDate", "desc": True},
                {"field": "gtin", "desc": False}
            ]
        }
        
        # Add the date filtering criteria
        base_query["lastModifiedDate"] = {
            "from": {
                "date": start_date.strftime("%Y-%m-%d"),
                "op": "GTE"
            },
            "to": {
                "date": end_date.strftime("%Y-%m-%d"),
                "op": "LTE"
            }
        }
        
        return base_query
    
    def fetch_incremental_data(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch incremental data from OneWorldSync using the same approach as initial_load
        """
        # TODO: Implement actual OneWorldSync API call using the same client as initial_load
        # This should use the same OWS client and approach as your existing scripts
        logger.info(f"Fetching incremental data with criteria: {json.dumps(criteria, indent=2)}")
        
        # Placeholder implementation - replace with actual OWS client call
        # You would typically do something like:
        # from oneworldsync import Content1Client
        # client = Content1Client()
        # result = client.fetch_products(criteria=criteria, page_size=ETLConfig.OWS_BATCH_SIZE)
        # return result.get('items', [])
        
        return []
    
    def save_to_spaces(self, products: List[Dict[str, Any]], session_id: str, batch_number: int) -> str:
        """Save incremental data to DigitalOcean Spaces using same structure as initial_load"""
        try:
            # Create session directory structure (similar to initial_load)
            session_key = f"incremental_batches/batch_{session_id}/"
            
            # Create batch filename (similar to initial_load format)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_filename = f"incremental_batch_{timestamp}_batch_{batch_number:04d}_products.json"
            batch_key = session_key + batch_filename
            
            # Convert products to JSON (same structure as initial_load)
            batch_data = {
                "metadata": {
                    "session_id": session_id,
                    "batch_number": batch_number,
                    "timestamp": timestamp,
                    "product_count": len(products),
                    "type": "incremental"
                },
                "products": products
            }
            
            # Upload to Spaces using same client as initial_load
            self.spaces_client.put_object(
                Bucket=self.spaces_bucket,
                Key=batch_key,
                Body=json.dumps(batch_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Saved batch {batch_number} to Spaces: {batch_key} ({len(products)} products)")
            return batch_key
            
        except Exception as e:
            logger.error(f"Failed to save batch {batch_number} to Spaces: {e}")
            raise
    
    def get_batch_from_spaces(self, batch_key: str) -> Dict[str, Any]:
        """Get batch data directly from DigitalOcean Spaces without downloading to local"""
        try:
            response = self.spaces_client.get_object(
                Bucket=self.spaces_bucket,
                Key=batch_key
            )
            
            # Read the data directly from the response stream
            batch_data = json.loads(response['Body'].read())
            logger.info(f"Retrieved batch from Spaces: {batch_key}")
            return batch_data
            
        except Exception as e:
            logger.error(f"Failed to get batch from Spaces: {e}")
            raise
    
    def run_incremental_update(self, lookback_days: int = None) -> Dict[str, Any]:
        """Run incremental update using initial_load infrastructure - no local files"""
        start_time = time.time()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_keys = []
        
        try:
            # Connect to database
            self.connect()
            
            # Setup Spaces client
            self.setup_spaces_client()
            
            # Setup batch loader from initial_load
            self.setup_batch_loader()
            
            # Get date range
            if lookback_days is None:
                lookback_days = 7  # Default to 7 days
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            logger.info(f"Starting incremental update from {start_date} to {end_date}")
            
            # Build incremental criteria
            criteria = self.build_incremental_criteria(start_date, end_date)
            
            # Step 1: Fetch data from OWS (using same approach as initial_load)
            logger.info("Step 1: Fetching data from OneWorldSync...")
            products = self.fetch_incremental_data(criteria)
            
            if not products:
                logger.info("No products found for incremental update")
                return {'status': 'success', 'message': 'No products to update'}
            
            # Step 2: Save to DigitalOcean Spaces (using same structure as initial_load)
            logger.info("Step 2: Saving data to DigitalOcean Spaces...")
            batch_key = self.save_to_spaces(products, session_id, 1)
            batch_keys.append(batch_key)
            
            # Step 3: Get data from Spaces and process directly with initial_load loaders
            logger.info("Step 3: Processing data directly from Spaces with initial_load loaders...")
            batch_data = self.get_batch_from_spaces(batch_key)
            stats = self._process_batch_with_loaders(batch_data)
            
            # Log the update
            self.log_update(start_date, end_date, stats, session_id, batch_keys, 'success')
            
            total_time = time.time() - start_time
            
            final_result = {
                'status': 'success',
                'session_id': session_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'stats': stats,
                'batch_keys': batch_keys,
                'processing_time': total_time
            }
            
            logger.info(f"Incremental update completed: {final_result}")
            return final_result
            
        except Exception as e:
            logger.error(f"Incremental update failed: {e}")
            
            # Log failure
            try:
                self.log_update(
                    start_date if 'start_date' in locals() else datetime.now(),
                    end_date if 'end_date' in locals() else datetime.now(),
                    {'products_processed': 0, 'products_updated': 0, 'products_inserted': 0, 'errors': 1},
                    session_id if 'session_id' in locals() else 'unknown',
                    batch_keys,
                    'failed'
                )
            except:
                pass
            
            return {
                'status': 'failed',
                'error': str(e)
            }
        
        finally:
            self.disconnect()
    
    def _process_batch_with_loaders(self, batch_data: Dict[str, Any]) -> Dict[str, int]:
        """Process batch using initial_load loaders for proper data handling - no local files"""
        start_time = time.time()
        stats = {
            'products_processed': 0,
            'products_updated': 0,
            'products_inserted': 0,
            'errors': 0
        }
        
        products = batch_data.get('products', [])
        
        try:
            # Use the batch loader from initial_load to process products
            # This will handle all the complex logic for inserting/updating products
            # and their related data (nutrition, allergens, etc.)
            # All processing happens in memory - no local file operations
            
            for product in products:
                try:
                    gtin = product.get('gtin')
                    if not gtin:
                        continue
                    
                    # Check if product exists
                    self.cursor.execute("SELECT gtin FROM products WHERE gtin = %s", (gtin,))
                    exists = self.cursor.fetchone()
                    
                    if exists:
                        # Update existing product using batch loader
                        self._update_product_with_loader(product)
                        stats['products_updated'] += 1
                    else:
                        # Insert new product using batch loader
                        self._insert_product_with_loader(product)
                        stats['products_inserted'] += 1
                    
                    stats['products_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing product {product.get('gtin', 'unknown')}: {e}")
                    stats['errors'] += 1
            
            # Commit transaction
            self.connection.commit()
            
            processing_time = time.time() - start_time
            logger.info(f"Processed batch with loaders (no local files): {stats} in {processing_time:.2f}s")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Batch processing failed: {e}")
            raise
        
        return stats
    
    def _update_product_with_loader(self, product: Dict[str, Any]):
        """Update existing product using initial_load batch loader"""
        try:
            # Use the batch loader's update logic
            # This will handle updating the product and all related data
            self.batch_loader.update_product(product)
        except Exception as e:
            logger.error(f"Failed to update product {product.get('gtin', 'unknown')}: {e}")
            raise
    
    def _insert_product_with_loader(self, product: Dict[str, Any]):
        """Insert new product using initial_load batch loader"""
        try:
            # Use the batch loader's insert logic
            # This will handle inserting the product and all related data
            self.batch_loader.insert_product(product)
        except Exception as e:
            logger.error(f"Failed to insert product {product.get('gtin', 'unknown')}: {e}")
            raise
    
    def log_update(self, start_date: datetime, end_date: datetime, stats: Dict[str, int], 
                   session_id: str, batch_keys: List[str], status: str = 'success'):
        """Log the update operation"""
        try:
            self.cursor.execute("""
                INSERT INTO etl_update_log 
                (start_date, end_date, products_processed, products_updated, products_inserted, 
                 errors, status, session_id, batch_keys, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                start_date,
                end_date,
                stats.get('products_processed', 0),
                stats.get('products_updated', 0),
                stats.get('products_inserted', 0),
                stats.get('errors', 0),
                status,
                session_id,
                json.dumps(batch_keys),
                datetime.now()
            ))
            self.connection.commit()
            logger.info(f"Update logged: {status}")
        except Exception as e:
            logger.error(f"Failed to log update: {e}")
