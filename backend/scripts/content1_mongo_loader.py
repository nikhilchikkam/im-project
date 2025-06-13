import os
import json
from pymongo import MongoClient, errors

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["mendon_db"]
collection = db["products"]

# Directory containing JSON files
PRODUCTS_DIR = r"E:/Projects/Mendon/results/products"
BATCH_PREFIX = "products_batch_"

# Stats
total_inserted = 0
total_duplicates = 0
total_skipped = 0

# Process each batch file
for file_name in sorted(os.listdir(PRODUCTS_DIR)):
    if file_name.startswith(BATCH_PREFIX) and file_name.endswith(".json"):
        file_path = os.path.join(PRODUCTS_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            products = json.load(f)

            docs_to_insert = []
            for product in products:
                obj_id = product.get("objId")
                if obj_id is not None:
                    product["_id"] = obj_id
                    docs_to_insert.append(product)
                else:
                    total_skipped += 1

            try:
                result = collection.insert_many(docs_to_insert, ordered=False)
                inserted_count = len(result.inserted_ids)
                total_inserted += inserted_count
                print(f"{file_name}: Inserted {inserted_count}")
            except errors.BulkWriteError as bwe:
                inserted_count = bwe.details.get("nInserted", 0)
                error_count = len(bwe.details.get("writeErrors", []))
                total_inserted += inserted_count
                total_duplicates += error_count
                print(f"{file_name}: Inserted {inserted_count}, Duplicates Skipped {error_count}")

# Summary
print("\nInsertion Complete")
print(f"Total Inserted: {total_inserted}")
print(f"Total Duplicates Skipped: {total_duplicates}")
print(f"Total Products Without objId Skipped: {total_skipped}")
