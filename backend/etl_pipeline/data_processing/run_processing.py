#!/usr/bin/env python3
"""
Simple Data Processing Runner

This script can be imported and called from the ETL orchestrator
to run data processing after ETL completion.

Usage:
    from data_processing.run_processing import run_data_processing
    success = run_data_processing()
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import the wrapper
sys.path.append(str(Path(__file__).parent))

from run_all_processing import DataProcessingWrapper

def run_data_processing():
    """
    Run all data processing scripts in order.
    
    Returns:
        bool: True if all scripts completed successfully, False otherwise
    """
    try:
        wrapper = DataProcessingWrapper()
        return wrapper.run_all_processing()
    except Exception as e:
        print(f"Error running data processing: {e}")
        return False

if __name__ == "__main__":
    success = run_data_processing()
    sys.exit(0 if success else 1)
