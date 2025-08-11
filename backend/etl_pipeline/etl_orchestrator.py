#!/usr/bin/env python3
"""
ETL Orchestrator for OneWorldSync Data
- Loads products first (maintaining FK integrity)
- Processes related data in parallel (after products exist)
- Handles batching efficiently
- Provides progress tracking and error handling
"""

import os
import json
import time
import boto3
import psycopg2
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import logging

# Import standalone loaders
from loaders.product_loader import ProductLoader
from loaders.allergen_loader import AllergenLoader
from loaders.nutrition_loader import NutritionLoader
from loaders.serving_loader import ServingLoader
from loaders.diet_claim_loader import DietClaimLoader
from loaders.image_url_loader import ImageURLLoader

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Spaces configuration
SPACES_ACCESS_KEY = os.getenv('SPACES_ACCESS_KEY')
SPACES_SECRET_KEY = os.getenv('SPACES_SECRET_KEY')
SPACES_REGION = os.getenv('SPACES_REGION', 'sfo3')
SPACES_BUCKET = os.getenv('SPACES_BUCKET', 'nutrigence-etl')

# Processing configuration
MAX_WORKERS = 8  # Increased to handle more parallel operations
BATCH_SIZE = 1000
RETRY_DELAY = 5
MAX_RETRIES = 3
MAX_CONCURRENT_BATCHES = 2  # Process multiple batches in parallel
ENABLE_PARALLEL_BATCHES = False  # Set to True to enable parallel batch processing

# Local storage configuration
LOCAL_BATCHES_DIR = "downloaded_batches"
KEEP_LOCAL_COPIES = True  # Set to False to delete local files after processing
MAX_LOCAL_STORAGE_GB = 10  # Maximum local storage in GB

