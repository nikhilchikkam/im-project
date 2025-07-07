import os
import json
import psycopg2
import pandas as pd
from dotenv import load_dotenv
#from nutrition_loader import extract_nutrition, insert_nutrition, extract_daily_value_intake_percent, insert_daily_value_intake_percent
#from serving_loader import extract_serving, insert_serving
from allergen_loader import extract_allergens, insert_allergens

# Load DB credentials from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DATA_FOLDER = r"E:\Projects\Mendon\results\products2"
LOG_FILE = "bad_records.log"
CLASS_MAPPING_FILE = "family_class_brick.xlsx"

# Globals
success_count = 0
fail_count = 0
skip_count = 0
conn = None
valid_brick_codes = set()


def load_valid_brick_codes():
    df = pd.read_excel(CLASS_MAPPING_FILE)
    return set(str(code).strip() for code in df["BrickCode"].dropna().astype(str))


def log_bad_record(file, index, error):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{file} - Record #{index} - Error: {error}\n")


def process_file(file_path, cur):
    global success_count, fail_count, skip_count, conn

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            items = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Failed to load {file_path}: {e}")
            return

    for i, record in enumerate(items):
        try:
            item = record.get("item", {})
            gpc_code = str(item.get("globalClassificationCategory", {}).get("code"))

            if gpc_code not in valid_brick_codes:
                skip_count += 1
                continue

            # Only run allergen loader
            allergen_rows = extract_allergens(item)
            insert_allergens(cur, allergen_rows)

            conn.commit()
            success_count += 1

        except Exception as e:
            conn.rollback()
            fail_count += 1
            log_bad_record(os.path.basename(file_path), i, str(e))
            print(f"Error in record #{i} of {os.path.basename(file_path)}: {e}")


def process_all_files(folder_path):
    global conn, valid_brick_codes
    valid_brick_codes = load_valid_brick_codes()

    files = sorted(f for f in os.listdir(folder_path) if f.endswith(".json"))
    total = len(files)

    print(f"\nFound {total} JSON files to process.\n")

    with psycopg2.connect(DATABASE_URL) as db_conn:
        conn = db_conn
        with conn.cursor() as cur:
            for i, file in enumerate(files, 1):
                print(f"[{i}/{total}] Processing: {file}")
                process_file(os.path.join(folder_path, file), cur)

    print("\nAll files processed.")
    print(f"Success: {success_count}  Failed: {fail_count}  Skipped (Invalid GPC): {skip_count}")
    print(f"Errors logged in: {LOG_FILE}")


if __name__ == "__main__":
    process_all_files(DATA_FOLDER)
