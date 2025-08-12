#!/usr/bin/env python3
"""
ETL Orchestrator for OneWorldSync Data
- Loads nutrition and allergen data only from local files
- Processes data in parallel
- Handles batching efficiently
- Provides progress tracking and error handling
"""

import os
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import logging

# Import standalone loaders
from loaders.allergen_loader import AllergenLoader
from loaders.nutrition_loader import NutritionLoader

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

# Local data configuration
LOCAL_BATCHES_DIR = "downloaded_batches"  # Directory containing downloaded batch files

class ETLOrchestrator:
    """ETL Orchestrator for managing nutrition and allergen data loading from local files"""
    
    def __init__(self):
        # Initialize only nutrition and allergen loaders
        self.allergen_loader = AllergenLoader(DATABASE_URL)
        self.nutrition_loader = NutritionLoader(DATABASE_URL)
        
        # Statistics
        self.total_batches = 0
        self.total_products = 0
        self.start_time = None
        
        logger.info("Initialized ETL Orchestrator for nutrition and allergen loading from local files")
        
    def get_local_batch_files(self):
        """Get all JSON batch files from local directory"""
        try:
            if not os.path.exists(LOCAL_BATCHES_DIR):
                logger.error(f"Local batches directory not found: {LOCAL_BATCHES_DIR}")
                return []
                
            batch_files = []
            for root, dirs, files in os.walk(LOCAL_BATCHES_DIR):
                for file in files:
                    if file.endswith('_products.json'):
                        batch_files.append(os.path.join(root, file))
                        
            logger.info(f"Found {len(batch_files)} batch files in local directory")
            return batch_files
            
        except Exception as e:
            logger.error(f"Error getting local batch files: {e}")
            return []
            
    def load_batch_from_local(self, batch_file_path):
        """Load batch data from local file"""
        try:
            logger.info(f"Loading batch from local file: {batch_file_path}")
            
            with open(batch_file_path, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            logger.info(f"Loaded batch {batch_file_path}: {len(batch_data)} items")
            return batch_data
            
        except Exception as e:
            logger.error(f"Error loading batch {batch_file_path}: {e}")
            return None
    
    def process_nutrition_allergen_parallel(self, batch_data):
        """Process nutrition and allergen data in parallel"""
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
            
        logger.info(f"Processing {len(items)} items with nutrition and allergen loaders")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit loader tasks for nutrition and allergen only
            future_to_loader = {
                executor.submit(self.nutrition_loader.process_batch, items): "Nutrition",
                executor.submit(self.allergen_loader.process_batch, items): "Allergen"
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
            logger.info(f"Nutrition and allergen loaders completed in {total_time:.2f}s")
    
    def run_etl(self):
        """Run the complete ETL process for nutrition and allergen only from local files"""
        self.start_time = datetime.now()
        logger.info("Starting ETL process for nutrition and allergen data from local files...")
        
        # Step 1: Get local batch files
        batch_files = self.get_local_batch_files()
        if not batch_files:
            logger.error("No batch files found in local directory")
            return False
            
        self.total_batches = len(batch_files)
        logger.info(f"Processing {self.total_batches} batch files from local directory...")
        
        # Step 2: Process each batch file
        for i, batch_file_path in enumerate(batch_files, 1):
            logger.info(f"Processing batch file {i}/{self.total_batches}: {batch_file_path}")
            
            # Load batch data from local file
            batch_data = self.load_batch_from_local(batch_file_path)
            if not batch_data:
                logger.warning(f"No data in batch {batch_file_path}")
                continue
                
            # Extract products from batch data
            if isinstance(batch_data, dict) and "products" in batch_data:
                products_list = batch_data["products"]
                logger.info(f"Extracted {len(products_list)} products from batch")
            else:
                # Fallback: treat batch_data as products list directly
                products_list = batch_data
                logger.info(f"Using batch_data directly as products list: {len(products_list)} items")
                
            # Step 3: Process nutrition and allergen data in parallel
            logger.info(f"Processing nutrition and allergen data for {len(products_list)} products...")
            self.process_nutrition_allergen_parallel(products_list)
            
            logger.info(f"Completed batch file {i}/{self.total_batches}")
        
        # Step 4: Print final summary
        self.print_summary()
        return True
        
    def print_summary(self):
        """Print ETL summary for nutrition and allergen only"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("=" * 60)
        logger.info("ETL PROCESS COMPLETED - NUTRITION AND ALLERGEN ONLY")
        logger.info("=" * 60)
        logger.info(f"Total batches processed: {self.total_batches}")
        logger.info(f"Duration: {duration}")
        logger.info("")
        logger.info("LOADER STATISTICS:")
        logger.info(f"  Allergens: {self.allergen_loader.processed_count} processed, {self.allergen_loader.error_count} errors")
        logger.info(f"  Nutrition: {self.nutrition_loader.processed_count} processed, {self.nutrition_loader.error_count} errors")
        logger.info("")
        logger.info("=" * 60)

def main():
    """Main function"""
    try:
        orchestrator = ETLOrchestrator()
        
        # Run ETL process
        success = orchestrator.run_etl()
        
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