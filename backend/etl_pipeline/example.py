#!/usr/bin/env python3
"""
Example usage of the ETL Pipeline
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import the ETL modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_pipeline import OneWorldSyncETL
from etl_pipeline.utils import setup_logging, print_sync_summary, print_bucket_stats

def example_basic_usage():
    """Example of basic ETL usage"""
    print("ETL Pipeline Example - Basic Usage")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    try:
        # Initialize ETL pipeline
        etl = OneWorldSyncETL()
        
        # Test connections
        print("Testing connections...")
        results = etl.test_connections()
        if not all(results.values()):
            print("Connection test failed!")
            return
        
        # Run smart sync
        print("Running smart sync...")
        result = etl.run_smart_sync()
        print_sync_summary(result)
        
        # Show bucket statistics
        print("Getting bucket statistics...")
        stats = etl.get_bucket_stats()
        print_bucket_stats(stats)
        
    except Exception as e:
        print(f"Example failed: {e}")

def example_incremental_sync():
    """Example of incremental sync"""
    print("🔄 ETL Pipeline Example - Incremental Sync")
    print("=" * 50)
    
    setup_logging()
    
    try:
        etl = OneWorldSyncETL()
        
        # Run incremental sync
        result = etl.run_incremental_sync()
        print_sync_summary(result)
        
    except Exception as e:
        print(f"Incremental sync failed: {e}")

def example_monitoring():
    """Example of monitoring and validation"""
    print("ETL Pipeline Example - Monitoring")
    print("=" * 50)
    
    setup_logging()
    
    try:
        etl = OneWorldSyncETL()
        
        # Get sync status
        status = etl.get_sync_status()
        print_sync_summary(status)
        
        # Validate data
        validation = etl.validate_data()
        print("Validation Results:")
        print(f"  Total Files: {validation.get('total_files', 0)}")
        print(f"  Total Size: {validation.get('total_size_mb', 0):.2f} MB")
        if validation.get('errors'):
            print("  Errors:")
            for error in validation['errors']:
                print(f"    - {error}")
        else:
            print("No validation errors found")
        
        # Get bucket stats
        stats = etl.get_bucket_stats()
        print_bucket_stats(stats)
        
    except Exception as e:
        print(f"Monitoring failed: {e}")

def example_cleanup():
    """Example of data cleanup"""
    print("ETL Pipeline Example - Data Cleanup")
    print("=" * 50)
    
    setup_logging()
    
    try:
        etl = OneWorldSyncETL()
        
        # Clean up old data (keep last 7 days)
        print("Cleaning up data older than 7 days...")
        etl.cleanup_old_data(days_to_keep=7)
        print("Cleanup completed!")
        
    except Exception as e:
        print(f"Cleanup failed: {e}")

def main():
    """Main example function"""
    if len(sys.argv) < 2:
        print("Usage: python example.py [basic|incremental|monitoring|cleanup]")
        print("\nExamples:")
        print("  python example.py basic        # Basic usage example")
        print("  python example.py incremental  # Incremental sync example")
        print("  python example.py monitoring   # Monitoring example")
        print("  python example.py cleanup     # Cleanup example")
        return
    
    example_type = sys.argv[1].lower()
    
    if example_type == 'basic':
        example_basic_usage()
    elif example_type == 'incremental':
        example_incremental_sync()
    elif example_type == 'monitoring':
        example_monitoring()
    elif example_type == 'cleanup':
        example_cleanup()
    else:
        print(f"Unknown example type: {example_type}")
        print("Available examples: basic, incremental, monitoring, cleanup")

if __name__ == "__main__":
    main() 