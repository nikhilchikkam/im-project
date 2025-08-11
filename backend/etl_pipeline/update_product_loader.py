#!/usr/bin/env python3
"""
Updated product loader that handles lastModifiedDate from OneWorldSync data
and stores it in the last_updated column of the products table.
"""

import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('../.env')


DATABASE_URL = os.getenv("DATABASE_URL")

def parse_last_modified_date(last_modified_date_str):
    """
    Parse the lastModifiedDate from OneWorldSync data.
    OneWorldSync typically returns dates in ISO 8601 format.
    """
    if not last_modified_date_str:
        return None
    
    try:
        # Handle different date formats that OneWorldSync might return
        if isinstance(last_modified_date_str, str):
            # Remove timezone info if present and parse
            if 'T' in last_modified_date_str:
                # ISO format: "2024-01-01T12:00:00Z" or "2024-01-01T12:00:00.000Z"
                date_str = last_modified_date_str.split('T')[0]
                time_str = last_modified_date_str.split('T')[1].split('.')[0].replace('Z', '')
                datetime_str = f"{date_str} {time_str}"
                return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            else:
                # Date only format: "2024-01-01"
                return datetime.strptime(last_modified_date_str, '%Y-%m-%d')
        else:
            return None
    except Exception as e:
        print(f"Warning: Could not parse lastModifiedDate '{last_modified_date_str}': {e}")
        return None

def extract_product(item):
    """
    Extract product data from OneWorldSync item, including lastModifiedDate.
    """
    # Parse the lastModifiedDate
    last_modified_date = parse_last_modified_date(item.get("lastModifiedDate"))
    
    return {
        "gtin": item.get("gtin"),
        "name": item.get("functionalName", [{}])[0].get("value") if item.get("functionalName") else None,
        "description": item.get("productDescription", [{}])[0].get("value") if item.get("productDescription") else None,
        "ingredients": item.get("ingredientStatement", [{}])[0].get("statement", [{}])[0].get("value") if item.get("ingredientStatement") else None,
        "brand": item.get("brandName"),
        "product_type": item.get("productType"),
        "is_consumer_unit": item.get("isConsumerUnit") == "true",
        "gpc_code": item.get("globalClassificationCategory", {}).get("code") if item.get("globalClassificationCategory") else None,
        "raw_data": json.dumps(item),
        "last_updated": last_modified_date
    }

def insert_or_update_product(cur, product):
    """
    Insert or update a product in the database, including the last_updated field.
    """
    cur.execute("""
        INSERT INTO products (
            gtin, name, description, ingredients, brand,
            product_type, is_consumer_unit, gpc_code, raw_data, last_updated
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (gtin) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            ingredients = EXCLUDED.ingredients,
            brand = EXCLUDED.brand,
            product_type = EXCLUDED.product_type,
            is_consumer_unit = EXCLUDED.is_consumer_unit,
            gpc_code = EXCLUDED.gpc_code,
            raw_data = EXCLUDED.raw_data,
            last_updated = EXCLUDED.last_updated
    """, (
        product["gtin"], product["name"], product["description"],
        product["ingredients"], product["brand"], product["product_type"],
        product["is_consumer_unit"], product["gpc_code"], product["raw_data"],
        product["last_updated"]
    ))

def load_products_from_spaces(spaces_client, bucket, batch_key):
    """
    Load products from a batch file stored in DigitalOcean Spaces.
    """
    try:
        response = spaces_client.get_object(Bucket=bucket, Key=batch_key)
        batch_data = json.loads(response['Body'].read().decode('utf-8'))
        return batch_data.get('products', [])
    except Exception as e:
        print(f"Error loading products from {batch_key}: {e}")
        return []

def main():
    """
    Main function to load products from OneWorldSync data stored in Spaces.
    """
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Connected to database")
        
        # Check if last_updated column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'last_updated'
        """)
        
        if not cur.fetchone():
            print("❌ last_updated column not found. Please run the SQL script first:")
            print("   backend/etl_pipeline/add_last_updated_column.sql")
            return False
        
        print("✅ last_updated column found")
        
        # Example: Load products from a specific batch
        # You can modify this to load from multiple batches or all batches
        batch_key = "batches/batch_session_20241201_120000/batch_0001_products.json"
        
        # Load products from Spaces (you'll need to implement this based on your Spaces setup)
        # products = load_products_from_spaces(spaces_client, bucket, batch_key)
        
        # For now, let's show the structure
        print("📋 Product structure with last_updated:")
        sample_product = {
            "gtin": "1234567890123",
            "functionalName": [{"value": "Sample Product"}],
            "productDescription": [{"value": "Sample description"}],
            "ingredientStatement": [{"statement": [{"value": "Sample ingredients"}]}],
            "brandName": "Sample Brand",
            "productType": "Food",
            "isConsumerUnit": "true",
            "globalClassificationCategory": {"code": "10000000"},
            "lastModifiedDate": "2024-12-01T12:00:00Z"
        }
        
        extracted = extract_product(sample_product)
        print(f"  GTIN: {extracted['gtin']}")
        print(f"  Name: {extracted['name']}")
        print(f"  Last Updated: {extracted['last_updated']}")
        
        print("\n🎉 Product loader updated to handle lastModifiedDate!")
        print("💡 The last_updated column will store the lastModifiedDate from OneWorldSync")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 