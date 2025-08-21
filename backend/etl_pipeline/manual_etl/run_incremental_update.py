#!/usr/bin/env python3
"""
Manual trigger script for incremental ETL updates
Can be run from DigitalOcean App Platform console
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from etl_pipeline.scheduler.incremental_loader import IncrementalLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Manual trigger for incremental ETL update"""
    try:
        logger.info("Starting manual incremental ETL update...")
        
        # Initialize the incremental loader
        loader = IncrementalLoader()
        
        # Default to 7 days lookback, but can be overridden
        lookback_days = int(os.getenv('LOOKBACK_DAYS', '7'))
        
        logger.info(f"Running incremental update with {lookback_days} days lookback")
        
        # Run the incremental update
        result = loader.run_incremental_update(lookback_days=lookback_days)
        
        logger.info("Manual incremental ETL update completed successfully!")
        logger.info(f"Results: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Manual incremental ETL update failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
