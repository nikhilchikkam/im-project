#!/usr/bin/env python3
"""
Script to update nutrient_available and allergen_available flags in products table
based on data presence in product_nutrition and product_allergen tables.
"""

import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def ensure_availability_columns():
    """Ensure the availability columns exist in the products table"""
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('products')]
    
    with engine.begin() as conn:
        if 'nutrient_available' not in columns:
            conn.execute(text('ALTER TABLE products ADD COLUMN nutrient_available BOOLEAN DEFAULT FALSE'))
            logging.info('Added nutrient_available column to products table.')
        else:
            logging.info('nutrient_available column already exists.')
            
        if 'allergen_available' not in columns:
            conn.execute(text('ALTER TABLE products ADD COLUMN allergen_available BOOLEAN DEFAULT FALSE'))
            logging.info('Added allergen_available column to products table.')
        else:
            logging.info('allergen_available column already exists.')


def update_nutrient_availability():
    """Update nutrient_available flag based on data in product_nutrition table"""
    logging.info("Updating nutrient_available flags...")
    
    BATCH_SIZE = 10000
    
    # Get count and GTINs with nutrition data
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(DISTINCT gtin) 
            FROM product_nutrition
        """)).scalar()
        logging.info(f"Found {result} products with nutrition data")
        
        gtin_rows = conn.execute(text("""
            SELECT DISTINCT gtin 
            FROM product_nutrition
        """)).fetchall()
        gtins_with_nutrition = [row[0] for row in gtin_rows]
        logging.info(f"Retrieved {len(gtins_with_nutrition)} unique GTINs with nutrition data")
    
    # Update in batches with separate connections
    updated_count = 0
    for i in range(0, len(gtins_with_nutrition), BATCH_SIZE):
        batch_gtins = gtins_with_nutrition[i:i+BATCH_SIZE]
        
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE products 
                SET nutrient_available = TRUE 
                WHERE gtin = ANY(:gtins)
            """), {"gtins": batch_gtins})
            updated_count += result.rowcount
            logging.info(f"Updated batch {i//BATCH_SIZE + 1}: {result.rowcount} products with nutrient_available = TRUE")
    
    logging.info(f"Total updated: {updated_count} products with nutrient_available = TRUE")
    
    # Set nutrient_available = FALSE for products without nutrition data
    logging.info("Setting nutrient_available = FALSE for products without nutrition data...")
    with engine.begin() as conn:
        result = conn.execute(text("""
            UPDATE products 
            SET nutrient_available = FALSE 
            WHERE gtin NOT IN (
                SELECT DISTINCT gtin 
                FROM product_nutrition
            )
        """))
        logging.info(f"Updated {result.rowcount} products with nutrient_available = FALSE")


def update_allergen_availability():
    """Update allergen_available flag based on data in product_allergen table"""
    logging.info("Updating allergen_available flags...")
    
    BATCH_SIZE = 10000
    
    # Get count and GTINs with allergen data
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(DISTINCT gtin) 
            FROM product_allergen
        """)).scalar()
        logging.info(f"Found {result} products with allergen data")
        
        gtin_rows = conn.execute(text("""
            SELECT DISTINCT gtin 
            FROM product_allergen
        """)).fetchall()
        gtins_with_allergen = [row[0] for row in gtin_rows]
        logging.info(f"Retrieved {len(gtins_with_allergen)} unique GTINs with allergen data")
    
    # Update in batches with separate connections
    updated_count = 0
    for i in range(0, len(gtins_with_allergen), BATCH_SIZE):
        batch_gtins = gtins_with_allergen[i:i+BATCH_SIZE]
        
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE products 
                SET allergen_available = TRUE 
                WHERE gtin = ANY(:gtins)
            """), {"gtins": batch_gtins})
            updated_count += result.rowcount
            logging.info(f"Updated batch {i//BATCH_SIZE + 1}: {result.rowcount} products with allergen_available = TRUE")
    
    logging.info(f"Total updated: {updated_count} products with allergen_available = TRUE")
    
    # Set allergen_available = FALSE for products without allergen data
    logging.info("Setting allergen_available = FALSE for products without allergen data...")
    with engine.begin() as conn:
        result = conn.execute(text("""
            UPDATE products 
            SET allergen_available = FALSE 
            WHERE gtin NOT IN (
                SELECT DISTINCT gtin 
                FROM product_allergen
            )
        """))
        logging.info(f"Updated {result.rowcount} products with allergen_available = FALSE")


def get_availability_summary():
    """Get a summary of availability status"""
    logging.info("Getting availability summary...")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_products,
                COUNT(CASE WHEN nutrient_available = TRUE THEN 1 END) as products_with_nutrition,
                COUNT(CASE WHEN allergen_available = TRUE THEN 1 END) as products_with_allergens,
                COUNT(CASE WHEN nutrient_available = TRUE AND allergen_available = TRUE THEN 1 END) as products_with_both,
                COUNT(CASE WHEN nutrient_available = FALSE AND allergen_available = FALSE THEN 1 END) as products_with_neither
            FROM products
        """)).fetchone()
        
        logging.info("=== AVAILABILITY SUMMARY ===")
        logging.info(f"Total products: {result[0]}")
        logging.info(f"Products with nutrition data: {result[1]}")
        logging.info(f"Products with allergen data: {result[2]}")
        logging.info(f"Products with both nutrition and allergen data: {result[3]}")
        logging.info(f"Products with neither nutrition nor allergen data: {result[4]}")
        logging.info("===========================")


def main():
    """Main function to run the availability update process"""
    logging.info("Starting availability flag updates...")
    
    try:
        # Ensure columns exist
        ensure_availability_columns()
        
        # Update availability flags
        update_nutrient_availability()
        update_allergen_availability()
        
        # Get summary
        get_availability_summary()
        
        logging.info("Availability flag updates completed successfully!")
        
    except Exception as e:
        logging.error(f"Error updating availability flags: {e}")
        raise


if __name__ == '__main__':
    main()
