"""
Incremental Loader for ETL Scheduler
Reuses initial_load infrastructure with modified criteria for date filtering
Works directly on DigitalOcean App Platform without local file operations
Uses parallel processing for better performance
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Import from initial_load to reuse existing code - using absolute imports
try:
    from initial_load.config import ETLConfig
    from initial_load.utils import get_spaces_client
except ImportError:
    # Fallback for when running as standalone script
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from initial_load.config import ETLConfig
    from initial_load.utils import get_spaces_client

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

logger = logging.getLogger(__name__)

# Configuration for parallel processing
MAX_WORKERS = int(os.getenv('SCHEDULER_MAX_WORKERS', '4'))



class IncrementalLoader:
    """Handles incremental loading by reusing initial_load infrastructure - with parallel batch processing"""
    
    def __init__(self, database_url: str = None, max_workers: int = MAX_WORKERS):
        self.database_url = database_url or ETLConfig.DATABASE_URL
        self.max_workers = max_workers
        self.connection = None
        self.cursor = None
        self.spaces_client = None
        self.spaces_bucket = ETLConfig.SPACES_BUCKET
        self.total_stats = {
            'batches_processed': 0,
            'products_processed': 0,
            'products_updated': 0,
            'products_inserted': 0,
            'errors': 0
        }
        
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
    

    
    def build_incremental_criteria(self, start_date: datetime, end_date: datetime = None) -> Dict[str, Any]:
        """Build incremental criteria with proper date filtering - using the working format from Swagger API"""
        if end_date is None:
            end_date = datetime.now()
            
        # Use the proven working criteria format from OneWorldSync Swagger API
        base_query = {
            "pullHierarchy": False,
            "targetMarket": "US",
            "lastModifiedDate": {
                "from": {
                    "date": start_date.strftime("%Y-%m-%d"),
                    "op": "GTE"
                },
                "to": {
                    "date": end_date.strftime("%Y-%m-%d"),
                    "op": "LTE"
                }
            },
            "sortFields": [
                {
                    "field": "lastModifiedDate",
                    "desc": "true"
                },
                {
                    "field": "gtin",
                    "desc": "false"
                }
            ],
            "fields": {
                "include": [
                    "gtin",
                    "functionalName",
                    "productDescription",
                    "ingredientStatement",
                    "brandName",
                    "productType",
                    "isConsumerUnit",
                    "globalClassificationCategory",
                    "lastModifiedDate",
                    "nutrientInformation",
                    "allergenRelatedInformation",
                    "foodAndBevDietTypeInfo",
                    "productInformationDetail",
                    "externalFileLink",
                    "dam"
                ],
                "exclude": []
            }
        }
        
        return base_query
    
    def fetch_incremental_data(self, criteria: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """
        Fetch incremental data from OneWorldSync with proper date filtering
        Now using the correct criteria format that works with the API
        """
        logger.info(f"Fetching incremental data with criteria: {json.dumps(criteria, indent=2)}")
        
        try:
            from oneworldsync import Content1Client, AuthenticationError, APIError
            
            # Create client instance (same as fetch_products.py)
            client = Content1Client()
            
            batches = []
            search_after = None
            batch_size = ETLConfig.OWS_BATCH_SIZE
            
            while True:
                logger.info(f"Fetching batch with searchAfter: {search_after}")
                
                # Update criteria with searchAfter if we have it
                current_criteria = criteria.copy()
                if search_after:
                    current_criteria["searchAfter"] = search_after
                
                try:
                    # Fetch products using the same method as fetch_products.py
                    result = client.fetch_products(criteria=current_criteria, page_size=batch_size)
                    products = result.get("items", [])
                    
                    if not products:
                        logger.info("No more products found, stopping...")
                        break
                    
                    logger.info(f"Received {len(products)} products in batch")
                    
                    # Add batch to our list
                    batches.append(products)
                    
                    # Get searchAfter for next batch
                    if "searchAfter" in result:
                        search_after = result["searchAfter"]
                    else:
                        logger.info("No searchAfter token, stopping...")
                        break
                        
                except AuthenticationError as e:
                    logger.error(f"Authentication error: {e}")
                    raise
                except APIError as e:
                    logger.error(f"API error: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Error fetching products: {e}")
                    raise
            
            logger.info(f"✅ Successfully fetched {len(batches)} batches from OWS API with proper date filtering")
            
            return batches
            
        except ImportError:
            logger.error("oneworldsync library not found. Please install it: pip install oneworldsync")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OWS client: {e}")
            raise
    
    def save_batches_to_spaces(self, batches: List[List[Dict[str, Any]]], session_id: str) -> List[str]:
        """Save incremental batches to DigitalOcean Spaces using same structure as initial_load"""
        batch_keys = []
        
        try:
            for batch_number, products in enumerate(batches, 1):
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
                
                batch_keys.append(batch_key)
                logger.info(f"Saved batch {batch_number} to Spaces: {batch_key} ({len(products)} products)")
            
            return batch_keys
            
        except Exception as e:
            logger.error(f"Failed to save batches to Spaces: {e}")
            raise
    

    
    def _process_batches_parallel(self, batch_keys: List[str]) -> Dict[str, int]:
        """Process batches using the Spaces ETL Orchestrator (reuses initial_load architecture)"""
        try:
            # Import the Spaces ETL Orchestrator
            from spaces_etl_orchestrator import SpacesETLOrchestrator
            
            # Create orchestrator instance
            orchestrator = SpacesETLOrchestrator(max_workers=self.max_workers)
            
            # Extract session_id from the first batch key
            if not batch_keys:
                return self.total_stats
            
            # Extract session_id from batch key format: incremental_batches/batch_{session_id}/...
            first_batch_key = batch_keys[0]
            session_id = first_batch_key.split('/')[1].replace('batch_', '')
            
            logger.info(f"Using Spaces ETL Orchestrator for session: {session_id}")
            
            # Run the ETL process using the orchestrator
            result = orchestrator.run_etl_from_spaces(session_id)
            
            if result['status'] == 'success':
                # Convert orchestrator results to our stats format (align with new keys)
                self.total_stats = {
                    'batches_processed': result.get('processed_batches', 0),
                    'products_processed': result.get('products_processed', 0),
                    # Upserts: conservatively count all as updates; inserts not tracked separately here
                    'products_updated': result.get('products_processed', 0),
                    'products_inserted': 0,
                    'errors': result.get('error_batches', 0)
                }
                logger.info(f"Spaces ETL Orchestrator completed successfully: {self.total_stats}")
            else:
                logger.error(f"Spaces ETL Orchestrator failed: {result.get('error')}")
                self.total_stats['errors'] = len(batch_keys)  # Mark all as errors
            
        except Exception as e:
            logger.error(f"Failed to use Spaces ETL Orchestrator: {e}")
            self.total_stats['errors'] = len(batch_keys)  # Mark all as errors
        
        return self.total_stats
    

    
    def run_incremental_update(self, lookback_days: int = None) -> Dict[str, Any]:
        """Run incremental update using initial_load infrastructure with parallel batch processing"""
        start_time = time.time()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_keys = []
        
        try:
            # Connect to database
            self.connect()
            
            # Setup Spaces client
            self.setup_spaces_client()
            

            
            # Get date range
            if lookback_days is None:
                lookback_days = 7  # Default to 7 days
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            logger.info(f"Starting incremental update from {start_date} to {end_date}")
            
            # Build incremental criteria
            criteria = self.build_incremental_criteria(start_date, end_date)
            
            # Step 1: Fetch data from OWS in batches (like initial load)
            logger.info("Step 1: Fetching data from OneWorldSync in batches...")
            batches = self.fetch_incremental_data(criteria)
            
            if not batches:
                logger.info("No batches found for incremental update")
                return {'status': 'success', 'message': 'No batches to update'}
            
            # Step 2: Save batches to DigitalOcean Spaces (like initial load)
            logger.info("Step 2: Saving batches to DigitalOcean Spaces...")
            batch_keys = self.save_batches_to_spaces(batches, session_id)
            
            # Step 3: Process batches with parallel workers (exactly like initial load)
            logger.info("Step 3: Processing batches with parallel workers...")
            
            # Initialize total stats for result collection
            self.total_stats = {
                'batches_processed': 0,
                'products_processed': 0,
                'products_updated': 0,
                'products_inserted': 0,
                'errors': 0
            }
            
            # Pass batch keys directly to workers (they will read from DO Spaces)
            stats = self._process_batches_parallel(batch_keys)
            
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
                'processing_time': total_time,
                'workers_used': self.max_workers
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
                    {'batches_processed': 0, 'products_processed': 0, 'products_updated': 0, 'products_inserted': 0, 'errors': 1},
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
