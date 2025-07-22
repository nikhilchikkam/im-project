import os
import csv
import json
import time
from dotenv import load_dotenv
from oneworldsync import Content1Client
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()
client = Content1Client()

BATCH_SIZE = 100  # Number of GTINs per API call
ITEMS_PER_FILE = 1000  # Number of products per output file
OUTPUT_DIR = "results/products_by_gtin"
GTIN_CSV = "missing_gtin.csv"  # Path to your GTINs CSV

# Use a conservative number of parallel requests. Increase if API allows.
MAX_WORKERS = 5  # Adjust this if you know your API can handle more
MAX_RETRIES = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_gtins_from_csv(csv_path):
    gtins = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gtin = row.get('gtin') or row.get('GTIN') or row.get('Gtin')
            if gtin:
                gtins.append(str(gtin).strip())
    return gtins

def fetch_products_for_gtins(gtin_list, attempt=1):
    criteria = {
        "pullHierarchy": False,
        "gtin": gtin_list,
        "targetMarket": "US",
        "fields": {
            "include": [
                "gtin",
                "functionalName",
                "productDescription",
                "ingredientStatement",
                "brandName",
                "productType",
                "globalClassificationCategory"
            ],
            "exclude": []
        },
        "searchAfter": []
    }
    try:
        return client.fetch_products(criteria=criteria, page_size=len(gtin_list))
    except Exception as e:
        if attempt < MAX_RETRIES:
            print(f"Retrying sub-batch (attempt {attempt+1}) due to error: {e}")
            time.sleep(2 * attempt)
            return fetch_products_for_gtins(gtin_list, attempt=attempt+1)
        else:
            print(f"Failed sub-batch after {MAX_RETRIES} attempts: {e}")
            return {"items": []}

def main():
    gtins = read_gtins_from_csv(GTIN_CSV)
    print(f"Loaded {len(gtins)} GTINs from {GTIN_CSV}")

    total = len(gtins)
    file_index = 1
    for i in range(0, total, ITEMS_PER_FILE):
        batch_gtins = gtins[i:i+ITEMS_PER_FILE]
        batch_products = []
        sub_batches = [batch_gtins[j:j+BATCH_SIZE] for j in range(0, len(batch_gtins), BATCH_SIZE)]
        print(f"Processing file batch {file_index} with {len(sub_batches)} sub-batches...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_range = {
                executor.submit(fetch_products_for_gtins, sub): (j+i+1, j+i+len(sub))
                for j, sub in enumerate(sub_batches)
            }
            for future in as_completed(future_to_range):
                start_idx, end_idx = future_to_range[future]
                try:
                    result = future.result()
                    items = result.get("items", [])
                    batch_products.extend(items)
                    print(f"Fetched {len(items)} products for GTINs {start_idx}-{end_idx}")
                except Exception as e:
                    print(f"Error fetching GTINs {start_idx}-{end_idx}: {e}")
        file_name = os.path.join(OUTPUT_DIR, f"products_by_gtin_batch_{file_index}.json")
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(batch_products, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(batch_products)} products to {file_name}")
        file_index += 1

if __name__ == "__main__":
    main() 