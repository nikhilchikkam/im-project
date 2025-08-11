#!/usr/bin/env python3
"""
Script to check the current schema of the products table
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def check_products_schema():
    """Check the current schema of the products table"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if products table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'products'
            );
        """)
        
        table_exists = cur.fetchone()['exists']
        
        if not table_exists:
            print("❌ Products table does not exist!")
            return
        
        print("✅ Products table exists")
        
        # Get table schema
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'products'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        print(f"\n📋 Products table schema ({len(columns)} columns):")
        print("-" * 80)
        print(f"{'Column Name':<25} {'Data Type':<20} {'Nullable':<10} {'Default'}")
        print("-" * 80)
        
        for col in columns:
            default = col['column_default'] if col['column_default'] else 'NULL'
            print(f"{col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']:<10} {default}")
        
        # Check for specific columns that ProductLoader needs
        required_columns = [
            'gtin', 'name', 'description', 'ingredients', 'brand',
            'product_type', 'is_consumer_unit', 'gpc_code', 'raw_data', 'last_updated'
        ]
        
        existing_columns = [col['column_name'] for col in columns]
        
        print(f"\n🔍 Checking required columns for ProductLoader:")
        missing_columns = []
        for col in required_columns:
            if col in existing_columns:
                print(f"✅ {col}")
            else:
                print(f"❌ {col} - MISSING")
                missing_columns.append(col)
        
        if missing_columns:
            print(f"\n⚠️  Missing columns: {', '.join(missing_columns)}")
            print("You need to add these columns to the products table.")
        else:
            print(f"\n🎉 All required columns are present!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_products_schema() 