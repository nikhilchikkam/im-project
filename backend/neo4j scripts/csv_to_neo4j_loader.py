import os
import pandas as pd
from neo4j import GraphDatabase, basic_auth
from tqdm import tqdm

# --- CONFIGURATION ---
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://167.99.147.151:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
CSV_PATH = "product_hierarchies.csv"
BATCH_SIZE = 1000

# Only update or create nodes with gtin property
NODE_CYPHER = """
UNWIND $batch AS row
MERGE (p:Product {id: row.id})
SET p.gtin = row.gtin
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
    print(f"CSV columns: {df.columns.tolist()}")
    # Use '_id' if present, else 'id'
    id_col = 'id'
    if 'id' not in df.columns and '_id' in df.columns:
        id_col = '_id'
    # Clean values
    for col in [id_col, 'gtin', '_start', '_end']:
        if col in df.columns:
            df[col] = df[col].apply(clean_value)
    # Only process node-only rows: id and gtin present, _start and _end missing or empty
    node_rows = df[
        df[id_col].notna() & (df[id_col] != '') &
        df['gtin'].notna() & (df['gtin'] != '') &
        (df['_start'].isna() | (df['_start'] == '')) &
        (df['_end'].isna() | (df['_end'] == ''))
    ]
    print(f"Processing {len(node_rows)} Product nodes with gtin property...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        for i in tqdm(range(0, len(node_rows), BATCH_SIZE), desc="Nodes with gtin"):
            batch = node_rows.iloc[i:i+BATCH_SIZE][[id_col, 'gtin']].rename(columns={id_col: 'id'}).to_dict('records')
            try:
                session.write_transaction(lambda tx: tx.run(NODE_CYPHER, batch=batch))
            except Exception as e:
                print(f"Error in batch {i//BATCH_SIZE+1}: {e}")
    driver.close()
    print(f"Done! Updated/created {len(node_rows)} Product nodes with gtin.")

if __name__ == "__main__":
    main() 