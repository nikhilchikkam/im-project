import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

DATA_DIR = r"E:\Projects\Mendon\results\products_with_diet_and_claim"
TABLE_NAME = "product_diet_claims"
MAX_WORKERS = 4
BATCH_SIZE = 500

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    gtin VARCHAR PRIMARY KEY,
    diet_types JSONB,
    claims JSONB
);
"""

UPSERT_SQL = f"""
INSERT INTO {TABLE_NAME} (gtin, diet_types, claims)
VALUES (%s, %s, %s)
ON CONFLICT (gtin) DO UPDATE SET
    diet_types = EXCLUDED.diet_types,
    claims = EXCLUDED.claims;
"""

def extract_diet_and_claims(item):
    gtin = item.get('gtin')
    # Diet types
    diet_types = []
    for diet in item.get('foodAndBevDietTypeInfo', []):
        code = diet.get('dietTypeCode')
        if code:
            diet_types.append(code)
    # Claims
    claims = {}
    for detail in item.get('productInformationDetail', []):
        for claim in detail.get('claimDetail', []):
            claim_type = claim.get('claimTypeCode')
            claim_elem = claim.get('claimElementCode')
            if claim_type and claim_elem:
                claims.setdefault(claim_type, []).append(claim_elem)
    return gtin, diet_types, claims

def process_file(file_path):
    records = []
    with open(file_path, encoding='utf-8') as f:
        try:
            data = json.load(f)
            for prod in data:
                item = prod.get('item', {})
                gtin, diet_types, claims = extract_diet_and_claims(item)
                if gtin:
                    records.append((gtin, json.dumps(diet_types), json.dumps(claims)))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return records

def main():
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    print(f"Found {len(files)} files to process.")
    all_records = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f): f for f in files}
        for future in as_completed(futures):
            records = future.result()
            all_records.extend(records)
            print(f"Processed {len(records)} records from {os.path.basename(futures[future])}")
    print(f"Total records to insert: {len(all_records)}")
    if not all_records:
        print("No records to insert.")
        return
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            for i in range(0, len(all_records), BATCH_SIZE):
                batch = all_records[i:i+BATCH_SIZE]
                execute_batch(cur, UPSERT_SQL, batch)
                print(f"Inserted/updated {i+len(batch)} of {len(all_records)} records...")
            conn.commit()
    print(f"Done. Inserted/updated {len(all_records)} records into '{TABLE_NAME}'.")

if __name__ == "__main__":
    main() 