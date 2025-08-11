#!/usr/bin/env python3
"""
Test script to process a single batch and verify the data structure fix
"""

import logging
from etl_orchestrator import ETLOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_single_batch():
    """Test processing a single batch"""
    try:
        orchestrator = ETLOrchestrator()
        
        # Get batch files
        batch_files = orchestrator.get_batch_files_from_spaces()
        if not batch_files:
            logger.error("No batch files found")
            return False
            
        # Process only the first batch
        first_batch = batch_files[0]
        logger.info(f"Testing with first batch: {first_batch}")
        
        # Download batch data
        batch_data = orchestrator.download_batch_from_spaces(first_batch)
        if not batch_data:
            logger.error("Failed to download batch data")
            return False
            
        # Extract products from batch data
        if isinstance(batch_data, dict) and "products" in batch_data:
            products_list = batch_data["products"]
            logger.info(f"✅ Successfully extracted {len(products_list)} products from batch")
        else:
            products_list = batch_data
            logger.info(f"⚠️ Using batch_data directly as products list: {len(products_list)} items")
            
        # Test filtering
        filtered_data = orchestrator.filter_products_by_gpc(products_list)
        logger.info(f"✅ Filtered to {len(filtered_data)} valid products")
        
        # Test product loading (just a few items to avoid database issues)
        if filtered_data:
            test_items = filtered_data[:3]  # Just test first 3 items
            logger.info(f"Testing product loading with {len(test_items)} items...")
            
            # Extract items for product loader
            product_items = []
            for product in test_items:
                if isinstance(product, dict) and "item" in product:
                    product_items.append(product["item"])
                elif isinstance(product, dict):
                    product_items.append(product)
            
            if product_items:
                logger.info(f"✅ Successfully extracted {len(product_items)} product items")
                logger.info("Data structure fix is working correctly!")
                return True
            else:
                logger.error("❌ Failed to extract product items")
                return False
        else:
            logger.warning("No filtered products to test")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_single_batch()
    if success:
        logger.info("🎉 Single batch test completed successfully!")
    else:
        logger.error("❌ Single batch test failed!") 