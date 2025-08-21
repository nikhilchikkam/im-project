#!/usr/bin/env python3
"""
Test script for the Spaces ETL Orchestrator
Tests loading batch data from DO Spaces to database using the new orchestrator
"""

import os
import sys
import logging
from datetime import datetime
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

def test_spaces_orchestrator():
    """Test the Spaces ETL Orchestrator"""
    logger.info("🧪 Testing Spaces ETL Orchestrator...")
    
    try:
        # Import the Spaces ETL Orchestrator
        from spaces_etl_orchestrator import SpacesETLOrchestrator
        
        # Use the most recent session from the last test run
        session_id = "20250820_221859"  # From the last test run
        logger.info(f"Using session ID: {session_id}")
        
        # Create orchestrator instance with just 1 worker for testing
        logger.info("Creating Spaces ETL Orchestrator instance...")
        orchestrator = SpacesETLOrchestrator(max_workers=1)  # Use 1 worker for testing
        
        # Run the ETL process (test mode - only first 1 batch)
        logger.info("Running ETL process from DO Spaces (TEST MODE)...")
        result = orchestrator.run_etl_from_spaces(session_id, max_batches=1)
        
        if result['status'] == 'success':
            logger.info("\n🎉 Spaces ETL Orchestrator test completed successfully!")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"Total batches: {result['total_batches']}")
            logger.info(f"Processed batches: {result['processed_batches']}")
            logger.info(f"Error batches: {result['error_batches']}")
            logger.info(f"Success rate: {result['success_rate']:.1f}%")
            logger.info(f"Duration: {result['duration_seconds']:.2f} seconds")
            
            logger.info("\nDATA PROCESSED:")
            logger.info(f"  Nutrition records copied: {result['nutrition_copied']:,}")
            logger.info(f"  Allergen records copied: {result['allergen_copied']:,}")
            logger.info(f"  Nutrition records merged: {result['nutrition_merged']:,}")
            logger.info(f"  Allergen records merged: {result['allergen_merged']:,}")
            
            logger.info("\n✅ The Spaces ETL Orchestrator is working correctly!")
            return result
        else:
            logger.error(f"❌ Spaces ETL Orchestrator test failed: {result.get('error')}")
            return result
        
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
    logger.info("🧪 Starting Spaces ETL Orchestrator Test...")
    
    result = test_spaces_orchestrator()
    
    if result['status'] == 'success':
        logger.info("\n🎉 Test completed successfully!")
    else:
        logger.error(f"❌ Test failed: {result.get('error')}")

if __name__ == "__main__":
    main()
