import json
import os
from pathlib import Path

def split_batch_29():
    """
    Split the large hierarchies_batch_29.json file into smaller files
    with 10,000 products each.
    """
    input_file = "results/hierarchies_by_gtin/hierarchies_batch_29.json"
    output_dir = "results/hierarchies_by_gtin"
    products_per_file = 10000
    
    print(f"Reading {input_file}...")
    
    # Read the large JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total_products = len(products)
    print(f"Total products in batch 29: {total_products}")
    
    # Calculate number of files needed
    num_files = (total_products + products_per_file - 1) // products_per_file
    print(f"Splitting into {num_files} files with {products_per_file} products each...")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Split and save files
    for i in range(num_files):
        start_idx = i * products_per_file
        end_idx = min((i + 1) * products_per_file, total_products)
        
        # Extract chunk of products
        chunk = products[start_idx:end_idx]
        
        # Create filename
        output_filename = f"hierarchies_batch_29_part_{i+1:03d}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save chunk to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
        
        print(f"Created {output_filename} with {len(chunk)} products (products {start_idx+1}-{end_idx})")
    
    print(f"\nSplit complete! Created {num_files} files in {output_dir}/")
    print("Files created:")
    for i in range(num_files):
        filename = f"hierarchies_batch_29_part_{i+1:03d}.json"
        print(f"  - {filename}")

if __name__ == "__main__":
    split_batch_29()