import os
import pandas as pd
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Step 1: Load CSV with unit code → name mapping
mapping_df = pd.read_csv("Filtered_Nutrient_Attributes.csv")
mapping_df.columns = mapping_df.columns.str.strip().str.lower()

# Step 2: Clean and build mapping dictionary
mapping_df = mapping_df.dropna(subset=["code"])
mapping_df = mapping_df[mapping_df["code"].astype(str).str.strip() != ""]
unit_mapping = dict(zip(mapping_df["code"], mapping_df["name"]))

# Step 3: Connect and update DB
logging.info("Starting unit name updates...")
with engine.begin() as conn:
    for code, name in unit_mapping.items():
        conn.execute(text("""
            UPDATE product_nutrition
            SET unit_name = :name
            WHERE unit = :code
        """), {"name": name, "code": code})
        logging.info(f"Updated unit '{code}' to '{name}'")

logging.info("Unit name column updated successfully.")
