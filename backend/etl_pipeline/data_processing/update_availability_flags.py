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
    """Update nutrient_available flag to TRUE for products with nutrition data"""
    logging.info("Updating nutrient_available flags to TRUE...")
    
    # Update all products with nutrition data to TRUE in one batch
    with engine.begin() as conn:
        result = conn.execute(text("""
            UPDATE products 
            SET nutrient_available = TRUE 
            WHERE gtin IN (
                SELECT DISTINCT gtin 
                FROM product_nutrition
            )
        """))
        updated_count = result.rowcount
        logging.info(f"Updated {updated_count} products with nutrient_available = TRUE")
    
    # Get total count for summary
    with engine.connect() as conn:
        total_with_nutrition = conn.execute(text("""
            SELECT COUNT(DISTINCT gtin) 
            FROM product_nutrition
        """)).scalar()
        logging.info(f"Total products with nutrition data: {total_with_nutrition}")


def update_allergen_availability():
    """Update allergen_available flag to TRUE for products with allergen data"""
    logging.info("Updating allergen_available flags to TRUE...")
    
    # Update all products with allergen data to TRUE in one batch
    with engine.begin() as conn:
        result = conn.execute(text("""
            UPDATE products 
            SET allergen_available = TRUE 
            WHERE gtin IN (
                SELECT DISTINCT gtin 
                FROM product_allergen
            )
        """))
        updated_count = result.rowcount
        logging.info(f"Updated {updated_count} products with allergen_available = TRUE")
    
    # Get total count for summary
    with engine.connect() as conn:
        total_with_allergen = conn.execute(text("""
            SELECT COUNT(DISTINCT gtin) 
            FROM product_allergen
        """)).scalar()
        logging.info(f"Total products with allergen data: {total_with_allergen}")


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
