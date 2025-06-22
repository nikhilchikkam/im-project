import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

# DB config
db_config = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

# Load GPC codes from Excel
gpc_path = "GPC as of May 2025 v20250509 GB.xlsx"
gpc_df = pd.read_excel(gpc_path, sheet_name="gpc")
gpc_codes = tuple(map(str, gpc_df.iloc[:, 0]))

# Query DB
with psycopg2.connect(**db_config) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM products WHERE gpc_code IN %s", (gpc_codes,))
        match_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products WHERE gpc_code NOT IN %s", (gpc_codes,))
        non_match_count = cur.fetchone()[0]

        print("\n--- Random Non-Matching Products ---")
        cur.execute("""
            SELECT gtin, gpc_code 
            FROM products 
            WHERE gpc_code NOT IN %s 
            ORDER BY RANDOM()
            LIMIT 20
        """, (gpc_codes,))
        rows = cur.fetchall()

        for gtin, gpc in rows:
            print(f"GTIN: {gtin}, GPC: {gpc}")

print("\n--- GPC Code Match Summary ---")
print(f"Matching products   : {match_count}")
print(f"Non-matching products: {non_match_count}")

# ...after counting logic


