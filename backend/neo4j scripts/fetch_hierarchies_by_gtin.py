import os
import csv
import json
import time
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from oneworldsync import Content1Client, AuthenticationError, APIError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hierarchy_fetch_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()

logger.info("Initializing Content1Client...")
try:
    client = Content1Client()
    logger.info("Content1Client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Content1Client: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

BATCH_SIZE = 1000
OUTPUT_DIR = "results/hierarchies_by_gtin"
GTIN_CSV = os.path.join(os.path.dirname(__file__), "gtin.csv")

logger.info(f"Configuration:")
logger.info(f"  BATCH_SIZE: {BATCH_SIZE}")
logger.info(f"  OUTPUT_DIR: {OUTPUT_DIR}")
logger.info(f"  GTIN_CSV: {GTIN_CSV}")

# Create output directory
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logger.info(f"Output directory created/verified: {OUTPUT_DIR}")
except Exception as e:
    logger.error(f"Failed to create output directory: {e}")
    raise

def read_gtins(csv_path):
    logger.info(f"Reading GTINs from CSV: {csv_path}")
    
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            gtins = [row["gtin"].strip() for row in reader if row["gtin"].strip()]
            logger.info(f"Successfully read {len(gtins)} GTINs from CSV")
            return gtins
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def fetch_hierarchy(gtin, retries=3, delay=2):
    logger.debug(f"Fetching hierarchy for GTIN: {gtin}")
    
    criteria = {
        "targetMarket": "US",
        "gtin": [gtin],  # Always send as a list
        "sortFields": [
            {"field": "lastModifiedDate", "desc": True},
            {"field": "gtin", "desc": False}
        ]
    }
    
    logger.debug(f"API criteria: {criteria}")
    
    for attempt in range(retries):
        try:
            logger.debug(f"GTIN {gtin}: Attempt {attempt+1}/{retries}")
            start_time = time.time()
            
            result = client.fetch_hierarchies(criteria)
            
            end_time = time.time()
            logger.debug(f"GTIN {gtin}: API call completed in {end_time - start_time:.2f}s")
            
            # Log the type and available keys of the result
            if isinstance(result, dict):
                logger.debug(f"GTIN {gtin}: Received response with keys: {list(result.keys())}")
            else:
                logger.debug(f"GTIN {gtin}: Received response of type {type(result)}")
            
            # Try to access hierarchies as a dictionary
            hierarchies = result.get('hierarchies', []) if isinstance(result, dict) else []
            if hierarchies:
                logger.debug(f"GTIN {gtin}: Found {len(hierarchies)} hierarchies")
            else:
                logger.warning(f"GTIN {gtin}: No 'hierarchies' key in result or empty list")
            
            return result
            
        except AuthenticationError as e:
            logger.error(f"GTIN {gtin}: Authentication error on attempt {attempt+1}: {e}")
            if attempt == retries - 1:
                logger.error(f"GTIN {gtin}: Authentication failed after {retries} attempts")
            time.sleep(delay)
            
        except APIError as e:
            logger.error(f"GTIN {gtin}: API error on attempt {attempt+1}: {e}")
            logger.error(f"GTIN {gtin}: API error details: {getattr(e, 'status_code', 'Unknown')} - {getattr(e, 'message', str(e))}")
            if attempt == retries - 1:
                logger.error(f"GTIN {gtin}: API error failed after {retries} attempts")
            time.sleep(delay)
            
        except Exception as e:
            logger.error(f"GTIN {gtin}: Unexpected error on attempt {attempt+1}: {e}")
            logger.error(f"GTIN {gtin}: Error type: {type(e).__name__}")
            logger.error(f"GTIN {gtin}: Traceback: {traceback.format_exc()}")
            if attempt == retries - 1:
                logger.error(f"GTIN {gtin}: Failed after {retries} attempts")
            time.sleep(delay)
    
    logger.error(f"GTIN {gtin}: All attempts failed")
    return None

def process_hierarchy_structure(structure, level=0):
    logger.debug(f"Processing hierarchy structure at level {level} with {len(structure)} items")
    
    for i, item in enumerate(structure):
        indent = "  " * level
        parent_gtin = item.get('parentGtin')
        gtin = item.get('gtin')
        quantity = item.get('quantity')
        logger.debug(f"{indent}Item {i+1}: Parent GTIN: {parent_gtin}")
        logger.debug(f"{indent}Item {i+1}: GTIN: {gtin}")
        logger.debug(f"{indent}Item {i+1}: Quantity: {quantity}")
        
        children = item.get('children', [])
        if children:
            logger.debug(f"{indent}Item {i+1}: Has {len(children)} children")
            process_hierarchy_structure(children, level + 1)

def main():
    logger.info("Starting hierarchy fetching script...")
    
    try:
        # Read GTINs
        gtins = read_gtins(GTIN_CSV)
        logger.info(f"Total GTINs to process: {len(gtins)}")
        
        if len(gtins) == 0:
            logger.warning("No GTINs found to process")
            return
        
        # Process GTINs
        batch = []
        file_index = 1
        success_count = 0
        error_count = 0
        
        for idx, gtin in enumerate(gtins, 1):
            logger.info(f"Processing GTIN {idx}/{len(gtins)}: {gtin}")
            
            try:
                result = fetch_hierarchy(gtin)
                
                if result and isinstance(result, dict) and result.get('hierarchies'):
                    logger.info(f"GTIN {gtin}: Processing {len(result['hierarchies'])} hierarchies")
                    
                    for i, hierarchy in enumerate(result['hierarchies']):
                        logger.debug(f"GTIN {gtin}: Processing hierarchy {i+1}/{len(result['hierarchies'])}")
                        
                        hierarchy_gtin = hierarchy.get('gtin')
                        logger.debug(f"GTIN {gtin}: Hierarchy GTIN: {hierarchy_gtin}")
                        
                        hierarchy_structure = hierarchy.get('hierarchy', [])
                        logger.debug(f"GTIN {gtin}: Hierarchy structure has {len(hierarchy_structure)} items")
                        
                        process_hierarchy_structure(hierarchy_structure)
                        batch.append(hierarchy)
                        success_count += 1
                        
                elif result:
                    logger.warning(f"GTIN {gtin}: Response received but no 'hierarchies' key")
                    logger.debug(f"GTIN {gtin}: Response keys: {list(result.keys())}")
                else:
                    logger.warning(f"GTIN {gtin}: No result received")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"GTIN {gtin}: Error during processing: {e}")
                logger.error(f"GTIN {gtin}: Traceback: {traceback.format_exc()}")
                error_count += 1
            
            # Save batch if full or at end
            if len(batch) == BATCH_SIZE or idx == len(gtins):
                if batch:
                    file_path = os.path.join(OUTPUT_DIR, f"hierarchies_batch_{file_index}.json")
                    logger.info(f"Saving batch {file_index} with {len(batch)} hierarchies to {file_path}")
                    
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(batch, f, indent=2, ensure_ascii=False)
                        logger.info(f"Successfully saved batch {file_index} to {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to save batch {file_index}: {e}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    batch = []
                    file_index += 1
                else:
                    logger.warning(f"No hierarchies to save for batch {file_index}")
        
        # Final summary
        logger.info("=" * 50)
        logger.info("PROCESSING COMPLETE")
        logger.info(f"Total GTINs processed: {len(gtins)}")
        logger.info(f"Successful hierarchies: {success_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Batches saved: {file_index - 1}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    logger.info("Starting hierarchy fetching script...")
    try:
        main()
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 