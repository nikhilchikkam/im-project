import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Directory containing JSON files
DATA_DIR = r"E:/Projects/Mendon/results/products_by_gtin"

# Table and columns
TABLE_NAME = "one_worldsync_products"
COLUMNS = [
    "gtin",
    "name",
    "description",
    "ingredients",
    "brand",
    "product_type",
    "gpc_code"
]

# Create table if not exists (run once)
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    gtin VARCHAR PRIMARY KEY,
    name VARCHAR,
    description VARCHAR,
    ingredients VARCHAR,
    brand VARCHAR,
    product_type VARCHAR,
    gpc_code VARCHAR
);
"""

# Upsert SQL
UPSERT_SQL = f"""
INSERT INTO {TABLE_NAME} (gtin, name, description, ingredients, brand, product_type, gpc_code)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (gtin) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    ingredients = EXCLUDED.ingredients,
    brand = EXCLUDED.brand,
    product_type = EXCLUDED.product_type,
    gpc_code = EXCLUDED.gpc_code;
"""

def safe_str(val):
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)

def extract_fields(item):
    def get_first_value(val):
        if isinstance(val, list) and val:
            v = val[0]
            return v.get('value') if isinstance(v, dict) else v
        return val
    return (
        safe_str(item.get('gtin')),
        safe_str(get_first_value(item.get('functionalName'))),
        safe_str(get_first_value(item.get('productDescription'))),
        safe_str(item.get('ingredientStatement')),
        safe_str(item.get('brandName')),
        safe_str(item.get('productType')),
        safe_str((item.get('globalClassificationCategory') or {}).get('code'))
    )

def load_json_files(data_dir):
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    all_products = []
    for fname in files:
        path = os.path.join(data_dir, fname)
        with open(path, encoding='utf-8') as f:
            try:
                data = json.load(f)
                for prod in data:
                    item = prod.get('item', {})
                    if item.get('gtin'):
                        all_products.append(extract_fields(item))
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    print(f"Loaded {len(all_products)} products from {len(files)} files.")
    return all_products

def main():
    products = load_json_files(DATA_DIR)
    if not products:
        print("No products to insert.")
        return
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            print(f"Table '{TABLE_NAME}' checked/created.")
            batch_size = 500
            for i in range(0, len(products), batch_size):
                batch = products[i:i+batch_size]
                execute_batch(cur, UPSERT_SQL, batch)
                print(f"Inserted/updated {i+len(batch)} of {len(products)} products...")
            conn.commit()
    print(f"Done. Inserted/updated {len(products)} products into '{TABLE_NAME}'.")

if __name__ == "__main__":
    main() 