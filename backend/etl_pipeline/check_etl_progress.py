#!/usr/bin/env python3
"""
Script to check ETL processing progress
Shows how many records have been processed in each table
"""

import os
import sys
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

def check_table_counts():
    """Check record counts in all relevant tables"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Tables to check
    tables = [
        'products',
        'product_nutrition', 
        'product_allergen',
        'serving',
        'product_diet_claims',
        'product_images'
    ]
    
    print("=" * 60)
    print("ETL PROCESSING PROGRESS CHECK")
    print("=" * 60)
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_records = 0
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:25} : {count:,} records")
            total_records += count
        except Exception as e:
            print(f"{table:25} : ERROR - {e}")
    
    print("-" * 60)
    print(f"{'TOTAL RECORDS':25} : {total_records:,}")
    print("=" * 60)
    
    # Check for recent activity
    print("\nRECENT ACTIVITY (last 24 hours):")
    print("-" * 60)
    
    try:
        cursor.execute("""
            SELECT table_name, COUNT(*) as recent_count
            FROM (
                SELECT 'products' as table_name, created_at FROM products WHERE created_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 'product_nutrition', created_at FROM product_nutrition WHERE created_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 'product_allergen', created_at FROM product_allergen WHERE created_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 'serving', created_at FROM serving WHERE created_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 'product_diet_claims', created_at FROM product_diet_claims WHERE created_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 'product_images', created_at FROM product_images WHERE created_at >= NOW() - INTERVAL '24 hours'
            ) recent_activity
            GROUP BY table_name
            ORDER BY table_name
        """)
        
        recent_results = cursor.fetchall()
        if recent_results:
            for table_name, count in recent_results:
                print(f"{table_name:25} : {count:,} records (last 24h)")
        else:
            print("No recent activity found in the last 24 hours")
            
    except Exception as e:
        print(f"Error checking recent activity: {e}")
    
    cursor.close()
    conn.close()

def check_batch_files():
    """Check how many batch files exist locally"""
    print("\n" + "=" * 60)
    print("LOCAL BATCH FILES")
    print("=" * 60)
    
    batch_dir = "downloaded_batches"
    if not os.path.exists(batch_dir):
        print(f"Directory '{batch_dir}' not found")
        return
    
    batch_files = [f for f in os.listdir(batch_dir) if f.endswith('.json')]
    print(f"Total batch files found: {len(batch_files)}")
    
    if batch_files:
        print("\nFirst 5 batch files:")
        for i, file in enumerate(batch_files[:5]):
            file_path = os.path.join(batch_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  {i+1}. {file} ({file_size:,} bytes)")
        
        if len(batch_files) > 5:
            print(f"  ... and {len(batch_files) - 5} more files")

if __name__ == "__main__":
    check_table_counts()
    check_batch_files()
