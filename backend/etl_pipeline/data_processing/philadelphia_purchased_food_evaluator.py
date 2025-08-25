#!/usr/bin/env python3
"""
Philadelphia Purchased Food Standards Evaluator

This script evaluates products against Philadelphia School District's Purchased Food Standards.
Updated to work with current database schema and integrated into data processing pipeline.

Usage:
    python philadelphia_purchased_food_evaluator.py
"""

import re
import os
import sys
import logging
import psycopg2
import psycopg2.extras
from tqdm import tqdm
from pathlib import Path
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

def classify_purchased(nutrients, ingredients, description, family, cls, super_seg, seg, sub_seg):
    """
    Classify product against Philadelphia Purchased Food Standards
    
    Returns: (purchased_ok, purchased_explanation, recommended_ok, recommended_explanation)
    """
    # Extract nutrient values
    cal = nutrients.get("ENER-", (0,))[0]
    sod = nutrients.get("NA", (0,))[0]
    fat = nutrients.get("FATNLEA", (0,))[0]
    sat = nutrients.get("FASAT", (0,))[0]
    trans = nutrients.get("FATRN", (0,))[0]
    sugar = nutrients.get("SUGAR-", (0,))[0]
    fiber = nutrients.get("FIBTG", (0,))[0]
    
    # Philadelphia Purchased Food Standards thresholds
    PURCHASED_THRESHOLDS = {
        "calories": 200,
        "sodium": 200,
        "fat_pct": 0.35,  # 35% of calories
        "sat_fat_pct": 0.10,  # 10% of calories
        "trans_fat": 0.0,
        "sugar_pct": 0.35,  # 35% by weight
        "fiber_min": 2  # minimum 2g fiber
    }
    
    RECOMMENDED_THRESHOLDS = {
        "calories": 150,
        "sodium": 140,
        "fat_pct": 0.30,  # 30% of calories
        "sat_fat_pct": 0.08,  # 8% of calories
        "trans_fat": 0.0,
        "sugar_pct": 0.25,  # 25% by weight
        "fiber_min": 3  # minimum 3g fiber
    }
    
    # Check purchased standards
    purchased_errors = []
    if cal > PURCHASED_THRESHOLDS["calories"]:
        purchased_errors.append(f"Calories {cal} > {PURCHASED_THRESHOLDS['calories']}")
    if sod > PURCHASED_THRESHOLDS["sodium"]:
        purchased_errors.append(f"Sodium {sod}mg > {PURCHASED_THRESHOLDS['sodium']}mg")
    if cal and (fat * 9 / cal) > PURCHASED_THRESHOLDS["fat_pct"]:
        purchased_errors.append(f"Total fat {(fat * 9 / cal * 100):.1f}% > 35% of calories")
    if cal and (sat * 9 / cal) > PURCHASED_THRESHOLDS["sat_fat_pct"]:
        purchased_errors.append(f"Saturated fat {(sat * 9 / cal * 100):.1f}% > 10% of calories")
    if trans > PURCHASED_THRESHOLDS["trans_fat"]:
        purchased_errors.append(f"Trans fat {trans}g > 0g")
    if fiber < PURCHASED_THRESHOLDS["fiber_min"]:
        purchased_errors.append(f"Fiber {fiber}g < {PURCHASED_THRESHOLDS['fiber_min']}g")
    
    purchased_ok = len(purchased_errors) == 0
    purchased_explanation = "Meets Philadelphia Purchased Food Standards" if purchased_ok else f"Does not meet standards: {'; '.join(purchased_errors)}"
    
    # Check recommended standards
    recommended_errors = []
    if cal > RECOMMENDED_THRESHOLDS["calories"]:
        recommended_errors.append(f"Calories {cal} > {RECOMMENDED_THRESHOLDS['calories']}")
    if sod > RECOMMENDED_THRESHOLDS["sodium"]:
        recommended_errors.append(f"Sodium {sod}mg > {RECOMMENDED_THRESHOLDS['sodium']}mg")
    if cal and (fat * 9 / cal) > RECOMMENDED_THRESHOLDS["fat_pct"]:
        recommended_errors.append(f"Total fat {(fat * 9 / cal * 100):.1f}% > 30% of calories")
    if cal and (sat * 9 / cal) > RECOMMENDED_THRESHOLDS["sat_fat_pct"]:
        recommended_errors.append(f"Saturated fat {(sat * 9 / cal * 100):.1f}% > 8% of calories")
    if trans > RECOMMENDED_THRESHOLDS["trans_fat"]:
        recommended_errors.append(f"Trans fat {trans}g > 0g")
    if fiber < RECOMMENDED_THRESHOLDS["fiber_min"]:
        recommended_errors.append(f"Fiber {fiber}g < {RECOMMENDED_THRESHOLDS['fiber_min']}g")
    
    recommended_ok = len(recommended_errors) == 0
    recommended_explanation = "Meets Philadelphia Recommended Standards" if recommended_ok else f"Does not meet recommended standards: {'; '.join(recommended_errors)}"
    
    return purchased_ok, purchased_explanation, recommended_ok, recommended_explanation

