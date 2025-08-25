#!/usr/bin/env python3
"""
ETL Orchestrator for batch-parallel processing with staging tables
Uses process pools instead of thread pools for better performance
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

from loaders.batch_loader import BatchLoader
from config import ETLConfig
from utils import get_spaces_client, filter_products_by_gpc, load_gpc_codes

# Load environment variables
load_dotenv('../../.env')  # backend/.env


# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
LOCAL_BATCHES_DIR = "downloaded_batches"
MAX_WORKERS = ETLConfig.ETL_MAX_WORKERS
QUEUE_SIZE = 10
CHECKPOINT_FILE = "etl_checkpoint.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CheckpointManager:
    """Manages checkpointing to track processed batches"""
    
    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = checkpoint_file
        self.processed_batches = self._load_checkpoint()
    
    def _load_checkpoint(self) -> set:
        """Load processed batch IDs from checkpoint file"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_batches', []))
            return set()
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
            return set()
    
    def save_checkpoint(self, batch_id: str):
        """Save a batch as processed"""
        self.processed_batches.add(batch_id)
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    'processed_batches': list(self.processed_batches),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save checkpoint: {e}")
    
    def is_processed(self, batch_id: str) -> bool:
        """Check if a batch has been processed"""
        return batch_id in self.processed_batches
    
    def get_batch_id(self, batch_file_path: str) -> str:
        """Extract batch ID from file path"""
        filename = os.path.basename(batch_file_path)
        # Extract batch number from filename like "filtered_batches_batch_session_20250808_155051_batch_0159_products.json"
        if 'batch_' in filename:
            parts = filename.split('_')
            for i, part in enumerate(parts):
                if part == 'batch' and i + 1 < len(parts):
                    return parts[i + 1]  # Return the batch number
        return filename  # Fallback to full filename

def worker_process(worker_id: int, batch_queue: Queue, result_queue: Queue, database_url: str):
    """
    Worker process that processes batches using staging tables
    
    Args:
        worker_id: Unique identifier for this worker
        batch_queue: Queue containing batch file paths to process
        result_queue: Queue to send results back to main process
        database_url: Database connection string
    """
    logger.info(f"Worker {worker_id} started")
    
    # Create loader instance for this worker
    loader = BatchLoader(database_url)
    
    try:
        # Connect to database and prepare staging tables
        loader.connect()
        loader.prepare_staging()
        
        processed_count = 0
        error_count = 0
        
        while True:
            try:
                # Get batch file path from queue (timeout to allow graceful shutdown)
                batch_file_path = batch_queue.get(timeout=1)
                
                if batch_file_path == "STOP":
                    logger.info(f"Worker {worker_id} received stop signal")
                    break
                
                logger.info(f"Worker {worker_id} processing: {batch_file_path}")
                
                # Load batch data from file
                try:
                    with open(batch_file_path, 'r', encoding='utf-8') as f:
                        batch_data = json.load(f)
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to load batch file {batch_file_path}: {e}")
                    error_count += 1
                    continue
                
                # Process batch using staging tables
                try:
                    result = loader.process_batch(batch_data)
                    processed_count += 1
                    
                    # Send result back to main process
                    result_queue.put({
                        'worker_id': worker_id,
                        'batch_file': batch_file_path,
                        'result': result,
                        'success': True
                    })
                    
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to process batch {batch_file_path}: {e}")
                    error_count += 1
                    
                    # Send error result back to main process
                    result_queue.put({
                        'worker_id': worker_id,
                        'batch_file': batch_file_path,
                        'error': str(e),
                        'success': False
                    })
                
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

