#!/usr/bin/env python3
"""
Maintain Product Classification Table

This script ensures that all product GTINs with nutrition data from the products table 
exist in the product_classification table. It creates missing records with default values 
to maintain data consistency.

Usage:
    python maintain_product_classification.py
"""

import os
import sys
import logging
import psycopg2
import psycopg2.extras
from tqdm import tqdm
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

def find_missing_gtins():
    """Find GTINs that exist in products with nutrition data but not in product_classification"""
    
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Find missing GTINs - only for products with nutrition data
        cursor.execute("""
            SELECT p.gtin
            FROM products p
            LEFT JOIN product_classification pc ON p.gtin = pc.gtin
            WHERE p.nutrient_available = true  -- Only products with nutrition data
              AND pc.gtin IS NULL
            ORDER BY p.gtin
        """)
        
        missing_gtins = cursor.fetchall()
        logger.info(f"Found {len(missing_gtins)} GTINs with nutrition data missing from product_classification")
        
        return missing_gtins
        
    except Exception as e:
        logger.error(f"Error finding missing GTINs: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def insert_missing_gtins(missing_gtins):
    """Insert missing GTINs into product_classification with default values"""
    
    if not missing_gtins:
        logger.info("No missing GTINs to insert")
        return 0
    
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Set timeouts
        cursor.execute("SET lock_timeout = '30s'; SET statement_timeout = '10min';")
        
        # Prepare data for bulk insert
        insert_data = []
        for (gtin,) in missing_gtins:
            insert_data.append((
                gtin,
                None,  # is_smart_snack
                None,  # snack_explanation
                None,  # super_segment
                None,  # segment
                None,  # sub_segment
                None,  # nova_group
                None,  # nova_group_name
                None,  # nova_group_label
                None,  # is_good_choice
                None,  # purchased_ok
                None,  # purchased_explanation
                None,  # recommended_ok
                None,  # recommended_explanation
                None,  # good_choice_category
                False,  # good_choice_processed
                False,  # smart_snack_processed
                False,  # philadelphia_processed
            ))
        
        # Bulk insert using execute_values for better performance
        from psycopg2.extras import execute_values
        
        execute_values(
            cursor,
            """
            INSERT INTO product_classification (
                gtin, is_smart_snack, snack_explanation, super_segment, segment, sub_segment,
                nova_group, nova_group_name, nova_group_label, is_good_choice, purchased_ok,
                purchased_explanation, recommended_ok, recommended_explanation, good_choice_category,
                good_choice_processed, smart_snack_processed, philadelphia_processed
            ) VALUES %s
            ON CONFLICT (gtin) DO NOTHING
            """,
            insert_data,
            template=None,
            page_size=1000
        )
        
        inserted_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"Successfully inserted {inserted_count} missing GTINs into product_classification")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Error inserting missing GTINs: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def verify_sync():
    """Verify that all product GTINs with nutrition data exist in product_classification"""
    
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    try:
        # Count products with nutrition data
        cursor.execute("SELECT COUNT(*) FROM products WHERE nutrient_available = true")
        total_products_with_nutrition = cursor.fetchone()[0]
        
        # Count product_classification records
        cursor.execute("SELECT COUNT(*) FROM product_classification")
        total_classifications = cursor.fetchone()[0]
        
        # Count missing GTINs (only for products with nutrition data)
        cursor.execute("""
            SELECT COUNT(*)
            FROM products p
            LEFT JOIN product_classification pc ON p.gtin = pc.gtin
            WHERE p.nutrient_available = true
              AND pc.gtin IS NULL
        """)
        missing_count = cursor.fetchone()[0]
        
        # Count total products for reference
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        logger.info(f"Verification Results:")
        logger.info(f"  Total products: {total_products}")
        logger.info(f"  Products with nutrition: {total_products_with_nutrition}")
        logger.info(f"  Total classifications: {total_classifications}")
        logger.info(f"  Missing GTINs (with nutrition): {missing_count}")
        logger.info(f"  Sync status: {'SYNCED' if missing_count == 0 else 'NOT SYNCED'}")
        
        return missing_count == 0
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to maintain product classification table"""
    
    logger.info("Starting product classification table maintenance...")
    
    try:
        # Step 1: Find missing GTINs
        missing_gtins = find_missing_gtins()
        
        # Step 2: Insert missing GTINs
        if missing_gtins:
            inserted_count = insert_missing_gtins(missing_gtins)
            logger.info(f"Inserted {inserted_count} missing GTINs")
        else:
            logger.info("No missing GTINs found")
        
        # Step 3: Verify synchronization
        is_synced = verify_sync()
        
        if is_synced:
            logger.info("Product classification table is fully synchronized!")
        else:
            logger.warning("Some GTINs are still missing from product_classification")
        
        return is_synced
        
    except Exception as e:
        logger.error(f"Maintenance failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
