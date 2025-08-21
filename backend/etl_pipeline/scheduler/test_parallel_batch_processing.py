#!/usr/bin/env python3
"""
Test script for parallel batch processing using the spaces ETL orchestrator
This simulates the real production workflow with multiple workers processing batches in parallel
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

def test_parallel_batch_processing():
    """Test parallel batch processing using the spaces ETL orchestrator"""
    logger.info("🚀 Testing Parallel Batch Processing with Comprehensive BatchLoader...")
    
    try:
        # Import the spaces ETL orchestrator
        from spaces_etl_orchestrator import SpacesETLOrchestrator
        
        # Use the latest session ID (you can change this to test different sessions)
        session_id = "20250820_221859"  # Replace with actual session ID from DO Spaces
        
        # Create orchestrator with 2 workers for testing (faster than 4 for small tests)
        max_workers = 2
        logger.info(f"Creating Spaces ETL Orchestrator with {max_workers} workers...")
        orchestrator = SpacesETLOrchestrator(max_workers=max_workers)
        
        # Run ETL process with limited batches for testing (process 3rd and 4th)
        start_index = 2  # Skip first 2 batches
        max_batches = 2  # Then process next 2 batches (3rd and 4th)
        logger.info(f"Processing batches {start_index+1} and {start_index+2} from session: {session_id}")
        
        start_time = datetime.now()
        result = orchestrator.run_etl_from_spaces(session_id, max_batches=max_batches, start_index=start_index)
        end_time = datetime.now()
        
        duration = end_time - start_time
        
        if result['status'] == 'success':
            logger.info("\n🎉 Parallel batch processing test completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info(f"📊 Batches processed: {result['processed_batches']}/{result['total_batches']}")
            logger.info(f"✅ Success rate: {result['success_rate']:.1f}%")
            logger.info(f"📦 Products processed: {result['products_processed']:,}")
            logger.info(f"🥄 Serving processed: {result['serving_processed']:,}")
            logger.info(f"🏷️  Diet claims processed: {result['diet_claims_processed']:,}")
            logger.info(f"🖼️  Image URLs processed: {result['image_urls_processed']:,}")
            logger.info(f"🧬 Nutrition processed: {result['nutrition_processed']:,}")
            logger.info(f"⚠️  Allergen processed: {result['allergen_processed']:,}")
            
            # Calculate performance metrics
            total_records = (result['products_processed'] + result['serving_processed'] + 
                           result['diet_claims_processed'] + result['image_urls_processed'] + 
                           result['nutrition_processed'] + result['allergen_processed'])
            
            if duration.total_seconds() > 0:
                records_per_second = total_records / duration.total_seconds()
                logger.info(f"🚀 Performance: {records_per_second:.2f} records/second")
            
            logger.info("\n✅ The parallel batch processing is working correctly!")
            logger.info("All data types are processed through staging tables with parallel workers!")
            logger.info("Using the comprehensive BatchLoader that handles all data types!")
            
        else:
            logger.error(f"❌ Parallel batch processing failed: {result.get('error')}")
            return {
                'status': 'failed',
                'error': result.get('error')
            }
            
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
    logger.info("🧪 Starting Parallel Batch Processing Test...")
    
    result = test_parallel_batch_processing()
    
    if result.get('status') == 'failed':
        logger.error(f"❌ Test failed: {result.get('error')}")
        return 1
    else:
        logger.info("\n🎉 All tests completed successfully!")
        return 0

if __name__ == "__main__":
    exit(main())