def worker_process_spaces(worker_id: int, batch_queue: Queue, result_queue: Queue, database_url: str):
    """
    Worker process that processes batches directly from Spaces using staging tables
    
    Args:
        worker_id: Unique identifier for this worker
        batch_queue: Queue containing batch keys from Spaces to process
        result_queue: Queue to send results back to main process
        database_url: Database connection string
    """
    logger.info(f"Worker {worker_id} started (Spaces mode)")
    
    # Create loader instance for this worker
    loader = BatchLoader(database_url)
    
    try:
        # Connect to database and prepare staging tables
        loader.connect()
        loader.prepare_staging()
        
        # Create spaces client for this worker (avoid multiprocessing serialization issues)
        from utils import get_spaces_client
        spaces_client, spaces_bucket = get_spaces_client()
        
        processed_count = 0
        error_count = 0
        
        while True:
            try:
                # Get batch key from queue (timeout to allow graceful shutdown)
                batch_key = batch_queue.get(timeout=1)
                
                if batch_key == "STOP":
                    logger.info(f"Worker {worker_id} received stop signal")
                    break
                
                logger.info(f"Worker {worker_id} processing from Spaces: {batch_key}")
                
                # Load batch data directly from Spaces
                try:
                    response = spaces_client.get_object(Bucket=spaces_bucket, Key=batch_key)
                    batch_data = json.loads(response['Body'].read().decode('utf-8'))
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to load batch from Spaces {batch_key}: {e}")
                    error_count += 1
                    continue
                
                # Process batch using staging tables
                try:
                    result = loader.process_batch(batch_data)
                    processed_count += 1
                    
                    # Send result back to main process
                    result_queue.put({
                        'worker_id': worker_id,
                        'batch_file': batch_key,  # Use batch_key as batch_file for consistency
                        'result': result,
                        'success': True
                    })
                    
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed to process batch {batch_key}: {e}")
                    error_count += 1
                    
                    # Send error result back to main process
                    result_queue.put({
                        'worker_id': worker_id,
                        'batch_file': batch_key,
                        'error': str(e),
                        'success': False
                    })
                
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

