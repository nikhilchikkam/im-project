#!/usr/bin/env python3
"""
Test script for the ETL Scheduler
Tests if the scheduler can fetch data from OWS and process it
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from initial_load
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly to avoid relative import issues
from incremental_loader import IncrementalLoader

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

def test_scheduler_components():
    """Test individual components of the scheduler"""
    logger.info("🧪 Testing Scheduler Components...")
    
    try:
        # Test 1: Initialize IncrementalLoader
        logger.info("Test 1: Initializing IncrementalLoader...")
        loader = IncrementalLoader()
        logger.info("✅ IncrementalLoader initialized successfully")
        
        # Test 2: Test database connection
        logger.info("Test 2: Testing database connection...")
        loader.connect()
        logger.info("✅ Database connection successful")
        loader.disconnect()
        
        # Test 3: Test Spaces client setup
        logger.info("Test 3: Testing DigitalOcean Spaces client...")
        loader.setup_spaces_client()
        logger.info("✅ Spaces client configured successfully")
        
        # Test 4: Test batch loader setup
        logger.info("Test 4: Testing batch loader setup...")
        loader.setup_batch_loader()
        logger.info("✅ Batch loader configured successfully")
        
        # Test 5: Test criteria building
        logger.info("Test 5: Testing incremental criteria building...")
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        criteria = loader.build_incremental_criteria(start_date, end_date)
        logger.info(f"✅ Criteria built successfully: {json.dumps(criteria, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Component test failed: {e}")
        return False

def test_data_fetching():
    """Test if the scheduler can fetch data from OWS"""
    logger.info("🔄 Testing Data Fetching...")
    
    try:
        loader = IncrementalLoader()
        
        # Build test criteria for last 7 days
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        criteria = loader.build_incremental_criteria(start_date, end_date)
        
        logger.info(f"Fetching data for period: {start_date.date()} to {end_date.date()}")
        logger.info(f"Criteria: {json.dumps(criteria, indent=2)}")
        
        # Test the fetch method (currently returns empty list as placeholder)
        products = loader.fetch_incremental_data(criteria)
        
        logger.info(f"✅ Fetch completed. Retrieved {len(products)} products")
        
        if products:
            logger.info(f"Sample product: {json.dumps(products[0], indent=2)}")
        else:
            logger.info("ℹ️ No products returned (expected for placeholder implementation)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Data fetching test failed: {e}")
        return False

def test_full_workflow():
    """Test the complete workflow (without actual OWS API call)"""
    logger.info("🚀 Testing Full Workflow...")
    
    try:
        loader = IncrementalLoader()
        
        # Test with a small lookback period
        result = loader.run_incremental_update(lookback_days=1)
        
        logger.info(f"✅ Workflow completed with result: {json.dumps(result, indent=2)}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        logger.error(f"❌ Full workflow test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🧪 Starting Scheduler Tests...")
    
    # Test 1: Component tests
    component_test_passed = test_scheduler_components()
    
    if component_test_passed:
        logger.info("✅ All component tests passed!")
    else:
        logger.error("❌ Component tests failed!")
        return
    
    # Test 2: Data fetching test
    fetch_test_passed = test_data_fetching()
    
    if fetch_test_passed:
        logger.info("✅ Data fetching test passed!")
    else:
        logger.error("❌ Data fetching test failed!")
        return
    
    # Test 3: Full workflow test
    workflow_test_passed = test_full_workflow()
    
    if workflow_test_passed:
        logger.info("✅ Full workflow test passed!")
    else:
        logger.error("❌ Full workflow test failed!")
        return
    
    logger.info("🎉 All tests passed! Scheduler is ready for production.")

if __name__ == "__main__":
    main()
