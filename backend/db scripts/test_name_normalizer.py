import csv
from name_normalizer import normalize_product_name

INPUT_FILE = 'names.csv'
OUTPUT_FILE = 'names_normalized_test.csv'

results = []

with open(INPUT_FILE, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        name = row['name']
        norm = normalize_product_name(name)
        results.append({'name': name, 'normalized_name': norm})

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['name', 'normalized_name'])
    writer.writeheader()
    writer.writerows(results)

# Print a sample to console
print('Sample results:')
for r in results[:20]:
    print(f"{r['name']}  -->  {r['normalized_name']}") 