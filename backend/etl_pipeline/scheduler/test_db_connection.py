#!/usr/bin/env python3
"""
Simple test script to check database connection and BatchLoader functionality
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_db_connection():
    """Test database connection and BatchLoader"""
    logger.info("🧪 Testing Database Connection and BatchLoader...")
    
    try:
        # Import the BatchLoader from initial_load
        from initial_load.loaders.batch_loader import BatchLoader
        from initial_load.config import ETLConfig
        
        logger.info("✅ Successfully imported BatchLoader from initial_load")
        
        # Create loader instance
        logger.info("Creating BatchLoader instance...")
        loader = BatchLoader(ETLConfig.DATABASE_URL)
        
        # Test connection
        logger.info("Testing database connection...")
        loader.connect()
        logger.info("✅ Database connection successful")
        
        # Test staging tables
        logger.info("Testing staging tables preparation...")
        loader.prepare_staging()
        logger.info("✅ Staging tables prepared successfully")
        
        # Test allergen mapping
        logger.info("Testing allergen mapping...")
        if hasattr(loader, 'allergen_mapping_dict') and loader.allergen_mapping_dict:
            logger.info(f"✅ Allergen mapping loaded: {len(loader.allergen_mapping_dict)} mappings")
        else:
            logger.warning("⚠️ Allergen mapping not loaded")
        
        # Clean up
        loader.disconnect()
        logger.info("✅ Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    logger.info("🧪 Starting Database Connection Test...")
    
    success = test_db_connection()
    
    if success:
        logger.info("\n🎉 Database connection test completed successfully!")
        logger.info("✅ The BatchLoader from initial_load is working correctly!")
    else:
        logger.error("\n❌ Database connection test failed!")

if __name__ == "__main__":
    main()

