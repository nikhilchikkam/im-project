# smart_snack_etl.py

import re
import psycopg2
import psycopg2.extras
from tqdm import tqdm

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
    data = raw[0] if isinstance(raw, list) and raw else raw
    for s in data.get("servingSize", []):
        if s.get("qual", "").upper() == "OZA":
            try:
                return float(s.get("value", 0))
            except:
                pass
    return None

def format_success(rule, nutrition):
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
    text = ingredients or ""
    for grp in (4, 3, 2, 1):
        for rx in nova_rx[grp]:
            if rx.search(text):
                return grp
    return 1

def classify(ingredients, nutrition, family, class_title, raw, grade="Middle", segment="Snack"):
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
    conn = psycopg2.connect(dbname="nutrigence_db")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # ensure columns exist
    cur.execute("""
        ALTER TABLE products
          ADD COLUMN IF NOT EXISTS is_smart_snack boolean,
          ADD COLUMN IF NOT EXISTS snack_explanation text,
          ADD COLUMN IF NOT EXISTS nova_group integer;
    """)

    # fetch products
    cur.execute("""
      SELECT v.gtin, v.ingredients, v.raw_data,
             p.family_title, p.class_title,
             p.super_segment, p.segment
      FROM products_with_nutrition v
      JOIN products p USING(gtin)
    """)
    rows = cur.fetchall()

    upd = conn.cursor()
    for r in tqdm(rows, desc="processing"):
        gtin        = r["gtin"]
        ingredients = r["ingredients"] or ""
        family      = r["family_title"] or ""
        class_title = r["class_title"] or ""
        segment     = r["segment"] or "Snack"
        super_seg   = r["super_segment"] or "Snack"
        raw         = r["raw_data"] or []

        # build nutrient dict
        nutrients = {}
        info = raw[0].get("nutrientInformation") if isinstance(raw, list) and raw else raw.get("nutrientInformation", [])
        if isinstance(info, list):
            for block in info:
                for e in block.get("nutrientDetail", []):
                    val = 0.0
                    q = e.get("quantityContained") or []
                    if q:
                        try:
                            val = float(q[0].get("value", 0))
                        except:
                            pass
                    nutrients[e.get("nutrientTypeCode","")] = (val, e.get("measurementPrecisionCode",""))
        else:
            for e in raw[0].get("nutrientDetail", []):
                val = 0.0
                q = e.get("quantityContained") or []
                if q:
                    try:
                        val = float(q[0].get("value", 0))
                    except:
                        pass
                nutrients[e.get("nutrientTypeCode","")] = (val, e.get("measurementPrecisionCode",""))

        ok, reason = classify(
            ingredients, nutrients, family, class_title, raw,
            grade="Middle", segment=segment
        )
        ng = classify_nova_group(ingredients)

        upd.execute("""
          UPDATE products
             SET is_smart_snack   = %s,
                 snack_explanation = %s,
                 nova_group        = %s
           WHERE gtin = %s
        """, (ok, reason, ng, gtin))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