class ETLOrchestrator:
    """ETL Orchestrator using process pools and staging tables"""
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.start_time = None
        self.total_batches = 0
        self.processed_batches = 0
        self.error_batches = 0
        # Track all data types
        self.total_products_copied = 0
        self.total_serving_copied = 0
        self.total_diet_claims_copied = 0
        self.total_image_urls_copied = 0
        self.total_nutrition_copied = 0
        self.total_allergen_copied = 0
        self.total_products_merged = 0
        self.total_serving_merged = 0
        self.total_diet_claims_merged = 0
        self.total_image_urls_merged = 0
        self.total_nutrition_merged = 0
        self.total_allergen_merged = 0
        self.checkpoint_manager = CheckpointManager(CHECKPOINT_FILE)
        self.spaces_client = None
        self.spaces_bucket = None
        
    def get_batch_files(self) -> List[str]:
        """Get all batch file paths from local directory, starting from batch 1090, skipping already processed"""
        if not os.path.exists(LOCAL_BATCHES_DIR):
            raise FileNotFoundError(f"Local batches directory not found: {LOCAL_BATCHES_DIR}")
        
        batch_files = []
        for filename in os.listdir(LOCAL_BATCHES_DIR):
            if filename.endswith('.json'):
                batch_files.append(os.path.join(LOCAL_BATCHES_DIR, filename))
        
        batch_files.sort()  # Process in order
        
        # Start from batch 1090 (skip first 1089 batches)
        if len(batch_files) > 1089:
            batch_files = batch_files[1089:]  # Start from index 1089 (batch 1090)
            logger.info(f"Starting from batch 1090. Skipping first 1089 batches.")
        else:
            logger.warning(f"Only {len(batch_files)} batch files found. Processing all available batches.")
        
        # Filter out already processed batches
        unprocessed_batches = []
        skipped_count = 0
        
        for batch_file in batch_files:
            batch_id = self.checkpoint_manager.get_batch_id(batch_file)
            if self.checkpoint_manager.is_processed(batch_id):
                skipped_count += 1
                logger.debug(f"Skipping already processed batch: {batch_id}")
            else:
                unprocessed_batches.append(batch_file)
        
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} already processed batches")
        
        logger.info(f"Remaining batches to process: {len(unprocessed_batches)}")
        return unprocessed_batches
    
    def setup_spaces_client(self):
        """Setup DigitalOcean Spaces client"""
        try:
            self.spaces_client, self.spaces_bucket = get_spaces_client()
            logger.info("DigitalOcean Spaces client configured")
        except Exception as e:
            logger.error(f"Failed to setup Spaces client: {e}")
            raise
    
    def fetch_incremental_data(self) -> List[Dict[str, Any]]:
        """Fetch incremental data from OWS with date filtering"""
        try:
            # Try different import patterns for oneworldsync (same as manual ETL)
            try:
                from oneworldsync import Content1Client, AuthenticationError, APIError
                logger.info("Successfully imported Content1Client from oneworldsync")
                client = Content1Client()
            except ImportError:
                try:
                    from oneworldsync import Client as Content1Client, AuthenticationError, APIError
                    logger.info("Successfully imported Client as Content1Client from oneworldsync")
                    client = Content1Client()
                except ImportError:
                    # Last resort: try importing everything from oneworldsync
                    import oneworldsync
                    logger.info(f"Available in oneworldsync: {dir(oneworldsync)}")
                    
                    if hasattr(oneworldsync, 'Client'):
                        client = oneworldsync.Client()
                    elif hasattr(oneworldsync, 'Content1Client'):
                        client = oneworldsync.Content1Client()
                    else:
                        raise ImportError("No suitable client found in oneworldsync library")
            
            # Get date range and build criteria
            start_date, end_date = ETLConfig.get_date_range()
            criteria = ETLConfig.build_incremental_criteria()
            
            logger.info(f"Fetching incremental data from {start_date} to {end_date}")
            logger.info(f"Date criteria: {criteria}")
            
            # Cache GPC codes once at the beginning (same as manual ETL)
            valid_gpc_codes = load_gpc_codes()
            logger.info(f"Cached {len(valid_gpc_codes)} GPC codes for filtering")
            
            batches = []
            search_after = None
            
            while True:
                # Fetching batch (searchAfter logging removed for brevity)
                
                # Update criteria with searchAfter if we have it
                current_criteria = criteria.copy()
                if search_after:
                    current_criteria["searchAfter"] = search_after
                
                # Fetch batch from OWS using page_size parameter
                response = client.fetch_products(criteria=current_criteria, page_size=ETLConfig.OWS_BATCH_SIZE)
                products = response.get('items', [])
                
                # Debug logging removed for performance
                
                if not products:
                    logger.info("No more products found")
                    break
                
                # Filter by GPC codes using cached codes (performance improvement)
                filtered_products = filter_products_by_gpc(products, valid_gpc_codes)
                logger.info(f"Batch {len(batches)+1}: {len(filtered_products)} valid GPC products from {len(products)} total")
                
                # Add filtered batch
                batches.append(filtered_products)
                
                # Get search_after for next batch (it's directly in response, not under pagination)
                search_after = response.get('searchAfter')
                if not search_after:
                    logger.info("No more searchAfter, finished fetching")
                    break
                
                # Removed verbose searchAfter logging
            
            logger.info(f"Successfully fetched {len(batches)} batches from OWS API with date filtering")
            return batches
            
        except ImportError:
            logger.error("oneworldsync library not found. Please install it: pip install oneworldsync")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch incremental data: {e}")
            raise
    
    def save_batches_to_spaces(self, batches: List[Dict[str, Any]], session_id: str) -> List[str]:
        """Save batches to DigitalOcean Spaces with retry logic"""
        try:
            if not self.spaces_client:
                self.setup_spaces_client()
            
            batch_keys = []
            for i, batch in enumerate(batches):
                batch_key = f"incremental_batches/batch_{session_id}/incremental_batch_{session_id}_batch_{i:04d}_products.json"
                
                # Save to Spaces with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.spaces_client.put_object(
                            Bucket=self.spaces_bucket,
                            Key=batch_key,
                            Body=json.dumps({'products': batch}, indent=2),
                            ContentType='application/json'
                        )
                        break  # Success, exit retry loop
                    except Exception as retry_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"Retry {attempt + 1}/{max_retries} for batch {i+1}: {retry_error}")
                            time.sleep(2 ** attempt)  # Exponential backoff
                            # Recreate client on connection issues
                            if "Connection" in str(retry_error):
                                self.setup_spaces_client()
                        else:
                            raise retry_error
                
                batch_keys.append(batch_key)
                logger.info(f"Saved batch {i+1}/{len(batches)} to Spaces: {batch_key}")
            
            return batch_keys
            
        except Exception as e:
            logger.error(f"Failed to save batches to Spaces: {e}")
            raise
    
    def run_etl_from_spaces(self, batch_keys: List[str]) -> bool:
        """Run ETL process directly from Spaces without downloading to local"""
        self.start_time = datetime.now()
        logger.info("Starting ETL process from Spaces with batch-parallel architecture...")
        
        try:
            if not batch_keys:
                logger.error("No batch keys provided")
                return False
            
            self.total_batches = len(batch_keys)
            logger.info(f"Found {self.total_batches} batch files in Spaces to process")
            
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
                    logger.info("Feeding batch keys to workers...")
                    for batch_key in batch_keys:
                        batch_queue.put(batch_key)
                    
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
            
            # Print final summary
            self.print_summary()
            return True
            
        except Exception as e:
            logger.error(f"ETL process from Spaces failed: {e}")
            return False
    
    def run_incremental_etl(self) -> bool:
        """Run complete incremental ETL: OWS -> Spaces -> Database"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Starting incremental ETL process (session: {session_id})")
        
        try:
            # Step 1: Fetch incremental data from OWS
            logger.info("Step 1: Fetching incremental data from OWS...")
            batches = self.fetch_incremental_data()
            
            if not batches:
                logger.info("No incremental data found")
                return True
            
            # Step 2: Save batches to Spaces
            logger.info("Step 2: Saving batches to Spaces...")
            batch_keys = self.save_batches_to_spaces(batches, session_id)
            
            # Step 3: Run ETL process directly from Spaces
            logger.info("Step 3: Running ETL process directly from Spaces...")
            return self.run_etl_from_spaces(batch_keys)
            
        except Exception as e:
            logger.error(f"Incremental ETL process failed: {e}")
            return False
    
    def run_etl(self) -> bool:
        """Run the complete ETL process using process pools"""
        self.start_time = datetime.now()
        logger.info("Starting ETL process with batch-parallel architecture...")
        
        try:
            # Get batch files
            batch_files = self.get_batch_files()
            if not batch_files:
                logger.error("No batch files found in local directory")
                return False
            
            self.total_batches = len(batch_files)
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
                            worker_process, 
                            args=(worker_id, batch_queue, result_queue, DATABASE_URL)
                        )
                        workers.append(worker)
                    
                    # Feed batch files to workers
                    logger.info("Feeding batch files to workers...")
                    for batch_file in batch_files:
                        batch_queue.put(batch_file)
                    
                    # Send stop signals to workers
                    for _ in range(self.max_workers):
                        batch_queue.put("STOP")
                    
                    # Collect results
                    logger.info("Collecting results from workers...")
                    self._collect_results(result_queue, len(batch_files))
                    
                    # Wait for workers to complete
                    for worker in workers:
                        worker.wait()
                
                logger.info("All workers completed")
            
            # Print final summary
            self.print_summary()
            return True
            
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            return False
    
    def _collect_results(self, result_queue: Queue, expected_results: int):
        """Collect and process results from workers"""
        collected = 0
        
        while collected < expected_results:
            try:
                result = result_queue.get(timeout=1800)  # 30 minute timeout for large batch processing
                collected += 1
                
                if result['success']:
                    self.processed_batches += 1
                    batch_result = result['result']
                    
                    # Save checkpoint for successfully processed batch
                    batch_file = result['batch_file']
                    # For Spaces mode, use the batch key as the batch ID
                    if batch_file.startswith('incremental_batches/'):
                        batch_id = batch_file  # Use full batch key as ID
                    else:
                        batch_id = self.checkpoint_manager.get_batch_id(batch_file)
                    self.checkpoint_manager.save_checkpoint(batch_id)
                    
                    # Accumulate statistics for all data types
                    self.total_products_copied += batch_result.get('products_copied', 0)
                    self.total_serving_copied += batch_result.get('serving_copied', 0)
                    self.total_diet_claims_copied += batch_result.get('diet_claims_copied', 0)
                    self.total_image_urls_copied += batch_result.get('image_urls_copied', 0)
                    self.total_nutrition_copied += batch_result.get('nutrition_copied', 0)
                    self.total_allergen_copied += batch_result.get('allergen_copied', 0)
                    self.total_products_merged += batch_result.get('products_merged', 0)
                    self.total_serving_merged += batch_result.get('serving_merged', 0)
                    self.total_diet_claims_merged += batch_result.get('diet_claims_merged', 0)
                    self.total_image_urls_merged += batch_result.get('image_urls_merged', 0)
                    self.total_nutrition_merged += batch_result.get('nutrition_merged', 0)
                    self.total_allergen_merged += batch_result.get('allergen_merged', 0)
                    
                    logger.info(f"Batch {collected}/{expected_results} processed: "
                              f"{batch_result.get('products_copied', 0)} products, "
                              f"{batch_result.get('nutrition_copied', 0)} nutrition, "
                              f"{batch_result.get('allergen_copied', 0)} allergens")
                else:
                    self.error_batches += 1
                    logger.error(f"Batch {collected}/{expected_results} failed: {result.get('error', 'Unknown error')}")
                
                # Progress update every 100 batches
                if collected % 100 == 0:
                    logger.info(f"Progress: {collected}/{expected_results} batches processed")
                    
            except Empty:
                logger.warning("Timeout waiting for worker results")
                break
    
    def print_summary(self):
        """Print final processing summary"""
        if not self.start_time:
            return
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("=" * 80)
        logger.info("ETL PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Start time: {self.start_time}")
        logger.info(f"End time: {end_time}")
        logger.info(f"Duration: {duration}")
        logger.info(f"Total batches: {self.total_batches}")
        logger.info(f"Processed batches: {self.processed_batches}")
        logger.info(f"Error batches: {self.error_batches}")
        logger.info(f"Success rate: {(self.processed_batches / self.total_batches * 100):.1f}%")
        logger.info("")
        logger.info("DATA PROCESSED:")
        logger.info(f"  Products copied: {self.total_products_copied:,}")
        logger.info(f"  Serving records copied: {self.total_serving_copied:,}")
        logger.info(f"  Diet claims copied: {self.total_diet_claims_copied:,}")
        logger.info(f"  Image URLs copied: {self.total_image_urls_copied:,}")
        logger.info(f"  Nutrition records copied: {self.total_nutrition_copied:,}")
        logger.info(f"  Allergen records copied: {self.total_allergen_copied:,}")
        logger.info("")
        logger.info("DATA MERGED:")
        logger.info(f"  Products merged: {self.total_products_merged:,}")
        logger.info(f"  Serving records merged: {self.total_serving_merged:,}")
        logger.info(f"  Diet claims merged: {self.total_diet_claims_merged:,}")
        logger.info(f"  Image URLs merged: {self.total_image_urls_merged:,}")
        logger.info(f"  Nutrition records merged: {self.total_nutrition_merged:,}")
        logger.info(f"  Allergen records merged: {self.total_allergen_merged:,}")
        logger.info("=" * 80)

def main():
    """Main entry point"""
    try:
        orchestrator = ETLOrchestrator(max_workers=MAX_WORKERS)
        
        # Check if we should run incremental ETL or standard ETL
        run_incremental = os.getenv('RUN_INCREMENTAL', 'true').lower() == 'true'
        
        if run_incremental:
            logger.info("Running incremental ETL (OWS -> Spaces -> Database)")
            success = orchestrator.run_incremental_etl()
        else:
            logger.info("Running standard ETL (local files -> Database)")
            success = orchestrator.run_etl()
        
        if success:
            logger.info("ETL process completed successfully")
        else:
            logger.error("ETL process failed")
            return 1
            
    except Exception as e:
        logger.error(f"ETL orchestrator failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 