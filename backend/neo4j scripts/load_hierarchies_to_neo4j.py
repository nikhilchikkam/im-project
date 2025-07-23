import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://167.99.147.151:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Path to your results directory
RESULTS_DIR = "results/hierarchies_by_gtin"
MAX_WORKERS = 4  # Adjust based on server resources


def check_existing_relationship(tx, parent_gtin, child_gtin):
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
    if check_existing_relationship(tx, parent_gtin, child_gtin):
        return False
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
    return True

def process_hierarchy(tx, structure, parent_gtin=None, level=1):
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
        for child in item.get("children", []):
            child_created, child_skipped = process_hierarchy(tx, [child], gtin, level + 1)
            created_count += child_created
            skipped_count += child_skipped
    return created_count, skipped_count

def process_file(file_path):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    total_created = 0
    total_skipped = 0
    try:
        with driver.session() as session:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for i, hierarchy in enumerate(data, 1):
                    structure = hierarchy.get("hierarchy", [])
                    created, skipped = session.write_transaction(
                        process_hierarchy, structure, None, 1
                    )
                    total_created += created
                    total_skipped += skipped
        return os.path.basename(file_path), total_created, total_skipped, len(data)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return os.path.basename(file_path), 0, 0, 0
    finally:
        driver.close()

def main():
    files = [os.path.join(RESULTS_DIR, f) for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
    print(f"Found {len(files)} files to process.")
    summary = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f): f for f in files}
        for future in as_completed(futures):
            fname, created, skipped, count = future.result()
            print(f"{fname}: {count} hierarchies, {created} created, {skipped} skipped")
            summary.append((fname, created, skipped, count))
    total_created = sum(x[1] for x in summary)
    total_skipped = sum(x[2] for x in summary)
    total_hierarchies = sum(x[3] for x in summary)
    print(f"\nAll files processed.")
    print(f"Total hierarchies: {total_hierarchies}")
    print(f"Total relationships created: {total_created}")
    print(f"Total relationships skipped: {total_skipped}")
    print(f"Total relationships processed: {total_created + total_skipped}")

if __name__ == "__main__":
    main() 