from dotenv import load_dotenv
load_dotenv()

import sqlalchemy
from sqlalchemy import create_engine, text
import os
import sys
import logging
from collections import defaultdict
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load DATABASE_URL from .env
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Good Choice criteria for each category
CRITERIA = {
    'Baked Goods': {
        'sodium': ('<=', 290),
        'calories': ('<=', 300),
        'basis': 'BY_SERVING'
    },
    'Beverages': {
        'calories': ('<=', 25),  # per 8 fl. oz.
        'basis': 'BY_8_FLOZ'
    },
    'Cereal': {
        'sodium': ('<=', 200),
        'dietary_fiber': ('>=', 2),
        'sugars': ('<=', 10),
        'basis': 'BY_SERVING'
    },
    'Cheese/Cheese Substitutes': {
        'sodium': ('<=', 350),
        'basis': 'BY_SERVING'
    },
    'Desserts': {
        'sodium': ('<=', 480),
        'calories': ('<=', 200),
        'basis': 'BY_SERVING'
    },
    'Fruits, Vegetables, Beans, Nuts & Seeds': {
        'sodium': ('<=', 290),
        'basis': 'BY_SERVING'
    },
    'Grains & Pasta': {
        'dietary_fiber': ('>=', 3),
        'basis': 'BY_SERVING'
    },
    'Meat/Poultry/Other Animals - Unprepared/Unprocessed': {
        'sodium': ('<=', 290),
        'basis': 'BY_SERVING'
    },
    'Meat/Poultry/Other Animals - Prepared/Processed': {
        'sodium': ('<=', 480),
        'basis': 'BY_SERVING'
    },
    'Fish - Unprepared/Unprocessed': {
        'sodium': ('<=', 290),
        'basis': 'BY_SERVING'
    },
    'Milk & Milk Substitutes': {
        'total_fat': ('<=', 2.5),  # per 8 fl. oz.
        'basis': 'BY_8_FLOZ'
    },
    'Pre-Packaged Snacks': {
        'calories': ('<=', 200),  # per package
        'total_fat': ('<=', 7),
        'saturated_fat': ('<=', 2),
        'sodium': ('<=', 200),
        'sugars': ('<=', 10),
        'dietary_fiber': ('>=', 2),
        'basis': 'BY_PACKAGE'
    },
    'Prepared Foods': {
        'sodium': ('<=', 480),
        'basis': 'BY_SERVING'
    },
    'Sandwich Bread': {
        'sodium': ('<=', 180),  # per slice
        'dietary_fiber': ('>=', 2),
        'basis': 'BY_SLICE'
    },
    'Sauces, Dressings, and Dips': {
        'sodium': ('<=', 350),
        'basis': 'BY_SERVING'
    },
    'Yogurt': {
        'total_fat': ('<=', 3),  # per 8 oz.
        'sugars': ('<=', 30),    # per 8 oz.
        'basis': 'BY_8_OZ'
    },
}

def evaluate_good_choice(row, category):
    crit = CRITERIA.get(category)
    if not crit:
        logger.warning(f"Category '{category}' not found in CRITERIA. Marking as false.")
        return 'false'
    # Check basis
    if row.get('basis_quantity_type') != crit['basis']:
        return 'TBD'
    # Check all nutrient criteria
    for nutrient, rule in crit.items():
        if nutrient == 'basis':
            continue
        op, threshold = rule
        value = row.get(nutrient)
        if value is None:
            logger.info(f"Missing value for {nutrient} in category {category} (gtin: {row.get('gtin', 'unknown')}). Marking as false.")
            return 'false'
        if op == '<=' and not value <= threshold:
            return 'false'
        if op == '>=' and not value >= threshold:
            return 'false'
    return 'true'

def main():
    logging.info("Starting Good Choice evaluation...")
    with engine.connect() as conn:
        # Set timeouts to prevent hanging
        conn.execute(text("SET lock_timeout = '30s'; SET statement_timeout = '10min';"))
        
        # First, ensure the good_choice_processed column exists in product_classification table
        conn.execute(text('''
            ALTER TABLE product_classification 
            ADD COLUMN IF NOT EXISTS good_choice_processed BOOLEAN DEFAULT FALSE
        '''))
        conn.commit()
        
        # 1. Get products with nutrient_available=true and good_choice_processed=false
        products = conn.execute(text('''
            SELECT DISTINCT p.gtin, p.class_title as good_choice_category, s.basis_quantity_type
            FROM products p
            JOIN serving s ON p.gtin = s.gtin
            JOIN product_nutrition pn ON p.gtin = pn.gtin
            JOIN product_classification pc ON p.gtin = pc.gtin
            WHERE p.nutrient_available = true
            AND pc.good_choice_processed = false
        ''')).mappings().all()
        logging.info(f"Fetched {len(products)} products with nutrition info to process.")

        # 2. Get all nutrients for these products
        nutrients = conn.execute(text('''
            SELECT gtin, nutrient_label, standardized_value
            FROM product_nutrition
        ''')).mappings().all()
        logging.info(f"Fetched {len(nutrients)} nutrient records.")

        # 3. Organize nutrients by gtin
        nutrient_map = defaultdict(dict)
        for n in nutrients:
            nutrient_map[n['gtin']][n['nutrient_label']] = n['standardized_value']

        # 4. Evaluate and collect updates
        updates = []
        count_true = count_false = count_tbd = count_skipped = 0
        for row in tqdm(products, desc="Good Choice Evaluation"):
            gtin = row['gtin']
            category = row['good_choice_category']
            basis_quantity_type = row['basis_quantity_type']
            nutrient_dict = nutrient_map.get(gtin, {})
            if not nutrient_dict:
                count_skipped += 1
                logging.info(f"Skipping gtin {gtin} (no nutrients found).")
                continue
            nutrient_dict['basis_quantity_type'] = basis_quantity_type
            nutrient_dict['gtin'] = gtin
            status = evaluate_good_choice(nutrient_dict, category)
            if status == 'true':
                count_true += 1
            elif status == 'false':
                count_false += 1
            elif status == 'TBD':
                count_tbd += 1
            updates.append({'status': status, 'gtin': gtin})

        logging.info(f"Evaluation complete. true: {count_true}, false: {count_false}, TBD: {count_tbd}, skipped: {count_skipped}")

        # 5. Bulk update using VALUES for maximum performance (much faster than temp table)
        logging.info("Performing bulk update using VALUES clause...")
        with engine.begin() as conn2:
            # Create VALUES clause for bulk update
            values_clause = ','.join([f"('{update['gtin']}', '{update['status']}')" for update in updates])
            
            # Single bulk update using VALUES - update product_classification table
            result = conn2.execute(text(f'''
                UPDATE product_classification 
                SET is_good_choice = v.is_good_choice,
                    good_choice_processed = true
                FROM (VALUES {values_clause}) AS v(gtin, is_good_choice)
                WHERE product_classification.gtin = v.gtin
            '''))
            logging.info(f"Bulk update completed. {result.rowcount} records updated.")


if __name__ == '__main__':
    main()