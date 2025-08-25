#!/usr/bin/env python3
"""
Data Processing Wrapper Script

This script runs all data processing scripts in the specified order.
Handles both Python and SQL scripts.

Scripts run in order:
1. add_unit_name.py
2. update_availability_flags.py
3. update_class_title.py
4. name_normalizer.py
5. good_choice_evaluator.py

Usage:
    python run_all_processing.py
"""

import os
import sys
import subprocess
import logging
import psycopg2
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_processing_wrapper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataProcessingWrapper:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.reference_files_dir = self.scripts_dir.parent / "reference_files"
        
        # Scripts in execution order
        self.scripts = [
            "add_unit_name.py",
            "update_availability_flags.py", 
            "update_class_title.py",
            "name_normalizer.py",
            "maintain_product_classification.py",
            "good_choice_evaluator.py",
            "smart_snack_evaluator.py",
            "philadelphia_purchased_food_evaluator.py"
        ]
        
        # Database connection
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    def run_all_processing(self):
        """Run all data processing scripts in order"""
        logger.info("="*80)
        logger.info("STARTING DATA PROCESSING WRAPPER")
        logger.info("="*80)
        
        start_time = datetime.now()
        
        try:
            for i, script_name in enumerate(self.scripts, 1):
                logger.info(f"Processing {i}/{len(self.scripts)}: {script_name}")
                logger.info("-" * 60)
                
                script_path = self.scripts_dir / script_name
                if not script_path.exists():
                    logger.error(f"Script not found: {script_path}")
                    return False
                
                # Handle SQL scripts differently
                if script_name.endswith('.sql'):
                    success = self._run_sql_script(script_path, script_name)
                else:
                    success = self._run_python_script(script_path, script_name)
                
                if not success:
                    logger.error(f"Failed to run: {script_name}")
                    return False
                
                logger.info(f"Completed: {script_name}")
                logger.info("")
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("="*80)
            logger.info("ALL DATA PROCESSING COMPLETED SUCCESSFULLY")
            logger.info(f"Total Duration: {duration}")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"Processing failed with error: {e}")
            return False
    
    def _run_python_script(self, script_path: Path, script_name: str) -> bool:
        """Run a Python data processing script"""
        try:
            # Set environment variables for the script
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.scripts_dir.parent)
            
            logger.info(f"Running Python script: {script_name}")
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.scripts_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout per script
            )
            
            if result.returncode != 0:
                logger.error(f"Script {script_name} failed:")
                logger.error(f"Return code: {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
            
            # Log output if any
            if result.stdout.strip():
                logger.info(f"Script {script_name} output: {result.stdout.strip()}")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script {script_name} timed out after 30 minutes")
            return False
        except Exception as e:
            logger.error(f"Error running {script_name}: {e}")
            return False
    
    def _run_sql_script(self, script_path: Path, script_name: str) -> bool:
        """Run a SQL data processing script"""
        try:
            logger.info(f"Running SQL script: {script_name}")
            
            # Read SQL script
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Connect to database
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            logger.info(f"Executing {len(statements)} SQL statements...")
            
            for i, stmt in enumerate(statements, 1):
                if stmt:
                    try:
                        cursor.execute(stmt)
                        logger.debug(f"Executed statement {i}/{len(statements)}")
                    except Exception as e:
                        logger.error(f"Error executing statement {i}: {e}")
                        logger.error(f"Statement: {stmt[:100]}...")
                        conn.rollback()
                        cursor.close()
                        conn.close()
                        return False
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"SQL script {script_name} executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running SQL script {script_name}: {e}")
            return False
    
    def _get_database_connection(self):
        """Get database connection for scripts that need it"""
        return psycopg2.connect(self.database_url)

def main():
    """Main entry point"""
    try:
        wrapper = DataProcessingWrapper()
        success = wrapper.run_all_processing()
        
        if success:
            logger.info("All data processing completed successfully!")
            sys.exit(0)
        else:
            logger.error("Data processing failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
