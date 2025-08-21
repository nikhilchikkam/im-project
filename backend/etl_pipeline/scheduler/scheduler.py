"""
ETL Scheduler for Incremental Updates
Handles both scheduled and manual incremental updates
"""

import os
import sys
import json
import logging
import time
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import schedule
import threading
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from .config import SchedulerConfig
from .incremental_loader import IncrementalLoader

# Setup logging
logging.basicConfig(
    level=getattr(logging, SchedulerConfig.SCHEDULER_LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SchedulerConfig.SCHEDULER_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IncrementalETLScheduler:
    """Main scheduler for incremental ETL updates"""
    
    def __init__(self):
        self.loader = IncrementalLoader()
        self.running = False
        self.scheduler_thread = None
        self.last_run = None
        self.next_run = None
        
    def setup_schedule(self):
        """Setup the scheduled job"""
        try:
            # Parse schedule time (format: "HH:MM")
            hour, minute = map(int, SchedulerConfig.SCHEDULE_TIME.split(':'))
            
            # Schedule weekly job
            if SchedulerConfig.SCHEDULE_INTERVAL_DAYS == 7:
                schedule.every().week.at(f"{hour:02d}:{minute:02d}").do(self.run_scheduled_update)
                logger.info(f"Scheduled weekly update at {SchedulerConfig.SCHEDULE_TIME}")
            else:
                # Custom interval
                schedule.every(SchedulerConfig.SCHEDULE_INTERVAL_DAYS).days.at(f"{hour:02d}:{minute:02d}").do(self.run_scheduled_update)
                logger.info(f"Scheduled update every {SchedulerConfig.SCHEDULE_INTERVAL_DAYS} days at {SchedulerConfig.SCHEDULE_TIME}")
            
            # Calculate next run time
            self._calculate_next_run()
            
        except Exception as e:
            logger.error(f"Failed to setup schedule: {e}")
            raise
    
    def _calculate_next_run(self):
        """Calculate next scheduled run time"""
        try:
            # Get the next scheduled run
            next_job = schedule.next_run()
            if next_job:
                self.next_run = next_job
                logger.info(f"Next scheduled run: {self.next_run}")
            else:
                self.next_run = None
        except Exception as e:
            logger.warning(f"Could not calculate next run time: {e}")
            self.next_run = None
    
    def run_scheduled_update(self):
        """Run scheduled incremental update"""
        logger.info("Starting scheduled incremental update")
        self.last_run = datetime.now()
        
        try:
            result = self.loader.run_incremental_update()
            
            if result['status'] == 'success':
                logger.info("Scheduled update completed successfully")
            else:
                logger.error(f"Scheduled update failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Scheduled update failed with exception: {e}")
        
        finally:
            # Recalculate next run time
            self._calculate_next_run()
    
    def run_manual_update(self, lookback_days: Optional[int] = None) -> Dict[str, Any]:
        """Run manual incremental update"""
        logger.info(f"Starting manual incremental update (lookback: {lookback_days} days)")
        
        try:
            # Validate lookback days
            if lookback_days is not None:
                if lookback_days > SchedulerConfig.MAX_LOOKBACK_DAYS:
                    raise ValueError(f"Lookback days ({lookback_days}) exceeds maximum ({SchedulerConfig.MAX_LOOKBACK_DAYS})")
                if lookback_days < 1:
                    raise ValueError("Lookback days must be at least 1")
            
            result = self.loader.run_incremental_update(lookback_days)
            
            if result['status'] == 'success':
                logger.info("Manual update completed successfully")
            else:
                logger.error(f"Manual update failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Manual update failed with exception: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self.running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'schedule_interval_days': SchedulerConfig.SCHEDULE_INTERVAL_DAYS,
            'schedule_time': SchedulerConfig.SCHEDULE_TIME,
            'timezone': SchedulerConfig.TIMEZONE
        }
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Validate configuration
            SchedulerConfig.validate()
            
            # Setup schedule
            self.setup_schedule()
            
            # Start scheduler thread
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("ETL Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping ETL Scheduler...")
        self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        
        logger.info("ETL Scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Run pending scheduled jobs
                schedule.run_pending()
                
                # Sleep for a short interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue after error
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point for the scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Scheduler for Incremental Updates')
    parser.add_argument('--manual', action='store_true', help='Run manual update instead of starting scheduler')
    parser.add_argument('--lookback', type=int, help='Number of days to look back for manual update')
    parser.add_argument('--status', action='store_true', help='Show scheduler status')
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        SchedulerConfig.validate()
        SchedulerConfig.print_config()
        
        scheduler = IncrementalETLScheduler()
        
        if args.status:
            # Show status
            status = scheduler.get_status()
            print(json.dumps(status, indent=2, default=str))
            
        elif args.manual:
            # Run manual update
            result = scheduler.run_manual_update(args.lookback)
            print(json.dumps(result, indent=2, default=str))
            
        else:
            # Start scheduler
            scheduler.setup_signal_handlers()
            scheduler.start()
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                scheduler.stop()
                
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
