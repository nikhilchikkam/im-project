#!/usr/bin/env python3
"""
Smart Snacks in School Standards Evaluator

This script evaluates products against USDA Smart Snacks in School nutrition standards.
Updated to work with current database schema and integrated into data processing pipeline.

Usage:
    python smart_snack_evaluator.py
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

# nutrient thresholds for snacks and entrées
THRESHOLDS = {
    "Snack": {
        "cal":          200,
        "sodium":       200,
        "fat_pct":      0.35,
        "sat_fat_pct":  0.10,
        "trans_fat":    0.0,
        "sugar_wt_pct": 0.35
    },
    "Entree": {
        "cal":          350,
        "sodium":       480,
        "fat_pct":      0.35,
        "sat_fat_pct":  0.10,
        "trans_fat":    0.0,
        "sugar_wt_pct": 0.35
    }
}

# beverage volume limits by school level
VOLUME_LIMITS = {
    "Water":         {"Elementary": float("inf"), "Middle": float("inf"), "High": float("inf")},
    "Milk":          {"Elementary": 8,             "Middle": 12,            "High": 12},
    "Juice":         {"Elementary": 8,             "Middle": 12,            "High": 12},
    "Diluted Juice": {"Elementary": 8,             "Middle": 12,            "High": 12},
    "LowNoCal":      {"Elementary": 0,             "Middle": 0,             "High": 20},
}

# NOVA group keyword patterns
nova_group_1 = [
    r"\bfresh\b", r"\braw\b", r"\bfrozen\b", r"\bdried\b", r"\bwhole\b",
    r"\bunprocessed\b", r"\bpasteuriz(?:ed|ation)?\b", r"\brefrigerat(?:ed)?\b",
    r"\bvacuum\s*pack(?:ed)?\b", r"\bnon[- ]alcoholic fermentation\b",
    r"\bfruit(?:s)?\b", r"\b(?:leafy )?vegetable(?:s)?\b", r"\blegume(?:s)?\b",
    r"\bbean(?:s)?\b", r"\blentil(?:s)?\b", r"\bchickpea(?:s)?\b",
    r"\b(?:grain|rice|wheat berry|corn cob|kernel)\b",
    r"\bpotato(?:es)?\b", r"\bsweet potato(?:es)?\b", r"\bcassava\b",
    r"\bfungus|mushroom(?:s)?\b", r"\bmeat\b", r"\bpoultry\b",
    r"\bfish\b", r"\bseafood\b", r"\bfillet(?:s)?\b", r"\bsteak(?:s)?\b",
    r"\begg(?:s)?\b", r"\bmilk\b", r"\byogurt\b", r"\bplain yogurt\b",
    r"\b(?!.*added)juice\b", r"\b(?:grit|flake|flour)s?\b",
    r"\bnut(?:s)?\b", r"\bseed(?:s)?\b", r"\bherb(?:s)?\b", r"\bspice(?:s)?\b",
    r"\b(?:thyme|oregano|mint|pepper|clove(?:s)?|cinnamon)\b",
    r"\b(?:dried mixed fruits|granola|pasta|couscous|polenta)\b",
]
nova_group_2 = [
    r"\boil(?:s)?\b", r"\bvegetable oil(?:s)?\b", r"\bolive oil\b",
    r"\bbutter\b", r"\blard\b", r"\bsalted butter\b",
    r"\bsugar\b", r"\bmolasses\b", r"\bhoney\b", r"\bmaple syrup\b",
    r"\bsyrup\b", r"\bstarch(?:es)?\b", r"\bcorn starch\b",
    r"\bpotato starch\b", r"\bsalt\b", r"\biodi(?:sed|zed) salt\b",
]
nova_group_3 = [
    r"\bcanned\b", r"\bbottled\b", r"\bjarred\b", r"\bbrine\b",
    r"\bsalted\b", r"\bsugared\b", r"\bdried\b", r"\bcured\b",
    r"\bsmoked\b", r"\bfruits? in syrup\b", r"\bbread(?:s)?\b",
    r"\bcheese(?:s)?\b",
]
nova_group_4 = [
    r"\b(snack|snacks)\b", r"\bchocolate(?:s)?\b", r"\bcandy\b",
    r"\bice[- ]?cream(?:s)?\b", r"\bcookie(?:s)?\b", r"\bbiscuit(?:s)?\b",
    r"\bpastry(?:ies)?\b", r"\bcake(?:s)?\b", r"\bcereal'?s? bar(?:s)?\b",
    r"\benergy drink(?:s)?\b", r"\bmeal replacement(?:s)?\b",
    r"\bpre[- ]?prepared\b", r"\binstant\b", r"\bhigh fructose corn syrup\b",
    r"\bhydrogenated oil(?:s)?\b", r"\bemulsifier(?:s)?\b", r"\bsweetener(?:s)?\b",
]

# compile regexes
nova_rx = {
    1: [re.compile(p, re.I) for p in nova_group_1],
    2: [re.compile(p, re.I) for p in nova_group_2],
    3: [re.compile(p, re.I) for p in nova_group_3],
    4: [re.compile(p, re.I) for p in nova_group_4],
}

def extract_serving_oz(raw):
    """Extract serving size in ounces from raw data"""
    if raw is None:
        return None
    data = raw[0] if isinstance(raw, list) and raw else raw
    if data is None:
        return None
    for s in data.get("servingSize", []):
        if s.get("qual", "").upper() == "OZA":
            try:
                return float(s.get("value", 0))
            except:
                pass
    return None

def format_success(rule, nutrition):
    """Format success message with nutrition details"""
    cal   = nutrition.get("ENER-",   (0,))[0]
    sod   = nutrition.get("NA",      (0,))[0]
    fat   = nutrition.get("FATNLEA", (0,))[0]
    sat   = nutrition.get("FASAT",   (0,))[0]
    trans = nutrition.get("FATRN",   (0,))[0]
    sugar = nutrition.get("SUGAR-",  (0,))[0]
    wt    = nutrition.get("CHO-",    (0,))[0] or 100

    fat_pct   = (fat * 9 / cal * 100) if cal else 0
    sat_pct   = (sat * 9 / cal * 100) if cal else 0
    sugar_pct = sugar / wt * 100

    return (
        f"{rule}\n"
        f"Nutrient values:\n"
        f"- Calories: {cal} kcal\n"
        f"- Sodium: {sod} mg\n"
        f"- Total fat: {fat_pct:.1f}% of calories ({fat} g)\n"
        f"- Sat. fat: {sat_pct:.1f}% of calories ({sat} g)\n"
        f"- Trans fat: {trans} g\n"
        f"- Total sugar: {sugar_pct:.1f}% by weight ({sugar} g)"
    )

def classify_nova_group(ingredients):
    """Classify product into NOVA processing group based on ingredients"""
    text = ingredients or ""
    for grp in (4, 3, 2, 1):
        for rx in nova_rx[grp]:
            if rx.search(text):
                return grp
    return 1

def classify(ingredients, nutrition, family, class_title, raw, grade="Middle", segment="Snack"):
    """Classify product against Smart Snacks standards"""
    cls = (class_title or "").strip().lower()
    fam = (family or "").strip().lower()
    size = extract_serving_oz(raw)

    # beverage rules
    if fam == "water":
        return True, format_success("Water always allowed", nutrition)

    if fam == "milk":
        lim = VOLUME_LIMITS["Milk"][grade]
        if size and size <= lim:
            return True, format_success(f"Milk ≤ {lim} fl oz", nutrition)
        return False, f"Milk size {size} fl oz > {lim} fl oz"

    if "juice" in fam and "diluted" not in fam:
        lim = VOLUME_LIMITS["Juice"][grade]
        if size and size <= lim:
            return True, format_success(f"100% juice ≤ {lim} fl oz", nutrition)
        return False, f"Juice size {size} fl oz > {lim} fl oz"

    if "diluted" in fam:
        lim = VOLUME_LIMITS["Diluted Juice"][grade]
        if size and size <= lim:
            return True, format_success(f"Diluted juice ≤ {lim} fl oz", nutrition)
        return False, f"Diluted juice size {size} fl oz > {lim} fl oz"

    if "low and no-calorie beverages" in fam:
        if grade != "High":
            return False, "Low/no-calorie beverages only allowed in High School"
        cal = nutrition.get("ENER-", (0,))[0]
        if size and ((size <= 8 and cal <= 40) or (size <= 12 and cal <= 60)):
            return True, format_success(f"Low-cal beverage: {cal} kcal in {size} fl oz", nutrition)
        if size and size <= 20 and cal <= 10:
            return True, format_success(f"No-cal beverage: {cal} kcal in {size} fl oz", nutrition)
        return False, f"Calories {cal} in {size} fl oz exceed limits"

    # fruit rules
    if "fruit" in cls:
        if any(k in cls for k in ("fresh", "canned", "frozen")):
            return True, format_success("Fruit exempt", nutrition)
        if "dried" in cls and not any(x in cls for x in ("mix", "trail", "nut", "seed")):
            return True, format_success("Dried whole fruit exempt", nutrition)
        if "dried" in cls and any(x in cls for x in ("mix", "trail", "nut", "seed")):
            errs = []
            cal = nutrition.get("ENER-", (0,))[0]
            sod = nutrition.get("NA", (0,))[0]
            if cal > THRESHOLDS["Snack"]["cal"]:
                errs.append(f"calories {cal} > {THRESHOLDS['Snack']['cal']}")
            if sod > THRESHOLDS["Snack"]["sodium"]:
                errs.append(f"sodium {sod} > {THRESHOLDS['Snack']['sodium']}")
            if errs:
                return False, "Dried fruit+seeds must meet limits:\n" + "\n".join(errs)
            return True, format_success("Dried fruit+seeds exempt", nutrition)

    # vegetable exempt
    if "vegetable" in cls:
        return True, format_success("Vegetable exempt", nutrition)

    # reduced-fat cheese
    if "dairy" in cls and "cheese" in cls and any(x in cls for x in ("reduced", "part-skim")):
        errs = []
        cal, sod, trans, sugar, wt = (nutrition.get(k, (0,))[0] for k in ("ENER-", "NA", "FATRN", "SUGAR-", "CHO-"))
        wt = wt or 100
        if cal  > THRESHOLDS["Snack"]["cal"]:
            errs.append(f"calories {cal} > {THRESHOLDS['Snack']['cal']}")
        if sod  > THRESHOLDS["Snack"]["sodium"]:
            errs.append(f"sodium {sod} > {THRESHOLDS['Snack']['sodium']}")
        if trans> THRESHOLDS["Snack"]["trans_fat"]:
            errs.append("trans-fat > 0")
        if sugar/wt > THRESHOLDS["Snack"]["sugar_wt_pct"]:
            errs.append("sugar > 35%")
        if errs:
            return False, "Reduced-fat cheese must meet limits:\n" + "\n".join(errs)
        return True, format_success("Reduced-fat cheese exempt", nutrition)

    # protein foods
    if "protein" in cls:
        if "seafood" in cls and "no added fat" in cls:
            errs = []
            cal, sod, sugar, wt = (nutrition.get(k, (0,))[0] for k in ("ENER-", "NA", "SUGAR-", "CHO-"))
            wt = wt or 100
            if cal  > THRESHOLDS["Snack"]["cal"]:
                errs.append(f"calories {cal} > {THRESHOLDS['Snack']['cal']}")
            if sod  > THRESHOLDS["Snack"]["sodium"]:
                errs.append(f"sodium {sod} > {THRESHOLDS['Snack']['sodium']}")
            if sugar/wt> THRESHOLDS["Snack"]["sugar_wt_pct"]:
                errs.append("sugar > 35%")
            if errs:
                return False, "Seafood must meet limits:\n" + "\n".join(errs)
            return True, format_success("Seafood exempt", nutrition)

        if any(kw in cls for kw in ("nut", "seed", "butter", "egg")):
            errs = []
            cal, sod, trans, sugar, wt = (nutrition.get(k, (0,))[0] for k in ("ENER-", "NA", "FATRN", "SUGAR-", "CHO-"))
            wt = wt or 100
            if cal  > THRESHOLDS["Snack"]["cal"]:
                errs.append(f"calories {cal} > {THRESHOLDS['Snack']['cal']}")
            if sod  > THRESHOLDS["Snack"]["sodium"]:
                errs.append(f"sodium {sod} > {THRESHOLDS['Snack']['sodium']}")
            if trans> THRESHOLDS["Snack"]["trans_fat"]:
                errs.append("trans-fat > 0")
            if sugar/wt> THRESHOLDS["Snack"]["sugar_wt_pct"]:
                errs.append("sugar > 35%")
            if errs:
                return False, "Protein foods must meet limits:\n" + "\n".join(errs)
            return True, format_success("Protein exempt", nutrition)

    # full nutrient standards check
    t = THRESHOLDS.get(segment, THRESHOLDS["Snack"])
    errs = []
    cal, sod, fat, sat, trans, sugar, wt = (
        nutrition.get(k, (0,))[0] for k in ("ENER-", "NA", "FATNLEA", "FASAT", "FATRN", "SUGAR-", "CHO-")
    )
    wt = wt or 100
    if cal and cal > t["cal"]:
        errs.append(f"calories {cal} > {t['cal']}")
    if sod and sod > t["sodium"]:
        errs.append(f"sodium {sod} > {t['sodium']}")
    if cal and (fat*9/cal) > t["fat_pct"]:
        errs.append("fat > 35% of cal")
    if cal and (sat*9/cal) > t["sat_fat_pct"]:
        errs.append("sat-fat > 10% of cal")
    if trans and trans > t["trans_fat"]:
        errs.append("trans-fat > 0")
    if (sugar/wt) > t["sugar_wt_pct"]:
        errs.append("sugar > 35% by weight")

    if errs:
        msg = f"{segment} does not meet standards:\n" + "\n".join(errs)
        return False, msg

    return True, format_success(f"Meets all {segment} standards", nutrition)

def main():
    """Main function to evaluate all products against Smart Snacks standards"""
    logger.info("Starting Smart Snacks evaluation...")
    
    # Get database connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    logger.info("Connecting to database...")
    conn = psycopg2.connect(database_url)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Set timeouts to prevent hanging
    cur.execute("SET lock_timeout = '30s'; SET statement_timeout = '10min';")

    # Create indexes for better performance (if they don't exist)
    logger.info("Creating indexes for better query performance...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_nutrient_available ON products(nutrient_available);
        CREATE INDEX IF NOT EXISTS idx_products_gtin ON products(gtin);
        CREATE INDEX IF NOT EXISTS idx_product_nutrition_gtin ON product_nutrition(gtin);
        CREATE INDEX IF NOT EXISTS idx_product_classification_gtin ON product_classification(gtin);
    """)

    # First, ensure the smart_snack_processed column exists in product_classification table
    cur.execute("""
        ALTER TABLE product_classification 
        ADD COLUMN IF NOT EXISTS smart_snack_processed BOOLEAN DEFAULT FALSE
    """)

    # fetch products with nutrition data (only unprocessed records) - optimized to fetch only needed nutrients
    logger.info("Fetching products with nutrition data (filtered: smart_snack_processed=false)...")
    cur.execute("""
      SELECT pc.gtin, p.ingredients, p.family_title, p.class_title,
             pn.nutrient_code, pn.nutrient_label, pn.value, pn.unit
      FROM product_classification pc
      JOIN products p ON p.gtin = pc.gtin
      JOIN product_nutrition pn ON p.gtin = pn.gtin
      WHERE pc.smart_snack_processed = false
        AND pn.nutrient_code IN ('ENER-', 'NA', 'FATNLEA', 'FASAT', 'FATRN', 'SUGAR-', 'CHO-')
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
                "family_title": r["family_title"] or "",
                "class_title": r["class_title"] or "",
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

    logger.info(f"Evaluating {len(nutrition_by_gtin)} products against Smart Snacks standards...")

    upd = conn.cursor()
    processed_count = 0
    smart_snack_count = 0
    
    for gtin, data in tqdm(nutrition_by_gtin.items(), desc="Smart Snacks Evaluation"):
        ingredients = data["ingredients"]
        family = data["family_title"]
        class_title = data["class_title"]
        segment = "Snack"  # Default to Snack since we don't have segment column
        super_seg = "Snack"  # Default to Snack since we don't have super_segment column
        nutrients = data["nutrients"]

        # Convert nutrients to the format expected by classify function
        nutrient_dict = {}
        for code, info in nutrients.items():
            nutrient_dict[code] = (info["value"], info.get("unit", ""))

        ok, reason = classify(
            ingredients, nutrient_dict, family, class_title, None,  # raw data is None
            grade="Middle", segment=segment
        )
        ng = classify_nova_group(ingredients)

        # Update product_classification table
        upd.execute("""
          UPDATE product_classification
             SET is_smart_snack   = %s,
                 snack_explanation = %s,
                 nova_group        = %s,
                 smart_snack_processed = true
           WHERE gtin = %s
        """, (ok, reason, ng, gtin))
        
        processed_count += 1
        if ok:
            smart_snack_count += 1
        
        # Log progress every 10,000 products
        if processed_count % 10000 == 0:
            logger.info(f"Processed {processed_count} products so far...")

    logger.info("Committing changes to database...")
    conn.commit()
    conn.close()
    
    logger.info(f"Smart Snacks evaluation completed successfully!")
    logger.info(f"Total products processed: {processed_count}")
    logger.info(f"Products meeting Smart Snacks standards: {smart_snack_count}")
    logger.info(f"Products NOT meeting standards: {processed_count - smart_snack_count}")

if __name__ == "__main__":
    main()
