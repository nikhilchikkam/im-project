import os
import pandas as pd
from neo4j import GraphDatabase, basic_auth
from tqdm import tqdm

# --- CONFIGURATION ---
# Hardcoded for remote server:
NEO4J_URI = "bolt://167.99.147.151:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "nutrigence.app"
CSV_PATH = "product_hierarchies.csv"
BATCH_SIZE = 1000

CYPHER = """
UNWIND $batch AS row
MERGE (start:Product {gtin: row._start})
MERGE (end:Product {gtin: row._end})
MERGE (start)-[r:CONTAINS]->(end)
SET r.type = row._type,
    r.level = row.level,
    r.quantity = row.quantity
"""

def clean_value(val):
    if pd.isna(val) or val == '':
        return None
    try:
        f = float(val)
        if f.is_integer():
            return str(int(f))
        return str(f)
    except Exception:
        return str(val)

def main():
    print(f"Connecting to Neo4j at: {NEO4J_URI}")
    print(f"Using username: {NEO4J_USER}")
    print(f"Password set: {'yes' if NEO4J_PASSWORD and NEO4J_PASSWORD != 'your_neo4j_password' else 'no'}")
    df = pd.read_csv(CSV_PATH, dtype=str)
    df = df[['_start', '_end', '_type', 'level', 'quantity']]
    for col in ['_start', '_end', 'level', 'quantity']:
        df[col] = df[col].apply(clean_value)
    df['_type'] = df['_type'].fillna('CONTAINS')

    # Only keep rows that define relationships
    initial_len = len(df)
    df = df[df['_start'].notna() & df['_end'].notna() & (df['_start'] != '') & (df['_end'] != '')]
    print(f"Skipped {initial_len - len(df)} non-relationship rows (node-only rows).")

    driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
    total = len(df)
    errors = 0

    with driver.session() as session:
        for i in tqdm(range(0, total, BATCH_SIZE), desc="Uploading to Neo4j"):
            batch = df.iloc[i:i+BATCH_SIZE].to_dict('records')
            try:
                session.write_transaction(lambda tx: tx.run(CYPHER, batch=batch))
            except Exception as e:
                errors += 1
                print(f"Error in batch {i//BATCH_SIZE+1}: {e}")

    driver.close()
    print(f"Done! Uploaded {total} rows with {errors} batch errors.")

if __name__ == "__main__":
    main() 