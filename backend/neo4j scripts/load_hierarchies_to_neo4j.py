import os
import json
from neo4j import GraphDatabase

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "nut!q0)0N8V-"  # Change to your password

# Path to your results directory
RESULTS_DIR = "results/hierarchies_by_gtin"

def check_existing_relationship(tx, parent_gtin, child_gtin):
    """Check if a relationship already exists between parent and child"""
    result = tx.run(
        """
        MATCH (parent:Product {gtin: $parent_gtin})-[r:CONTAINS]->(child:Product {gtin: $child_gtin})
        RETURN count(r) as count
        """,
        parent_gtin=parent_gtin,
        child_gtin=child_gtin
    )
    return result.single()["count"] > 0

def create_hierarchy(tx, parent_gtin, child_gtin, quantity, level):
    """Create hierarchy relationship only if it doesn't already exist"""
    # Check if relationship already exists
    if check_existing_relationship(tx, parent_gtin, child_gtin):
        return False  # Relationship already exists
    
    # Create the relationship
    tx.run(
        """
        MERGE (parent:Product {gtin: $parent_gtin})
        MERGE (child:Product {gtin: $child_gtin})
        MERGE (parent)-[r:CONTAINS {quantity: $quantity, level: $level}]->(child)
        """,
        parent_gtin=parent_gtin,
        child_gtin=child_gtin,
        quantity=quantity,
        level=level
    )
    return True  # Relationship was created

def process_hierarchy(tx, structure, parent_gtin=None, level=1):
    """Process hierarchy structure with tracking of created relationships"""
    created_count = 0
    skipped_count = 0
    
    for item in structure:
        gtin = item.get("gtin")
        quantity = item.get("quantity")
        if parent_gtin and gtin:
            was_created = create_hierarchy(tx, parent_gtin, gtin, quantity, level)
            if was_created:
                created_count += 1
            else:
                skipped_count += 1
        
        # Recursively process children
        for child in item.get("children", []):
            child_created, child_skipped = process_hierarchy(tx, [child], gtin, level + 1)
            created_count += child_created
            skipped_count += child_skipped
    
    return created_count, skipped_count

def get_last_batch_file():
    """Get the last batch file (highest number)"""
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError("No JSON files found in results directory")
    
    # Sort by batch number
    files.sort(key=lambda x: int(x.split('_')[2].split('.')[0]))
    return files[-1]

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # Get the last batch file
        last_file = get_last_batch_file()
        print(f"Processing only the last file: {last_file}")
        
        with driver.session() as session:
            file_path = os.path.join(RESULTS_DIR, last_file)
            print(f"Loading data from {file_path}...")
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"Found {len(data)} hierarchies to process")
                
                total_created = 0
                total_skipped = 0
                
                for i, hierarchy in enumerate(data, 1):
                    if i % 100 == 0:  # Progress update every 100 hierarchies
                        print(f"Processed {i}/{len(data)} hierarchies...")
                    
                    structure = hierarchy.get("hierarchy", [])
                    created, skipped = session.write_transaction(
                        process_hierarchy, structure, None, 1
                    )
                    total_created += created
                    total_skipped += skipped
                
                print(f"\nProcessing complete!")
                print(f"Total relationships created: {total_created}")
                print(f"Total relationships skipped (already existed): {total_skipped}")
                print(f"Total relationships processed: {total_created + total_skipped}")
    
    except Exception as e:
        print(f"Error during processing: {e}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    main() 