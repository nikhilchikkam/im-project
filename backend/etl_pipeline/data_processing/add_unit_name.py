import os
import pandas as pd
import logging
import psycopg2
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Step 1: Load CSV with unit code → name mapping
# Load from reference_files directory
reference_path = "../reference_files/Filtered_Nutrient_Attributes.csv"

if not os.path.exists(reference_path):
    logging.error(f"Reference file not found: {reference_path}")
    raise FileNotFoundError(f"Filtered_Nutrient_Attributes.csv not found at {reference_path}")

try:
    mapping_df = pd.read_csv(reference_path)
    logging.info(f"Loaded mapping file from: {reference_path}")
except Exception as e:
    logging.error(f"Failed to load {reference_path}: {e}")
    raise

mapping_df.columns = mapping_df.columns.str.strip().str.lower()

# Step 2: Clean and build mapping dictionary
mapping_df = mapping_df.dropna(subset=["code"])
mapping_df = mapping_df[mapping_df["code"].astype(str).str.strip() != ""]
unit_mapping = dict(zip(mapping_df["code"], mapping_df["name"]))

# Step 3: Connect and update DB using batch processing with retry logic
logging.info("Starting unit name updates using batch processing...")

def update_with_retry(max_attempts=3, base_delay=1):
    """Execute the update with retry logic for deadlock handling"""
    for attempt in range(max_attempts):
        try:
            # Connect to database
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            try:
                # Set a reasonable lock timeout (30 seconds)
                cursor.execute("SET lock_timeout = '30s'")
                
                # Create temporary table
                cursor.execute("""
                    CREATE TEMP TABLE unit_mapping_temp (
                        unit_code VARCHAR(50),
                        unit_name VARCHAR(255)
                    )
                """)
                
                # Insert all mappings into temp table using executemany
                mapping_data = [(code, name) for code, name in unit_mapping.items()]
                cursor.executemany("""
                    INSERT INTO unit_mapping_temp (unit_code, unit_name)
                    VALUES (%s, %s)
                """, mapping_data)
                
                # Update only records where unit_name is NULL
                cursor.execute("""
                    UPDATE product_nutrition pn
                    SET unit_name = umt.unit_name
                    FROM unit_mapping_temp umt
                    WHERE pn.unit = umt.unit_code
                    AND pn.unit_name IS NULL
                """)
                
                updated_count = cursor.rowcount
                logging.info(f"Batch updated {updated_count} records with unit names")
                
                # Commit the transaction
                conn.commit()
                logging.info("Unit name column updated successfully using batch processing.")
                return True
                
            except psycopg2.errors.DeadlockDetected as e:
                conn.rollback()
                if attempt < max_attempts - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(f"Deadlock detected on attempt {attempt + 1}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logging.error(f"Deadlock persisted after {max_attempts} attempts")
                    raise
            except Exception as e:
                conn.rollback()
                logging.error(f"Error during batch update: {e}")
                raise
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            if attempt < max_attempts - 1 and "deadlock" in str(e).lower():
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Connection error on attempt {attempt + 1}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise
    
    return False

# Execute the update with retry logic
success = update_with_retry()
if not success:
    raise Exception("Failed to update unit names after multiple attempts")
