import os
import psycopg2
import pandas as pd
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

# Load Excel and build mapping
df = pd.read_excel("family_class_mapping.xlsx")
mapping = dict(zip(df["ClassTitle"].astype(str), df["FamilyTitle"]))

# Update DB
with psycopg2.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
        for class_title, family_title in mapping.items():
            cur.execute("""
                UPDATE products
                SET family_title = %s
                WHERE class_title = %s
            """, (family_title, class_title))
        conn.commit()

print("Family titles updated based on class titles.")
