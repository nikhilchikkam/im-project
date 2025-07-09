import os
import re
import logging
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

BATCH_SIZE = 1000

def normalize_product_name(name: str) -> str:
    name = name.strip()

    # Remove all dollar prices (e.g., "$2.00", "$.50", "$0.75", "$")
    name = re.sub(r'\$\s?\d*(\.\d{1,2})?', '', name)

    # Remove compound quantity-unit patterns (e.g., "3-2/40oz", "2/12pk")
    name = re.sub(
        r'\b\d+[-/]\d+/?\d*(\.\d+)?\s?(oz|g|kg|lb|lbs|ct|pk|pkg|pcs?|ml|l|fl oz|gram|ounce)\b',
        '', name, flags=re.IGNORECASE
    )

    # Remove bracketed unit phrases (e.g., "(18.6 FL OZ)", "(7 oz)")
    name = re.sub(
        r'\(\s*\d+(\.\d+)?\s?(fl\s)?(oz|g|kg|lb|lbs|ct|pk|pkg|pcs?|ml|l)\s*\)',
        '', name, flags=re.IGNORECASE
    )

    # Remove quantity-unit patterns anywhere in the string (e.g., "12 oz", "1 lb")
    name = re.sub(
        r'\b\d+(\.\d+)?\s?(oz|fl\s?oz|g|kg|lb|lbs|ct|pk|pkg|pcs?|each|ea|ml|l)\b',
        '', name, flags=re.IGNORECASE
    )

    # (Optional) Preserve numeric phrases like "18-22 slices per pound"
    # name = re.sub(r'\b\d+(\.\d+)?\b', '', name)

    # Clean up leading and trailing punctuation or symbols
    name = re.sub(r'^[\.\'"\s,]+', '', name)
    name = re.sub(r'[\.\'"\s,]+$', '', name)

    # Normalize internal whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Preserve acronyms by using temporary placeholders
    acronyms = ['PB&J', 'L/F', 'U.S.', 'A&E']
    for acronym in acronyms:
        pattern = re.compile(re.escape(acronym), re.IGNORECASE)
        name = pattern.sub(f"{{{{{acronym}}}}}", name)

    # Apply title case to the whole string
    name = name.title()

    # Restore acronyms from placeholders
    name = re.sub(r'\{\{(.*?)\}\}', r'\1', name)

    return name


def ensure_normalized_name_column():
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('products')]
    if 'normalized_name' not in columns:
        with engine.begin() as conn:
            conn.execute(text('ALTER TABLE products ADD COLUMN normalized_name TEXT'))
        logging.info('Added normalized_name column to products table.')
    else:
        logging.info('normalized_name column already exists.')

def update_normalized_names_batched():
    with engine.begin() as conn:
        gtin_rows = conn.execute(text('''
            SELECT gtin, name FROM products
            WHERE nutrient_avilable = TRUE
        ''')).fetchall()
        gtins = [row[0] for row in gtin_rows]
        logging.info(f'Fetched {len(gtins)} products with nutrient_avilable = TRUE.')
        for i in range(0, len(gtins), BATCH_SIZE):
            batch_gtins = gtins[i:i+BATCH_SIZE]
            # Fetch names for this batch
            products = conn.execute(
                text('SELECT gtin, name FROM products WHERE gtin = ANY(:gtins)'),
                {'gtins': batch_gtins}
            ).fetchall()
            updates = []
            for row in products:
                gtin, name = row
                norm = normalize_product_name(name or "")
                updates.append({'gtin': gtin, 'normalized_name': norm})
            for u in updates:
                conn.execute(
                    text('UPDATE products SET normalized_name = :normalized_name WHERE gtin = :gtin'),
                    u
                )
            logging.info(f'Updated batch {i//BATCH_SIZE + 1} ({len(updates)} records)')
    logging.info(f'Finished updating normalized_name for {len(gtins)} products.')

if __name__ == '__main__':
    ensure_normalized_name_column()
    update_normalized_names_batched() 