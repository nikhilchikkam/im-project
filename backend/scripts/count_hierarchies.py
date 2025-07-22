import os
import json

output_dir = "results/hierarchies_by_gtin"
total = 0
file_count = 0

for filename in sorted(os.listdir(output_dir)):
    if filename.endswith(".json"):
        file_count += 1
        with open(os.path.join(output_dir, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            total += len(data)
        print(f"{filename}: {len(data)} hierarchies")

print(f"\nTotal files: {file_count}")
print(f"Total hierarchies: {total}")