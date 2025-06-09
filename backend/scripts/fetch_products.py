import os
import json
import time
from dotenv import load_dotenv
from oneworldsync import Content1Client, AuthenticationError, APIError

# Load environment variables
load_dotenv()
client = Content1Client()

# Config
BATCH_SIZE = 1000
ITEMS_PER_FILE = 100_000

# Criteria: fetch everything
criteria = {
    "targetMarket": "US",
    "pullHierarchy": True,
    "sortFields": [
        {"field": "lastModifiedDate", "desc": True},
        {"field": "gtin", "desc": False}
    ]
}

def fetch_with_retry(criteria, page_size, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return client.fetch_products(criteria=criteria, page_size=page_size)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception("Failed after multiple retries.")

def fetch_all_products_batched():
    total = client.count_products(criteria)
    print(f"Total products: {total}")

    all_items = []
    search_after = None
    file_index = 1
    total_fetched = 0

    while total_fetched < total:
        # If we already wrote this batch, skip (resumable fetch)
        file_name = f"products_batch_{file_index}.json"
        if os.path.exists(file_name):
            print(f"{file_name} already exists. Skipping...")
            total_fetched += ITEMS_PER_FILE
            file_index += 1
            continue

        # Fetch up to ITEMS_PER_FILE
        batch_items = []
        while len(batch_items) < ITEMS_PER_FILE and total_fetched < total:
            if search_after:
                criteria["searchAfter"] = search_after

            result = fetch_with_retry(criteria, BATCH_SIZE)
            items = result.get("items", [])
            batch_items.extend(items)
            total_fetched += len(items)
            print(f"Fetched {total_fetched} / {total} items")

            if "searchAfter" not in result or not items:
                break
            search_after = result["searchAfter"]

        # Write this batch to file
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(batch_items, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(batch_items)} items to {file_name}")

        file_index += 1


if __name__ == "__main__":
    fetch_all_products_batched()
