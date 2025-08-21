#!/usr/bin/env python3
"""
Spaces ETL Orchestrator for scheduler - reads batch data from DO Spaces instead of local files
Modified version of initial_load/etl_orchestrator.py for scheduler use
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any
from multiprocessing import Pool, Queue, Manager
from queue import Empty
import psycopg2
from dotenv import load_dotenv

# Import from initial_load
try:
    from initial_load.utils import get_spaces_client
    from initial_load.loaders.batch_loader import BatchLoader
except ImportError:
    # Fallback for standalone execution
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from initial_load.utils import get_spaces_client
    from initial_load.loaders.batch_loader import BatchLoader

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
MAX_WORKERS = int(os.getenv('SCHEDULER_MAX_WORKERS', '4'))
QUEUE_SIZE = int(os.getenv('SCHEDULER_QUEUE_SIZE', '10'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def worker_process_spaces(worker_id: int, batch_queue: Queue, result_queue: Queue, database_url: str):
    """
    Worker process that processes batches from DO Spaces using staging tables
    
    Args:
        worker_id: Unique identifier for this worker
        batch_queue: Queue containing batch keys (strings) to process
        result_queue: Queue to send results back to main process
        database_url: Database connection string
    """
    logger.info(f"Spaces Worker {worker_id} started")
    
    # Create batch loader instance for this worker
    loader = BatchLoader(database_url)
    
    try:
        # Connect to database and prepare staging tables
        loader.connect()
        loader.prepare_staging()
        
        processed_count = 0
        error_count = 0
        
        while True:
            try:
                # Get batch key from queue (timeout to allow graceful shutdown)
                batch_key = batch_queue.get(timeout=5)
                
                if batch_key == "STOP":
                    logger.info(f"Worker {worker_id} received stop signal")
                    break
                
                logger.debug(f"Worker {worker_id} processing: {batch_key}")
                
                # Load batch data from DO Spaces
                try:
                    # Get Spaces client for this worker
                    spaces_client, spaces_bucket = get_spaces_client()
                    
                    # Read batch data directly from DO Spaces
                    response = spaces_client.get_object(
                        Bucket=spaces_bucket,
                        Key=batch_key
                    )
                    batch_data = json.loads(response['Body'].read())
                    logger.debug(f"Worker {worker_id} loaded batch with {len(batch_data.get('products', []))} products")
                    
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to load batch from DO Spaces {batch_key}: {e}")
                    error_count += 1
                    continue
                
                # Process batch using staging tables
                try:
                    logger.info(f"Worker {worker_id} starting to process batch: {batch_key}")
                    logger.info(f"Worker {worker_id} batch contains {len(batch_data.get('products', []))} products")
                    
                    # Process batch - this will log detailed timing info like initial_load
                    raw_result = loader.process_batch(batch_data)
                    # Normalize keys so aggregator and logs show real counts
                    result = {
                        'products_processed': max(raw_result.get('products_merged', 0), raw_result.get('products_copied', 0)),
                        'serving_processed': max(raw_result.get('serving_merged', 0), raw_result.get('serving_copied', 0)),
                        'diet_claims_processed': max(raw_result.get('diet_claims_merged', 0), raw_result.get('diet_claims_copied', 0)),
                        'image_urls_processed': max(raw_result.get('image_urls_merged', 0), raw_result.get('image_urls_copied', 0)),
                        'nutrition_processed': max(raw_result.get('nutrition_merged', 0), raw_result.get('nutrition_copied', 0)),
                        'allergen_processed': max(raw_result.get('allergen_merged', 0), raw_result.get('allergen_copied', 0)),
                        'total_time': raw_result.get('total_time', 0)
                    }
                    processed_count += 1
                    
                    # Log comprehensive summary for this worker
                    logger.info(f"Worker {worker_id} completed batch: {batch_key}")
                    logger.info(f"Worker {worker_id} comprehensive summary: "
                              f"Products: {result.get('products_processed', 0)}, "
                              f"Serving: {result.get('serving_processed', 0)}, "
                              f"Diet Claims: {result.get('diet_claims_processed', 0)}, "
                              f"Image URLs: {result.get('image_urls_processed', 0)}, "
                              f"Nutrition: {result.get('nutrition_processed', 0)}, "
                              f"Allergen: {result.get('allergen_processed', 0)}, "
                              f"Total time: {result.get('total_time', 0):.2f}s")
                    
                    # Send result back to main process
                    try:
                        result_queue.put({
                            'worker_id': worker_id,
                            'batch_key': batch_key,
                            'result': result,
                            'success': True
                        }, timeout=10)
                        logger.info(f"Worker {worker_id} sent result for batch: {batch_key}")
                    except Exception as queue_error:
                        logger.error(f"Worker {worker_id} failed to send result to queue: {queue_error}")
                        error_count += 1
                    
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to process batch {batch_key}: {e}")
                    error_count += 1
                    
                    # Send error result back to main process
                    try:
                        result_queue.put({
                            'worker_id': worker_id,
                            'batch_key': batch_key,
                            'error': str(e),
                            'success': False
                        }, timeout=10)
                    except Exception as queue_error:
                        logger.error(f"Worker {worker_id} failed to send error to queue: {queue_error}")
                
            except Empty:
                # Queue timeout - continue waiting
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} unexpected error: {e}")
                error_count += 1
        
        logger.info(f"Worker {worker_id} completed - Processed: {processed_count}, Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Worker {worker_id} failed to initialize: {e}")
    finally:
        # Clean up
        if loader.connection:
            loader.disconnect()

class SpacesETLOrchestrator:
    """Spaces ETL Orchestrator - reads batch data from DO Spaces instead of local files"""
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.start_time = None
        self.total_batches = 0
        self.processed_batches = 0
        self.error_batches = 0
        self.total_products_processed = 0
        self.total_serving_processed = 0
        self.total_diet_claims_processed = 0
        self.total_image_urls_processed = 0
        self.total_nutrition_processed = 0
        self.total_allergen_processed = 0
        self.spaces_client = None
        self.spaces_bucket = None
        
    def setup_spaces_client(self):
        """Setup DigitalOcean Spaces client"""
        try:
            self.spaces_client, self.spaces_bucket = get_spaces_client()
            logger.info("DigitalOcean Spaces client configured")
        except Exception as e:
            logger.error(f"Failed to setup Spaces client: {e}")
            raise
    
    def get_batch_keys_from_spaces(self, session_id: str) -> List[str]:
        """Get all batch keys from DO Spaces for a specific session"""
        if not self.spaces_client:
            self.setup_spaces_client()
        
        session_prefix = f"incremental_batches/batch_{session_id}/"
        logger.info(f"Looking for batches in: {session_prefix}")
        
        try:
            # List objects in the session directory
            response = self.spaces_client.list_objects_v2(
                Bucket=self.spaces_bucket,
                Prefix=session_prefix
            )
            
            batch_keys = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.json'):
                    batch_keys.append(obj['Key'])
            
            batch_keys.sort()  # Process in order
            logger.info(f"Found {len(batch_keys)} batch files in DO Spaces")
            return batch_keys
            
        except Exception as e:
            logger.error(f"Failed to list objects from DO Spaces: {e}")
            raise
    
    def run_etl_from_spaces(self, session_id: str, max_batches: int = None, start_index: int = 0) -> Dict[str, Any]:
        """Run the ETL process using batch data from DO Spaces"""
        self.start_time = datetime.now()
        logger.info(f"Starting Spaces ETL process for session: {session_id}")
        
        try:
            # Get batch keys from DO Spaces
            batch_keys = self.get_batch_keys_from_spaces(session_id)
            if not batch_keys:
                logger.error("No batch files found in DO Spaces")
                return {
                    'status': 'failed',
                    'error': 'No batch files found in DO Spaces'
                }
            
            # Apply start index (skip first N batches)
            if start_index and start_index > 0:
                if start_index >= len(batch_keys):
                    logger.error(f"Start index {start_index} is beyond available batch count {len(batch_keys)}")
                    return {
                        'status': 'failed',
                        'error': f'start_index {start_index} >= total {len(batch_keys)}'
                    }
                batch_keys = batch_keys[start_index:]
                logger.info(f"Skipping first {start_index} batches. Remaining: {len(batch_keys)}")

            # Limit batches for testing if specified
            if max_batches and max_batches < len(batch_keys):
                original_total = len(batch_keys)
                batch_keys = batch_keys[:max_batches]
                logger.info(f"TEST MODE: Processing {max_batches} batches starting at index {start_index} (of {original_total} total)")
            
            self.total_batches = len(batch_keys)
            logger.info(f"Found {self.total_batches} batch files to process")
            
            # Create multiprocessing manager for queues
            with Manager() as manager:
                batch_queue = manager.Queue(maxsize=QUEUE_SIZE)
                result_queue = manager.Queue()
                
                # Start worker processes
                logger.info(f"Starting {self.max_workers} worker processes...")
                with Pool(processes=self.max_workers) as pool:
                    # Start workers
                    workers = []
                    for worker_id in range(self.max_workers):
                        worker = pool.apply_async(
                            worker_process_spaces, 
                            args=(worker_id, batch_queue, result_queue, DATABASE_URL)
                        )
                        workers.append(worker)
                    
                    # Feed batch keys to workers
                    logger.info(f"Feeding {len(batch_keys)} batch keys to workers...")
                    for batch_key in batch_keys:
                        try:
                            batch_queue.put(batch_key, timeout=10)  # 10 second timeout
                        except Exception as e:
                            logger.error(f"Failed to put batch {batch_key} in queue: {e}")
                            break
                    
                    # Send stop signals to workers
                    for _ in range(self.max_workers):
                        batch_queue.put("STOP")
                    
                    # Collect results
                    logger.info("Collecting results from workers...")
                    self._collect_results(result_queue, len(batch_keys))
                    
                    # Wait for workers to complete
                    for worker in workers:
                        worker.wait()
                
                logger.info("All workers completed")
            
            # Return final summary
            return self.get_summary()
            
        except Exception as e:
            logger.error(f"Spaces ETL process failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _collect_results(self, result_queue: Queue, expected_results: int):
        """Collect and process results from workers"""
        collected = 0
        
        while collected < expected_results:
            try:
                result = result_queue.get(timeout=1200)  # 20 minute timeout for batch processing (increased from 10 minutes)
                collected += 1
                
                if result['success']:
                    self.processed_batches += 1
                    batch_result = result['result']
                    
                    # Accumulate comprehensive statistics
                    self.total_products_processed += batch_result.get('products_processed', 0)
                    self.total_serving_processed += batch_result.get('serving_processed', 0)
                    self.total_diet_claims_processed += batch_result.get('diet_claims_processed', 0)
                    self.total_image_urls_processed += batch_result.get('image_urls_processed', 0)
                    self.total_nutrition_processed += batch_result.get('nutrition_processed', 0)
                    self.total_allergen_processed += batch_result.get('allergen_processed', 0)
                    
                    logger.debug(f"Batch {collected}/{expected_results} completed: "
                              f"Products: {batch_result.get('products_processed', 0)}, "
                              f"Serving: {batch_result.get('serving_processed', 0)}, "
                              f"Diet Claims: {batch_result.get('diet_claims_processed', 0)}, "
                              f"Image URLs: {batch_result.get('image_urls_processed', 0)}, "
                              f"Nutrition: {batch_result.get('nutrition_processed', 0)}, "
                              f"Allergen: {batch_result.get('allergen_processed', 0)}")
                else:
                    self.error_batches += 1
                    logger.error(f"Batch {collected}/{expected_results} failed: {result.get('error', 'Unknown error')}")
                
                # Progress update every 10 batches
                if collected % 10 == 0:
                    logger.info(f"Progress: {collected}/{expected_results} batches processed")
                    
                # Log individual batch completion like initial_load
                logger.info(f"Batch {collected}/{expected_results} completed: "
                          f"Products: {batch_result.get('products_processed', 0)}, "
                          f"Serving: {batch_result.get('serving_processed', 0)}, "
                          f"Diet Claims: {batch_result.get('diet_claims_processed', 0)}, "
                          f"Image URLs: {batch_result.get('image_urls_processed', 0)}, "
                          f"Nutrition: {batch_result.get('nutrition_processed', 0)}, "
                          f"Allergen: {batch_result.get('allergen_processed', 0)}")
                    
            except Empty:
                logger.warning("Timeout waiting for worker results")
                break
    
    def get_summary(self) -> Dict[str, Any]:
        """Get final processing summary"""
        if not self.start_time:
            return {'status': 'failed', 'error': 'No start time recorded'}
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        summary = {
            'status': 'success',
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_batches': self.total_batches,
            'processed_batches': self.processed_batches,
            'error_batches': self.error_batches,
            'success_rate': (self.processed_batches / self.total_batches * 100) if self.total_batches > 0 else 0,
            'products_processed': self.total_products_processed,
            'serving_processed': self.total_serving_processed,
            'diet_claims_processed': self.total_diet_claims_processed,
            'image_urls_processed': self.total_image_urls_processed,
            'nutrition_processed': self.total_nutrition_processed,
            'allergen_processed': self.total_allergen_processed
        }
        
        logger.info("=" * 80)
        logger.info("SPACES ETL PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Start time: {self.start_time}")
        logger.info(f"End time: {end_time}")
        logger.info(f"Duration: {duration}")
        logger.info(f"Total batches: {self.total_batches}")
        logger.info(f"Processed batches: {self.processed_batches}")
        logger.info(f"Error batches: {self.error_batches}")
        logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        logger.info("")
        logger.info("COMPREHENSIVE DATA PROCESSED:")
        logger.info(f"  Products processed: {self.total_products_processed:,}")
        logger.info(f"  Serving records processed: {self.total_serving_processed:,}")
        logger.info(f"  Diet claims processed: {self.total_diet_claims_processed:,}")
        logger.info(f"  Image URLs processed: {self.total_image_urls_processed:,}")
        logger.info(f"  Nutrition records processed: {self.total_nutrition_processed:,}")
        logger.info(f"  Allergen records processed: {self.total_allergen_processed:,}")
        logger.info("=" * 80)
        
        return summary

def main():
    """Main entry point for testing"""
    try:
        # Test with a specific session ID
        session_id = "20250820_221859"  # Replace with actual session ID
        
        orchestrator = SpacesETLOrchestrator(max_workers=MAX_WORKERS)
        result = orchestrator.run_etl_from_spaces(session_id)
        
        if result['status'] == 'success':
            logger.info("Spaces ETL process completed successfully")
        else:
            logger.error(f"Spaces ETL process failed: {result.get('error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Spaces ETL orchestrator failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
