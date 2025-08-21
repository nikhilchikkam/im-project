#!/usr/bin/env python3
"""
End-to-end scheduler test:
1) Builds a last-7-days OWS criteria
2) Fetches 1-2 batches from OWS and saves to DO Spaces (creates a session)
3) Loads those batches into DB via parallel workers from Spaces

Environment required: DATABASE_URL, SPACES_* vars, OWS credentials configured for oneworldsync client.
"""

import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Step 1: Fetch from OWS and save to Spaces
    from incremental_loader import IncrementalLoader
    loader = IncrementalLoader()
    
    lookback_days = int(os.getenv('SCHEDULER_LOOKBACK_DAYS', '7'))
    logger.info(f"Starting end-to-end scheduler test for last {lookback_days} days...")
    result_fetch = loader.run_incremental_update(lookback_days=lookback_days)
    if result_fetch.get('status') != 'success':
        logger.error(f"Fetch/save failed: {result_fetch.get('error')}")
        return 1
    
    session_id = result_fetch.get('session_id')
    logger.info(f"Saved batches to Spaces for session: {session_id}")
    
    # Optionally, re-run loader from Spaces for a subset (e.g., 2 batches) using orchestrator directly
    from spaces_etl_orchestrator import SpacesETLOrchestrator
    max_workers = int(os.getenv('SCHEDULER_MAX_WORKERS', '4'))
    orchestrator = SpacesETLOrchestrator(max_workers=max_workers)
    load_result = orchestrator.run_etl_from_spaces(session_id, max_batches=int(os.getenv('SCHEDULER_TEST_MAX_BATCHES', '2')))
    if load_result.get('status') != 'success':
        logger.error(f"Load failed: {load_result.get('error')}")
        return 1
    
    logger.info("End-to-end scheduler test completed successfully")
    return 0

if __name__ == '__main__':
    exit(main())