class ETLOrchestrator:
    """ETL Orchestrator for managing the complete data pipeline"""
    
    def __init__(self):
        self.spaces_client = None
        self.bucket = None
        self.valid_gpc_codes = set()
        
        # Initialize loaders using imported classes
        self.product_loader = ProductLoader(DATABASE_URL)
        self.allergen_loader = AllergenLoader(DATABASE_URL)
        self.nutrition_loader = NutritionLoader(DATABASE_URL)
        self.serving_loader = ServingLoader(DATABASE_URL)
        self.diet_claim_loader = DietClaimLoader(DATABASE_URL)
        self.image_url_loader = ImageURLLoader(DATABASE_URL)
        
        # Statistics
        self.total_batches = 0
        self.total_products = 0
        self.start_time = None
        
        # Optimize worker counts based on system resources
        self.optimal_workers = self._calculate_optimal_workers()
        logger.info(f"Using {self.optimal_workers} workers for parallel processing")
        
    def get_spaces_client(self):
        """Get DigitalOcean Spaces client"""
        if not self.spaces_client:
            session = boto3.session.Session()
            self.spaces_client = session.client('s3',
                region_name=SPACES_REGION,
                endpoint_url=f'https://{SPACES_REGION}.digitaloceanspaces.com',
                aws_access_key_id=SPACES_ACCESS_KEY,
                aws_secret_access_key=SPACES_SECRET_KEY)
            self.bucket = SPACES_BUCKET
            
        return self.spaces_client, self.bucket
    
    def _calculate_optimal_workers(self):
        """Calculate optimal number of workers based on system resources"""
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            
            # For I/O-bound operations (database, network), we can use more workers than CPUs
            # Rule of thumb: 2-4x CPU count for I/O-bound tasks
            optimal = min(MAX_WORKERS, cpu_count * 3)
            
            # Ensure we have enough workers for our loaders
            min_workers = 5  # We have 5 loaders
            optimal = max(optimal, min_workers)
            
            logger.info(f"System has {cpu_count} CPUs, using {optimal} workers")
            return optimal
            
        except Exception as e:
            logger.warning(f"Could not determine optimal workers, using default: {e}")
            return MAX_WORKERS
        
    def download_excel_from_spaces(self):
        """Download Excel file from Spaces"""
        excel_file_local = "family_class_brick.xlsx"
        excel_file_spaces = "reference/family_class_brick.xlsx"
        
        if os.path.exists(excel_file_local):
            logger.info(f"Using local Excel file: {excel_file_local}")
            return True
            
        try:
            spaces_client, bucket = self.get_spaces_client()
            logger.info(f"Downloading Excel file from Spaces: {excel_file_spaces}")
            
            response = spaces_client.get_object(Bucket=bucket, Key=excel_file_spaces)
            with open(excel_file_local, 'wb') as f:
                f.write(response['Body'].read())
                
            logger.info(f"Downloaded Excel file: {excel_file_local}")
            return True
        except Exception as e:
            logger.error(f"Failed to download Excel file: {e}")
            return False
            
    def load_gpc_codes(self):
        """Load valid GPC codes from Excel file"""
        excel_file = "family_class_brick.xlsx"
        
        if not os.path.exists(excel_file):
            logger.error(f"Excel file not found: {excel_file}")
            return False
            
        try:
            df = pd.read_excel(excel_file)
            self.valid_gpc_codes = set(str(code).strip() for code in df["BrickCode"].dropna().astype(str))
            logger.info(f"Loaded {len(self.valid_gpc_codes)} valid GPC codes from Excel file")
            return True
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            return False
            
    def filter_products_by_gpc(self, products):
        """Filter products by GPC codes"""
        if not self.valid_gpc_codes:
            return products
            
        filtered_products = []
        for product in products:
            item = product.get("item", {})
            gpc_info = item.get("globalClassificationCategory", {})
            gpc_code = str(gpc_info.get("code", ""))
            
            if gpc_code and gpc_code in self.valid_gpc_codes:
                filtered_products.append(product)
                
        logger.info(f"Filtered {len(products)} products: {len(filtered_products)} valid")
        return filtered_products
        
    def get_batch_files_from_spaces(self, session_id=None):
        """Get batch files from Spaces"""
        try:
            spaces_client, bucket = self.get_spaces_client()
            
            if session_id:
                # If session_id is provided, look for individual JSON files within that session
                prefix = f"filtered_batches/batch_{session_id}/"
                batch_files = []
                
                # Handle pagination to get all files
                paginator = spaces_client.get_paginator('list_objects_v2')
                page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
                
                for page in page_iterator:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            if obj['Key'].endswith('.json'):
                                batch_files.append(obj['Key'])
                
                logger.info(f"Found {len(batch_files)} batch files in session {session_id}")
                return batch_files
            else:
                # If no session_id, look for batch session folders
                prefix = "filtered_batches/"
                response = spaces_client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter='/')
                batch_sessions = []
                
                if 'CommonPrefixes' in response:
                    for prefix_info in response['CommonPrefixes']:
                        session_path = prefix_info['Prefix']
                        if session_path.startswith('filtered_batches/batch_'):
                            batch_sessions.append(session_path.rstrip('/'))
                
                logger.info(f"Found {len(batch_sessions)} batch sessions")
                return batch_sessions
            
        except Exception as e:
            logger.error(f"Error getting batch files from Spaces: {e}")
            return []
            
    def download_batch_from_spaces(self, batch_key):
        """Download batch data from Spaces and optionally save locally"""
        try:
            # Check if we have a local copy first
            local_file = self._get_local_batch_path(batch_key)
            if os.path.exists(local_file):
                logger.info(f"Using local copy: {local_file}")
                with open(local_file, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                logger.info(f"Loaded local batch {batch_key}: {len(batch_data)} items")
                return batch_data
            
            # Download from Spaces if no local copy
            spaces_client, bucket = self.get_spaces_client()
            logger.info(f"Downloading batch: {batch_key}")
            
            response = spaces_client.get_object(Bucket=bucket, Key=batch_key)
            batch_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Save to local storage
            self._save_batch_locally(batch_key, batch_data)
            
            logger.info(f"Downloaded and saved batch {batch_key}: {len(batch_data)} items")
            return batch_data
            
        except Exception as e:
            logger.error(f"Error downloading batch {batch_key}: {e}")
            return None
            
    def _get_local_batch_path(self, batch_key):
        """Get local file path for a batch"""
        # Create batches directory if it doesn't exist
        if not os.path.exists(LOCAL_BATCHES_DIR):
            os.makedirs(LOCAL_BATCHES_DIR)
            
        # Convert batch key to safe filename
        safe_filename = batch_key.replace('/', '_').replace('\\', '_')
        return os.path.join(LOCAL_BATCHES_DIR, safe_filename)
        
    def _save_batch_locally(self, batch_key, batch_data):
        """Save batch data to local file"""
        try:
            local_file = self._get_local_batch_path(batch_key)
            with open(local_file, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved batch locally: {local_file}")
        except Exception as e:
            logger.warning(f"Failed to save batch locally: {e}")
            
    def cleanup_local_batches(self):
        """Clean up local batch files if configured to do so"""
        if not KEEP_LOCAL_COPIES:
            try:
                if os.path.exists(LOCAL_BATCHES_DIR):
                    import shutil
                    shutil.rmtree(LOCAL_BATCHES_DIR)
                    logger.info(f"Cleaned up local batch directory: {LOCAL_BATCHES_DIR}")
            except Exception as e:
                logger.warning(f"Failed to cleanup local batches: {e}")
                
    def get_local_storage_info(self):
        """Get information about local storage usage"""
        if not os.path.exists(LOCAL_BATCHES_DIR):
            return {"exists": False, "size_mb": 0, "file_count": 0}
            
        try:
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(LOCAL_BATCHES_DIR):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                    
            size_mb = total_size / (1024 * 1024)
            return {
                "exists": True,
                "size_mb": round(size_mb, 2),
                "file_count": file_count
            }
        except Exception as e:
            logger.error(f"Error getting local storage info: {e}")
            return {"exists": False, "size_mb": 0, "file_count": 0}
            
    def process_batch_parallel(self, batch_data):
        """Process related data in parallel using ThreadPoolExecutor"""
        # Extract items from batch_data for the loaders
        items = []
        for product in batch_data:
            if isinstance(product, dict) and "item" in product:
                items.append(product["item"])
            elif isinstance(product, dict):
                # If the product itself is the item
                items.append(product)
                
        if not items:
            logger.warning("No valid items found in batch data")
            return
            
        logger.info(f"Processing {len(items)} items with related data loaders")
        
        # Use optimal number of workers for the number of loaders
        optimal_workers = min(self.optimal_workers, 5)  # 5 loaders
        
        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            # Submit loader tasks with the extracted items (excluding nutrition and allergens)
            future_to_loader = {
                executor.submit(self.serving_loader.process_batch, items): "Serving",
                executor.submit(self.diet_claim_loader.process_batch, items): "Diet Claims",
                executor.submit(self.image_url_loader.process_batch, items): "Image URLs"
            }
            
            # Process completed tasks with better error handling and timing
            start_time = time.time()
            completed_loaders = 0
            total_loaders = len(future_to_loader)
            
            for future in as_completed(future_to_loader):
                loader_name = future_to_loader[future]
                try:
                    processed_count = future.result()
                    completed_loaders += 1
                    elapsed = time.time() - start_time
                    logger.info(f"{loader_name} processed {processed_count} items in {elapsed:.2f}s ({completed_loaders}/{total_loaders} loaders complete)")
                except Exception as e:
                    logger.error(f"{loader_name} failed: {e}")
                    completed_loaders += 1
            
            total_time = time.time() - start_time
            logger.info(f"All loaders completed in {total_time:.2f}s")
    
    def process_batches_parallel(self, batch_files):
        """Process multiple batches in parallel using ThreadPoolExecutor"""
        logger.info(f"Processing {len(batch_files)} batches in parallel with max {MAX_CONCURRENT_BATCHES} concurrent")
        
        def process_single_batch(batch_key):
            """Process a single batch - extracted for parallel execution"""
            try:
                logger.info(f"Processing batch: {batch_key}")
                
                # Download batch data
                batch_data = self.download_batch_from_spaces(batch_key)
                if not batch_data:
                    logger.warning(f"No data in batch {batch_key}")
                    return {"batch": batch_key, "status": "no_data", "products": 0}
                
                # Extract products from batch data
                if isinstance(batch_data, dict) and "products" in batch_data:
                    products_list = batch_data["products"]
                else:
                    products_list = batch_data
                
                # Filter by GPC codes
                filtered_data = self.filter_products_by_gpc(products_list)
                if not filtered_data:
                    logger.info(f"No valid products in batch {batch_key}")
                    return {"batch": batch_key, "status": "no_valid_products", "products": 0}
                
                # Load products first
                product_items = []
                for product in filtered_data:
                    if isinstance(product, dict) and "item" in product:
                        product_items.append(product["item"])
                    elif isinstance(product, dict):
                        product_items.append(product)
                
                if product_items:
                    self.product_loader.process_batch(product_items)
                    self.total_products += len(product_items)
                
                # Process related data in parallel
                self.process_batch_parallel(filtered_data)
                
                return {"batch": batch_key, "status": "success", "products": len(product_items)}
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_key}: {e}")
                return {"batch": batch_key, "status": "error", "error": str(e)}
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_BATCHES) as executor:
            # Submit all batch processing tasks
            future_to_batch = {
                executor.submit(process_single_batch, batch_key): batch_key 
                for batch_key in batch_files
            }
            
            # Process completed batches
            completed_batches = 0
            start_time = time.time()
            
            for future in as_completed(future_to_batch):
                batch_key = future_to_batch[future]
                try:
                    result = future.result()
                    completed_batches += 1
                    elapsed = time.time() - start_time
                    
                    if result["status"] == "success":
                        logger.info(f"✅ Batch {batch_key} completed: {result['products']} products ({completed_batches}/{len(batch_files)} batches)")
                    else:
                        logger.warning(f"⚠️ Batch {batch_key} status: {result['status']} ({completed_batches}/{len(batch_files)} batches)")
                        
                except Exception as e:
                    logger.error(f"❌ Batch {batch_key} failed: {e}")
                    completed_batches += 1
            
            total_time = time.time() - start_time
            logger.info(f"All batches completed in {total_time:.2f}s")
                    
    def run_etl(self, session_id=None):
        """Run the complete ETL process"""
        self.start_time = datetime.now()
        logger.info("Starting ETL process...")
        
        # Step 1: Load GPC codes for filtering
        if not self.load_gpc_codes():
            logger.error("Failed to load GPC codes")
            return False
            
        # Step 2: Get batch files from Spaces
        if session_id:
            # Process a specific session - get individual batch files
            batch_files = self.get_batch_files_from_spaces(session_id)
            if not batch_files:
                logger.error(f"No batch files found in session {session_id}")
                return False
                
            self.total_batches = len(batch_files)
            logger.info(f"Processing {self.total_batches} batch files in session {session_id}...")
            
            # Process individual batch files
            self._process_batch_files(batch_files)
        else:
            # Process all sessions - get session folders
            batch_sessions = self.get_batch_files_from_spaces()
            if not batch_sessions:
                logger.error("No batch sessions found")
                return False
                
            self.total_batches = len(batch_sessions)
            logger.info(f"Processing {self.total_batches} batch sessions...")
            
            # Process each session folder
            for i, session_path in enumerate(batch_sessions, 1):
                logger.info(f"Processing session {i}/{self.total_batches}: {session_path}")
                
                # Extract session ID from path (remove 'batch_' prefix)
                session_id = session_path.split('/')[-1].replace('batch_', '')
                
                # Get batch files for this session
                batch_files = self.get_batch_files_from_spaces(session_id)
                if not batch_files:
                    logger.warning(f"No batch files found in session {session_id}")
                    continue
                    
                logger.info(f"Processing {len(batch_files)} batch files in session {session_id}")
                self._process_batch_files(batch_files)
                
                logger.info(f"Completed session {i}/{self.total_batches}: {session_id}")
        
        # Step 6: Clean up local files if configured
        if not KEEP_LOCAL_COPIES:
            self.cleanup_local_batches()
            
        # Step 7: Print final summary
        self.print_summary()
        return True
            
        # Step 6: Clean up local files if configured
        if not KEEP_LOCAL_COPIES:
            self.cleanup_local_batches()
            
        # Step 7: Print final summary
        self.print_summary()
        return True
        
    def _process_batch_files(self, batch_files):
        """Process individual batch files"""
        for i, batch_key in enumerate(batch_files, 1):
            # Skip first 2 batches
            if i <= 2:
                logger.info(f"Skipping batch file {i}/{len(batch_files)}: {batch_key}")
                continue
                
            logger.info(f"Processing batch file {i}/{len(batch_files)}: {batch_key}")
            
            # Download batch data
            batch_data = self.download_batch_from_spaces(batch_key)
            if not batch_data:
                logger.warning(f"No data in batch {batch_key}")
                continue
                
            # Extract products from batch data
            if isinstance(batch_data, dict) and "products" in batch_data:
                products_list = batch_data["products"]
                logger.info(f"Extracted {len(products_list)} products from batch")
            else:
                # Fallback: treat batch_data as products list directly
                products_list = batch_data
                logger.info(f"Using batch_data directly as products list: {len(products_list)} items")
                
            # Debug: Log the structure of the first item
            if products_list and len(products_list) > 0:
                first_item = products_list[0]
                logger.info(f"Sample data structure - Type: {type(first_item)}, Keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                if isinstance(first_item, dict) and "item" in first_item:
                    logger.info(f"Item structure - Keys: {list(first_item['item'].keys()) if isinstance(first_item['item'], dict) else 'Not a dict'}")
                
            # Filter by GPC codes
            filtered_data = self.filter_products_by_gpc(products_list)
            if not filtered_data:
                logger.info(f"No valid products in batch {batch_key}")
                continue
                
            # Step 4: Load products first (maintaining FK integrity)
            logger.info(f"Loading {len(filtered_data)} products...")
            
            # Extract items for product loader
            product_items = []
            for product in filtered_data:
                if isinstance(product, dict) and "item" in product:
                    product_items.append(product["item"])
                elif isinstance(product, dict):
                    product_items.append(product)
            
            if product_items:
                self.product_loader.process_batch(product_items)
                self.total_products += len(product_items)
                logger.info(f"Successfully loaded {len(product_items)} products")
            else:
                logger.warning("No valid product items found in filtered data")
            
            # Step 5: Process related data in parallel
            logger.info(f"Processing related data for {len(filtered_data)} products...")
            self.process_batch_parallel(filtered_data)
            
            logger.info(f"Completed batch file {i}/{len(batch_files)}")
        
    def print_summary(self):
        """Print ETL summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("=" * 60)
        logger.info("ETL PROCESS COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Total batches processed: {self.total_batches}")
        logger.info(f"Total products loaded: {self.total_products}")
        logger.info(f"Duration: {duration}")
        logger.info("")
        logger.info("LOADER STATISTICS:")
        logger.info(f"  Products: {self.product_loader.processed_count} processed, {self.product_loader.error_count} errors")
        logger.info(f"  Allergens: {self.allergen_loader.processed_count} processed, {self.allergen_loader.error_count} errors")
        logger.info(f"  Nutrition: {self.nutrition_loader.processed_count} processed, {self.nutrition_loader.error_count} errors")
        logger.info(f"  Serving: {self.serving_loader.processed_count} processed, {self.serving_loader.error_count} errors")
        logger.info(f"  Diet Claims: {self.diet_claim_loader.processed_count} processed, {self.diet_claim_loader.error_count} errors")
        logger.info(f"  Image URLs: {self.image_url_loader.processed_count} processed, {self.image_url_loader.error_count} errors")
        logger.info("")
        
        # Local storage information
        storage_info = self.get_local_storage_info()
        if storage_info["exists"]:
            logger.info("LOCAL STORAGE:")
            logger.info(f"  Directory: {LOCAL_BATCHES_DIR}")
            logger.info(f"  Size: {storage_info['size_mb']} MB")
            logger.info(f"  Files: {storage_info['file_count']}")
            if not KEEP_LOCAL_COPIES:
                logger.info("  Note: Local files will be cleaned up")
        logger.info("=" * 60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Orchestrator for OneWorldSync Data')
    parser.add_argument('--session-id', help='Process only files from a specific session')
    parser.add_argument('--estimate', action='store_true', help='Estimate processing time')
    
    args = parser.parse_args()
    
    try:
        orchestrator = ETLOrchestrator()
        
        if args.estimate:
            # Estimate processing time
            batch_files = orchestrator.get_batch_files_from_spaces(args.session_id)
            estimated_time = len(batch_files) * 30  # 30 seconds per batch estimate
            logger.info(f"Estimated processing time: {estimated_time/60:.1f} minutes for {len(batch_files)} batches")
            return
            
        # Run ETL process
        success = orchestrator.run_etl(args.session_id)
        
        if success:
            logger.info("ETL process completed successfully!")
        else:
            logger.error("ETL process failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    main() 