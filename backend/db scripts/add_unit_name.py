import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load DB credentials
load_dotenv()
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

# Step 1: Load CSV with unit code → name mapping
mapping_df = pd.read_csv("Filtered_Nutrient_Attributes.csv")
mapping_df.columns = mapping_df.columns.str.strip().str.lower()

# Step 2: Clean and build mapping dictionary
mapping_df = mapping_df.dropna(subset=["code"])
mapping_df = mapping_df[mapping_df["code"].astype(str).str.strip() != ""]
unit_mapping = dict(zip(mapping_df["code"], mapping_df["name"]))

# Step 3: Connect and update DB
with psycopg2.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
        for code, name in unit_mapping.items():
            cur.execute("""
                UPDATE product_nutrition
                SET unit_name = %s
                WHERE unit = %s
            """, (name, code))
        conn.commit()

print("unit_name column updated successfully.")
