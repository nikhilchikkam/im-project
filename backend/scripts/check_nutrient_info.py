import os
import csv
import time
import logging
from dotenv import load_dotenv
from oneworldsync import Content1Client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()
BATCH_SIZE = 1000
INPUT_CSV = os.getenv("GTIN_INPUT_CSV", "no_nutrient_gtins.csv")
OUTPUT_CSV = os.getenv("GTIN_OUTPUT_CSV", "no_nutrient_flag.csv")
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "0.5"))

client = Content1Client()

def read_rows(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    return reader

def fetch_nutrient_info(gtin_batch):
    criteria = {
        "pullHierarchy": False,
        "gtin": gtin_batch,
        "targetMarket": "US",
        "fields": {
            "include": ["gtin","nutrientInformation"],
            "exclude": []
        },
        "searchAfter": []
    }
    return client.fetch_products(criteria)

def main():
    rows = read_rows(INPUT_CSV)
    if not rows:
        logging.error("No rows found in input CSV.")
        return
    gtin_col = 'gtin' if 'gtin' in rows[0] else list(rows[0].keys())[0]
    gtin_to_row = {row[gtin_col]: row for row in rows if row.get(gtin_col)}
    gtins = list(gtin_to_row.keys())
    logging.info(f"Loaded {len(gtins)} GTINs from {INPUT_CSV}")
    # Initialize all to False
    for row in rows:
        row['has_nutrient_info'] = ''
    for i in range(0, len(gtins), BATCH_SIZE):
        batch = gtins[i:i+BATCH_SIZE]
        try:
            data = fetch_nutrient_info(batch)
            # Map GTIN to presence of nutrient info
            gtin_has_nutrient = {}
            for item in data.get("items", []):
                gtin = item.get("item", {}).get("gtin")
                nutrient_info = item.get("item", {}).get("nutrientInformation")
                gtin_has_nutrient[gtin] = bool(nutrient_info)
            # Update rows
            for gtin in batch:
                row = gtin_to_row.get(gtin)
                if row is not None:
                    row['has_nutrient_info'] = gtin_has_nutrient.get(gtin, False)
            logging.info(f"Processed batch {i//BATCH_SIZE+1}: {len(batch)} GTINs")
        except Exception as e:
            logging.error(f"Error with batch {batch}: {e}")
        time.sleep(RATE_LIMIT_DELAY)
    # Write output CSV
    fieldnames = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    logging.info(f"Wrote output with nutrient info flag to {OUTPUT_CSV}")

if __name__ == "__main__":
    main() 