def main():
    """Main function to evaluate all products against Philadelphia Purchased Food Standards"""
    logger.info("Starting Philadelphia Purchased Food Standards evaluation...")
    
    # Get database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    logger.info("Connecting to database...")
    conn = psycopg2.connect(database_url)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Create indexes for better performance (if they don't exist)
    logger.info("Creating indexes for better query performance...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_nutrient_available ON products(nutrient_available);
        CREATE INDEX IF NOT EXISTS idx_products_gtin ON products(gtin);
        CREATE INDEX IF NOT EXISTS idx_product_nutrition_gtin ON product_nutrition(gtin);
        CREATE INDEX IF NOT EXISTS idx_product_classification_gtin ON product_classification(gtin);
        CREATE INDEX IF NOT EXISTS idx_product_classification_purchased ON product_classification(purchased_ok, recommended_ok);
    """)
    conn.commit()
    
    # First, ensure the philadelphia_processed column exists in product_classification table
    cur.execute("""
        ALTER TABLE product_classification 
        ADD COLUMN IF NOT EXISTS philadelphia_processed BOOLEAN DEFAULT FALSE
    """)
    conn.commit()
    
    # Fetch products with nutrition data and segment information (optimized query)
    logger.info("Fetching products with nutrition data and segment information (optimized)...")
    cur.execute("""
      WITH products_to_evaluate AS (
        SELECT p.gtin
        FROM products p
        LEFT JOIN product_classification pc ON pc.gtin = p.gtin
        WHERE p.nutrient_available = true
          AND (pc.philadelphia_processed = false OR pc.philadelphia_processed IS NULL)
      )
      SELECT p.gtin, p.ingredients, p.description, p.family_title, p.class_title,
             COALESCE(pc.super_segment, 'Snack') as super_segment,
             COALESCE(pc.segment, 'Snack') as segment,
             COALESCE(pc.sub_segment, 'Snack') as sub_segment,
             pn.nutrient_code, pn.nutrient_label, pn.value, pn.unit
      FROM products_to_evaluate pte
      JOIN products p ON p.gtin = pte.gtin
      JOIN product_nutrition pn ON p.gtin = pn.gtin
      LEFT JOIN product_classification pc ON pc.gtin = p.gtin
      WHERE pn.nutrient_code IN ('ENER-', 'NA', 'FATNLEA', 'FASAT', 'FATRN', 'SUGAR-', 'FIBTG')
      ORDER BY p.gtin, pn.nutrient_code
    """)
    rows = cur.fetchall()
    logger.info(f"Found {len(rows)} nutrition records to process...")

    # Group nutrition data by GTIN
    logger.info("Grouping nutrition data by product...")
    nutrition_by_gtin = {}
    for r in rows:
        gtin = r["gtin"]
        if gtin not in nutrition_by_gtin:
             nutrition_by_gtin[gtin] = {
                 "ingredients": r["ingredients"] or "",
                 "description": r["description"] or "",
                 "family_title": r["family_title"] or "",
                 "class_title": r["class_title"] or "",
                 "super_segment": r["super_segment"],  # Already has COALESCE default
                 "segment": r["segment"],  # Already has COALESCE default
                 "sub_segment": r["sub_segment"],  # Already has COALESCE default
                 "nutrients": {}
             }
        
        # Add nutrition data
        nutrient_code = r["nutrient_code"]
        nutrient_label = r["nutrient_label"]
        value = r["value"]
        unit = r["unit"]
        
        if nutrient_code and value is not None:
            try:
                nutrition_by_gtin[gtin]["nutrients"][nutrient_code] = {
                    "value": float(value),
                    "label": nutrient_label,
                    "unit": unit
                }
            except (ValueError, TypeError):
                continue

    logger.info(f"Evaluating {len(nutrition_by_gtin)} products against Philadelphia Purchased Food Standards...")

    upd = conn.cursor()
    processed_count = 0
    purchased_ok_count = 0
    recommended_ok_count = 0
    
    for gtin, data in tqdm(nutrition_by_gtin.items(), desc="Philadelphia Purchased Food Evaluation"):
        # Convert nutrients to the format expected by classify_purchased function
        nutrients = {}
        for code, info in data["nutrients"].items():
            nutrients[code] = (info["value"], info.get("unit", ""))

        purchased_ok, purchased_expl, recommended_ok, recommended_expl = classify_purchased(
            nutrients,
            data["ingredients"],
            data["description"],
            data["family_title"],
            data["class_title"],
            data["super_segment"],
            data["segment"],
            data["sub_segment"]
        )

        # Update product_classification table
        upd.execute("""
          UPDATE product_classification
             SET purchased_ok            = %s,
                 purchased_explanation   = %s,
                 recommended_ok          = %s,
                 recommended_explanation = %s,
                 philadelphia_processed  = true
           WHERE gtin = %s
        """, (purchased_ok, purchased_expl, recommended_ok, recommended_expl, gtin))
        
        processed_count += 1
        if purchased_ok:
            purchased_ok_count += 1
        if recommended_ok:
            recommended_ok_count += 1
        
        # Log progress every 10,000 products
        if processed_count % 10000 == 0:
            logger.info(f"Processed {processed_count} products so far...")

    logger.info("Committing changes to database...")
    conn.commit()
    conn.close()
    
    logger.info(f"Philadelphia Purchased Food Standards evaluation completed successfully!")
    logger.info(f"Total products processed: {processed_count}")
    logger.info(f"Products meeting Purchased standards: {purchased_ok_count}")
    logger.info(f"Products meeting Recommended standards: {recommended_ok_count}")
    logger.info(f"Products NOT meeting Purchased standards: {processed_count - purchased_ok_count}")
    logger.info(f"Products NOT meeting Recommended standards: {processed_count - recommended_ok_count}")

if __name__ == "__main__":
    main()
