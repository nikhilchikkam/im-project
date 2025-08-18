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

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
LOCAL_BATCHES_DIR = "downloaded_batches"
MAX_WORKERS = 4
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

class ETLOrchestrator:
    """ETL Orchestrator using process pools and staging tables"""
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.start_time = None
        self.total_batches = 0
        self.processed_batches = 0
        self.error_batches = 0
        self.total_nutrition_copied = 0
        self.total_allergen_copied = 0
        self.total_nutrition_merged = 0
        self.total_allergen_merged = 0
        self.checkpoint_manager = CheckpointManager(CHECKPOINT_FILE)
        
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
                result = result_queue.get(timeout=30)  # 30 second timeout
                collected += 1
                
                if result['success']:
                    self.processed_batches += 1
                    batch_result = result['result']
                    
                    # Save checkpoint for successfully processed batch
                    batch_file = result['batch_file']
                    batch_id = self.checkpoint_manager.get_batch_id(batch_file)
                    self.checkpoint_manager.save_checkpoint(batch_id)
                    
                    # Accumulate statistics
                    self.total_nutrition_copied += batch_result.get('nutrition_copied', 0)
                    self.total_allergen_copied += batch_result.get('allergen_copied', 0)
                    self.total_nutrition_merged += batch_result.get('nutrition_merged', 0)
                    self.total_allergen_merged += batch_result.get('allergen_merged', 0)
                    
                    logger.info(f"Batch {collected}/{expected_results} completed: "
                              f"{batch_result.get('nutrition_copied', 0)} nutrition, "
                              f"{batch_result.get('allergen_copied', 0)} allergen")
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
        logger.info(f"  Nutrition records copied: {self.total_nutrition_copied:,}")
        logger.info(f"  Allergen records copied: {self.total_allergen_copied:,}")
        logger.info(f"  Nutrition records merged: {self.total_nutrition_merged:,}")
        logger.info(f"  Allergen records merged: {self.total_allergen_merged:,}")
        logger.info("=" * 80)

def main():
    """Main entry point"""
    try:
        orchestrator = ETLOrchestrator(max_workers=MAX_WORKERS)
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