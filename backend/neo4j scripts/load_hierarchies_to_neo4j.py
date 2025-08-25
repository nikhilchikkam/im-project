import os
import json
import time
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://167.99.147.151:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Path to your results directory
RESULTS_DIR = "results/hierarchies_by_gtin"
BATCH_SIZE = 500  # Process relationships in batches

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('neo4j_loader.log'),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return logging.getLogger(__name__)


def create_hierarchies_batch(tx, relationships_batch):
    """
    Create multiple relationships in a single transaction using UNWIND
    This is much faster than individual MERGE operations
    """
    if not relationships_batch:
        return 0, 0
    
    # Use UNWIND to process all relationships in one query
    result = tx.run(
        """
        UNWIND $relationships AS rel
        MERGE (parent:Product {gtin: rel.parent_gtin})
        MERGE (child:Product {gtin: rel.child_gtin})
        MERGE (parent)-[r:CONTAINS {quantity: rel.quantity, level: rel.level}]->(child)
        RETURN count(r) as created_count
        """,
        relationships=relationships_batch
    )
    
    # Count created relationships (MERGE will only create if doesn't exist)
    created_count = result.single()["created_count"]
    skipped_count = len(relationships_batch) - created_count
    
    return created_count, skipped_count

def extract_relationships_from_hierarchy(hierarchy_data, parent_gtin=None, level=1):
    """
    Extract all relationships from hierarchy structure
    Returns a list of relationship dictionaries
    """
    relationships = []
    
    for item in hierarchy_data:
        gtin = item.get("gtin")
        quantity = item.get("quantity", "1")
        
        if parent_gtin and gtin:
            relationships.append({
                "parent_gtin": parent_gtin,
                "child_gtin": gtin,
                "quantity": quantity,
                "level": level
            })
        
        # Process children recursively
        for child in item.get("children", []):
            child_relationships = extract_relationships_from_hierarchy(
                [child], gtin, level + 1
            )
            relationships.extend(child_relationships)
    
    return relationships

def process_file_with_logging(file_path, logger):
    """
    Process file with detailed logging
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    total_created = 0
    total_skipped = 0
    
    try:
        logger.info(f"Starting to process file: {os.path.basename(file_path)}")
        
        with driver.session() as session:
            # Load and parse file
            logger.info("Loading JSON file...")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            logger.info(f"Found {len(data)} hierarchies to process")
            
            # Extract all relationships
            logger.info("Extracting relationships from hierarchies...")
            all_relationships = []
            for i, hierarchy in enumerate(data):
                if i % 1000 == 0:  # Log progress every 1000 hierarchies
                    logger.info(f"Processed {i}/{len(data)} hierarchies...")
                
                structure = hierarchy.get("hierarchy", [])
                relationships = extract_relationships_from_hierarchy(structure)
                all_relationships.extend(relationships)
            
            logger.info(f"Extracted {len(all_relationships)} total relationships")
            
            # Process relationships in batches
            logger.info("Creating relationships in database...")
            num_batches = (len(all_relationships) + BATCH_SIZE - 1) // BATCH_SIZE
            logger.info(f"Will process {num_batches} batches of {BATCH_SIZE} relationships each")
            
            for i in range(0, len(all_relationships), BATCH_SIZE):
                batch = all_relationships[i:i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                
                # Use execute_write instead of write_transaction (fixes deprecation warning)
                created, skipped = session.execute_write(
                    create_hierarchies_batch, batch
                )
                
                total_created += created
                total_skipped += skipped
                
                # Log progress every 10 batches or at the end
                if batch_num % 10 == 0 or batch_num == num_batches:
                    logger.info(f"Batch {batch_num}/{num_batches} completed. "
                              f"Total created: {total_created}, skipped: {total_skipped}")
        
        logger.info(f"Completed processing {os.path.basename(file_path)}: "
                   f"{total_created} created, {total_skipped} skipped")
        return os.path.basename(file_path), total_created, total_skipped, len(data)
    
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return os.path.basename(file_path), 0, 0, 0
    finally:
        driver.close()

def main():
    # Setup logging
    logger = setup_logging()
    
    files = [os.path.join(RESULTS_DIR, f) for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
    files.sort()  # Process files in order
    
    logger.info(f"Found {len(files)} files to process:")
    for f in files:
        logger.info(f"  - {os.path.basename(f)}")
    
    logger.info(f"Starting processing with batch size {BATCH_SIZE}")
    start_time = time.time()
    
    summary = []
    
    # Process files sequentially for better progress visibility
    for file_path in files:
        fname, created, skipped, count = process_file_with_logging(file_path, logger)
        summary.append((fname, created, skipped, count))
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Final summary
    total_created = sum(x[1] for x in summary)
    total_skipped = sum(x[2] for x in summary)
    total_hierarchies = sum(x[3] for x in summary)
    
    logger.info("="*60)
    logger.info("PROCESSING COMPLETE")
    logger.info("="*60)
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info(f"Total hierarchies processed: {total_hierarchies}")
    logger.info(f"Total relationships created: {total_created}")
    logger.info(f"Total relationships skipped: {total_skipped}")
    logger.info(f"Total relationships processed: {total_created + total_skipped}")
    logger.info(f"Average time per file: {total_time/len(files):.2f} seconds")
    
    if total_created + total_skipped > 0:
        logger.info(f"Processing rate: {(total_created + total_skipped)/total_time:.0f} relationships/second")

if __name__ == "__main__":
    main() 