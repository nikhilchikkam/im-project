#!/usr/bin/env python3
"""
Script to check how many batches have been processed by the ETL orchestrator
"""

import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')
load_dotenv('.env')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def count_products_per_batch():
    """Count products in database to estimate batches processed"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        # Count total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        # Get some sample products to check their structure
        cursor.execute("SELECT obj_id, gtin FROM products LIMIT 5")
        sample_products = cursor.fetchall()
        
        return total_products, sample_products
        
    except Exception as e:
        print(f"Error counting products: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def analyze_local_batches():
    """Analyze local batch files to understand structure"""
    batch_dir = "downloaded_batches"
    if not os.path.exists(batch_dir):
        print(f"Directory '{batch_dir}' not found")
        return None
    
    batch_files = [f for f in os.listdir(batch_dir) if f.endswith('.json')]
    batch_files.sort()  # Sort to get them in order
    
    if not batch_files:
        print("No batch files found")
        return None
    
    # Analyze first few batch files to understand structure
    batch_analysis = []
    
    for i, filename in enumerate(batch_files[:5]):  # Check first 5 files
        file_path = os.path.join(batch_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            products = data.get('products', [])
            batch_info = {
                'filename': filename,
                'products_count': len(products),
                'file_size': os.path.getsize(file_path),
                'batch_number': i + 1
            }
            
            if products:
                # Get sample product structure
                sample_product = products[0]
                batch_info['sample_obj_id'] = sample_product.get('objId', 'N/A')
                batch_info['sample_gtin'] = sample_product.get('gln', 'N/A')
            
            batch_analysis.append(batch_info)
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return batch_files, batch_analysis

def estimate_batches_processed():
    """Estimate how many batches have been processed"""
    print("=" * 70)
    print("ETL BATCH PROCESSING ANALYSIS")
    print("=" * 70)
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get database info
    db_result = count_products_per_batch()
    if not db_result:
        print("❌ Could not connect to database")
        return
    
    total_products_in_db, sample_products = db_result
    print(f"📊 Total products in database: {total_products_in_db:,}")
    
    # Get local batch info
    local_result = analyze_local_batches()
    if not local_result:
        print("❌ Could not analyze local batch files")
        return
    
    total_batch_files, batch_analysis = local_result
    print(f"📁 Total batch files available: {len(total_batch_files)}")
    print()
    
    # Analyze batch structure
    print("📋 BATCH FILE ANALYSIS (first 5 files):")
    print("-" * 70)
    
    total_products_in_batches = 0
    for batch in batch_analysis:
        print(f"Batch {batch['batch_number']:2d}: {batch['filename']}")
        print(f"         Products: {batch['products_count']:,} | Size: {batch['file_size']:,} bytes")
        print(f"         Sample ObjID: {batch['sample_obj_id']} | GTIN: {batch['sample_gtin']}")
        print()
        total_products_in_batches += batch['products_count']
    
    # Calculate average products per batch
    avg_products_per_batch = total_products_in_batches / len(batch_analysis)
    print(f"📈 Average products per batch: {avg_products_per_batch:,.0f}")
    print()
    
    # Estimate batches processed
    estimated_batches_processed = total_products_in_db / avg_products_per_batch
    estimated_batches_remaining = len(total_batch_files) - estimated_batches_processed
    
    print("🎯 BATCH PROCESSING ESTIMATE:")
    print("-" * 70)
    print(f"Estimated batches processed: {estimated_batches_processed:,.1f}")
    print(f"Estimated batches remaining: {estimated_batches_remaining:,.1f}")
    print(f"Progress: {(estimated_batches_processed / len(total_batch_files) * 100):.1f}%")
    print()
    
    # Check if processing is complete
    if estimated_batches_remaining <= 0:
        print("✅ ETL processing appears to be COMPLETE!")
        print(f"   All {len(total_batch_files)} batches have been processed")
    elif estimated_batches_remaining < 10:
        print("🟡 ETL processing is NEARLY COMPLETE!")
        print(f"   Only {estimated_batches_remaining:.0f} batches remaining")
    else:
        print("🔄 ETL processing is IN PROGRESS")
        print(f"   {estimated_batches_remaining:.0f} batches still need processing")
    
    print("=" * 70)

def check_processing_status():
    """Check if ETL is currently running"""
    print("\n🔍 CHECKING FOR ACTIVE ETL PROCESS:")
    print("-" * 70)
    
    # Check for Python processes that might be running ETL
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'python.exe' in result.stdout:
            print("🐍 Python processes found:")
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ No Python processes found running")
            
    except Exception as e:
        print(f"⚠️  Could not check for running processes: {e}")

if __name__ == "__main__":
    estimate_batches_processed()
    check_processing_status()

