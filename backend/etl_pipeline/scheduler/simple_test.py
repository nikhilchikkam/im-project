#!/usr/bin/env python3
"""
Simple test script for the ETL Scheduler
Basic functionality test without complex imports
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
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

def test_basic_functionality():
    """Test basic scheduler functionality"""
    logger.info("🧪 Testing Basic Scheduler Functionality...")
    
    try:
        # Test 1: Import the IncrementalLoader
        logger.info("Test 1: Importing IncrementalLoader...")
        from incremental_loader import IncrementalLoader
        logger.info("✅ IncrementalLoader imported successfully")
        
        # Test 2: Create instance
        logger.info("Test 2: Creating IncrementalLoader instance...")
        loader = IncrementalLoader()
        logger.info("✅ IncrementalLoader instance created")
        
        # Test 3: Test criteria building
        logger.info("Test 3: Testing criteria building...")
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        criteria = loader.build_incremental_criteria(start_date, end_date)
        logger.info(f"✅ Criteria built: {json.dumps(criteria, indent=2)}")
        
        # Test 4: Test data fetching (placeholder)
        logger.info("Test 4: Testing data fetching...")
        products = loader.fetch_incremental_data(criteria)
        logger.info(f"✅ Fetch test completed. Got {len(products)} products")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🧪 Starting Simple Scheduler Test...")
    
    if test_basic_functionality():
        logger.info("🎉 Basic functionality test passed!")
    else:
        logger.error("❌ Basic functionality test failed!")
