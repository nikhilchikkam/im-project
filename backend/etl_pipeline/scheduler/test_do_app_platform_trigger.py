#!/usr/bin/env python3
"""
Test script for manual trigger of the complete scheduler on DigitalOcean App Platform
Tests the full OWS -> Spaces -> Database workflow in the cloud environment
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta

# Setup logging for DO App Platform
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_do_app_platform_trigger():
    """Test the complete scheduler manual trigger on DigitalOcean App Platform"""
    logger.info("🧪 Testing Complete Scheduler Manual Trigger (DO App Platform)...")
    
    try:
        # Import the scheduler components directly to avoid relative import issues
        from incremental_loader import IncrementalLoader
        
        # Create loader instance directly
        logger.info("Creating IncrementalLoader instance...")
        loader = IncrementalLoader()
        
        # Test manual trigger with 7 days lookback
        lookback_days = 7
        logger.info(f"Triggering manual update with {lookback_days} days lookback...")
        
        # Run manual update directly using the loader
        result = loader.run_incremental_update(lookback_days=lookback_days)
        
        logger.info(f"Manual trigger result: {json.dumps(result, indent=2, default=str)}")
        
        if result.get('status') == 'success':
            logger.info("✅ Manual trigger completed successfully on DO App Platform!")
            logger.info(f"Session ID: {result.get('session_id')}")
            logger.info(f"Processing time: {result.get('processing_time', 0):.2f} seconds")
            logger.info(f"Workers used: {result.get('workers_used')}")
            
            stats = result.get('stats', {})
            logger.info(f"Batches processed: {stats.get('batches_processed', 0)}")
            logger.info(f"Products processed: {stats.get('products_processed', 0)}")
            logger.info(f"Products updated: {stats.get('products_updated', 0)}")
            logger.info(f"Products inserted: {stats.get('products_inserted', 0)}")
            logger.info(f"Errors: {stats.get('errors', 0)}")
            
            return {
                'status': 'success',
                'result': result
            }
        else:
            logger.error(f"❌ Manual trigger failed: {result.get('error')}")
            return {
                'status': 'failed',
                'error': result.get('error')
            }
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

def main():
    """Main test function"""
    logger.info("🧪 Starting DO App Platform Manual Trigger Test...")
    
    result = test_do_app_platform_trigger()
    
    if result['status'] == 'success':
        logger.info("\n🎉 DO App Platform manual trigger test completed successfully!")
        logger.info("The scheduler is working correctly on DigitalOcean App Platform!")
    else:
        logger.error(f"❌ DO App Platform manual trigger test failed: {result.get('error')}")

if __name__ == "__main__":
    main()
