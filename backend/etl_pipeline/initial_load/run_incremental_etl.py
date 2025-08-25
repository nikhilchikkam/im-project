#!/usr/bin/env python3
"""
Run incremental ETL using the enhanced initial load infrastructure
Complete flow: OWS API -> Spaces -> Database (no local download)
"""

import os
import sys
import logging

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from etl_orchestrator import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_incremental():
    """Run incremental ETL"""
    try:
        # Set environment to force incremental mode
        os.environ['RUN_INCREMENTAL'] = 'true'
        
        # Print configuration
        from config import ETLConfig
        start_date, end_date = ETLConfig.get_date_range()
        
        logger.info("="*60)
        logger.info("INCREMENTAL ETL CONFIGURATION")
        logger.info("="*60)
        logger.info(f"Lookback Days: {ETLConfig.LOOKBACK_DAYS}")
        logger.info(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Max Workers: {ETLConfig.ETL_MAX_WORKERS}")
        logger.info(f"OWS Batch Size: {ETLConfig.OWS_BATCH_SIZE}")
        logger.info("="*60)
        
        # Run the main ETL process
        return main()
        
    except Exception as e:
        logger.error(f"Incremental ETL failed: {e}")
        return 1

if __name__ == "__main__":
    exit(run_incremental())
