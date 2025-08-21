"""
Configuration module for ETL Scheduler
Extends the initial_load configuration with scheduler-specific settings
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import base config from initial_load
from ..initial_load.config import ETLConfig

# Load environment variables from backend directory
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

class SchedulerConfig(ETLConfig):
    """Configuration class for ETL scheduler settings - extends ETLConfig"""
    
    # Scheduler Configuration
    SCHEDULE_INTERVAL_DAYS = int(os.getenv('SCHEDULE_INTERVAL_DAYS', '7'))  # Weekly
    SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '02:00')  # 2 AM
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    
    # Incremental Update Configuration
    DEFAULT_LOOKBACK_DAYS = int(os.getenv('DEFAULT_LOOKBACK_DAYS', '7'))
    MAX_LOOKBACK_DAYS = int(os.getenv('MAX_LOOKBACK_DAYS', '30'))
    SCHEDULER_BATCH_SIZE = int(os.getenv('SCHEDULER_BATCH_SIZE', '1000'))
    
    # Logging Configuration (scheduler-specific)
    SCHEDULER_LOG_LEVEL = os.getenv('SCHEDULER_LOG_LEVEL', 'INFO')
    SCHEDULER_LOG_FILE = os.getenv('SCHEDULER_LOG_FILE', 'scheduler.log')
    
    @classmethod
    def get_date_range(cls, lookback_days=None):
        """Get date range for incremental updates"""
        if lookback_days is None:
            lookback_days = cls.DEFAULT_LOOKBACK_DAYS
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        return {
            "from": {
                "date": start_date.strftime("%Y-%m-%d"),
                "op": "GTE"
            },
            "to": {
                "date": end_date.strftime("%Y-%m-%d"),
                "op": "LTE"
            }
        }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        # First validate base ETL config
        super().validate()
        
        # Additional scheduler-specific validation
        required = [
            'SCHEDULE_TIME',
            'TIMEZONE'
        ]
        
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required scheduler configuration: {missing}")
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        # Print base ETL config
        super().print_config()
        
        # Print scheduler-specific config
        print("\nScheduler Configuration:")
        print(f"  Schedule Interval: {cls.SCHEDULE_INTERVAL_DAYS} days")
        print(f"  Schedule Time: {cls.SCHEDULE_TIME}")
        print(f"  Timezone: {cls.TIMEZONE}")
        print(f"  Default Lookback: {cls.DEFAULT_LOOKBACK_DAYS} days")
        print(f"  Max Lookback: {cls.MAX_LOOKBACK_DAYS} days")
        print(f"  Scheduler Batch Size: {cls.SCHEDULER_BATCH_SIZE}")
        print(f"  Scheduler Log Level: {cls.SCHEDULER_LOG_LEVEL}")
        print(f"  Scheduler Log File: {cls.SCHEDULER_LOG_FILE}")
