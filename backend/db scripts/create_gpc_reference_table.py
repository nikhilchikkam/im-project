import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Load DB credentials from .env
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

# Load Excel
df = pd.read_excel("family_class_brick.xlsx").astype(str)

# SQL statements
create_table_sql = """
CREATE TABLE IF NOT EXISTS gpc_reference (
    family_code TEXT,
    family_title TEXT,
    class_code TEXT,
    class_title TEXT,
    brick_code TEXT PRIMARY KEY,
    brick_title TEXT
);
"""

insert_sql = """
INSERT INTO gpc_reference (family_code, family_title, class_code, class_title, brick_code, brick_title)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (brick_code) DO NOTHING;
"""


def create_and_populate():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)
                for _, row in df.iterrows():
                    cur.execute(insert_sql, tuple(row))
            conn.commit()
            print("gpc_reference table created and populated successfully.")
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    create_and_populate()
