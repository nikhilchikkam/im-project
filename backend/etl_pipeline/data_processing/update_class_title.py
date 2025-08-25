import os
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Get database URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")

logging.info("Starting class and family title updates using gpc_reference table...")

# Update products table using gpc_reference table
with psycopg2.connect(database_url) as conn:
    with conn.cursor() as cur:
        # Update class_title and family_title in products table by matching gpc_code with brick_code
        cur.execute("""
            UPDATE products p
            SET 
                class_title = g.class_title,
                family_title = g.family_title
            FROM gpc_reference g
            WHERE p.gpc_code = g.brick_code
            AND (p.class_title != g.class_title OR p.family_title != g.family_title OR p.class_title IS NULL OR p.family_title IS NULL)
        """)
        
        updated_count = cur.rowcount
        conn.commit()
        
        # Get summary statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_products,
                COUNT(CASE WHEN class_title IS NOT NULL THEN 1 END) as products_with_class,
                COUNT(CASE WHEN family_title IS NOT NULL THEN 1 END) as products_with_family,
                COUNT(CASE WHEN class_title IS NOT NULL AND family_title IS NOT NULL THEN 1 END) as products_with_both
            FROM products
        """)
        
        stats = cur.fetchone()
        
        logging.info(f"Updated {updated_count} products with class and family titles")
        logging.info(f"Total products: {stats[0]}")
        logging.info(f"Products with class_title: {stats[1]}")
        logging.info(f"Products with family_title: {stats[2]}")
        logging.info(f"Products with both: {stats[3]}")

print(f"Class and family titles updated using gpc_reference table. {updated_count} records updated.")
