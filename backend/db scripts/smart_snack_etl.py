#!/usr/bin/env python3
import re
import psycopg2
from psycopg2.extras import DictCursor
from tqdm import tqdm

# ——————————————————————————————————————————————
# 1) Compile shared regexes
# ——————————————————————————————————————————————
PH_PARTIALLY_HYDRO_RX = re.compile(r"part(ially)?\s+hydrogenat", re.I)
PH_HYDRO_RX           = re.compile(r"hydrogenated", re.I)
ARTIFICIAL_SWEET_RX   = re.compile(r"(aspartame|sucralose|acesulfame|saccharin)", re.I)
LOW_SODIUM_RX         = re.compile(r"(low[- ]?sodium|reduced[- ]?sodium)", re.I)
WHOLE_GRAIN_RX        = re.compile(r"whole[- ]?grain", re.I)
SWEETENED_BEV_RX      = re.compile(r"(sugar|sweet)", re.I)

def classify_purchased(nutrients, ingredients, description,
                       family, cls, super_seg, seg, sub_seg):
    """
    Returns (bool req_ok, str req_expl, bool rec_ok, str rec_expl)
    according to the Philly Purchased Food Standards (2.2022).
    Each rule only fires if its category appears anywhere in
    super_seg/seg/sub_seg/family/cls/description/ingredients.
    """
    ing  = (ingredients or "").lower()
    desc = (description or "").lower()
    fam  = (family      or "").lower()
    cls  = (cls         or "").lower()

    # pull out key nutrients (default 0)
    cal   = nutrients.get("ENER-",   (0,))[0]
    sod   = nutrients.get("NA",      (0,))[0]
    fatg  = nutrients.get("FATNLEA", (0,))[0]
    sugar = nutrients.get("SUGAR-",  (0,))[0]
    satg  = nutrients.get("FASAT",   (0,))[0]
    fib   = nutrients.get("FIBTSW",  (0,))[0]

    req_errs = []

    # — A) Trans‐fat —
    if nutrients.get("FATRN", (0,))[0] != 0:
        req_errs.append(f"Trans fat {nutrients['FATRN'][0]}g → must be 0g")
    if PH_PARTIALLY_HYDRO_RX.search(ing) or PH_PARTIALLY_HYDRO_RX.search(desc):
        req_errs.append("Contains partially hydrogenated oil")

    # — B) Sodium —
    if sod > 480:
        req_errs.append(f"Sodium {sod}mg → exceeds 480mg limit")

    # — C) Breaded/pre‐fried —
    if any(w in fam for w in ("breaded","fried")) \
    or any(w in cls for w in ("breaded","fried")) \
    or "breaded" in desc or "fried" in desc \
    or "breaded" in ing  or "fried" in ing:
        req_errs.append("Breaded or pre‐fried products are not allowed")

    # helper: is a beverage?
    bev = any([
        super_seg.lower()=="beverage",
        seg.lower()=="beverage",
        sub_seg.lower()=="beverage",
        "beverage" in fam,
        "beverage" in cls,
        "beverage" in desc,
        "beverage" in ing,
    ])
    # — D) Beverages ≤40 kcal (juice & milk exempt) —
    if bev and not fam.startswith("juice") and fam != "milk":
        if cal > 40:
            req_errs.append(f"Beverage calories {cal}kcal → exceeds 40kcal limit")
    
      # helper: is dairy?  (only by true category flags)
    dairy = any([
        super_seg.lower()=="dairy",
        seg.lower()=="dairy",
        sub_seg.lower()=="dairy",
        fam == "milk",
        cls.startswith("milk"),
        "yogurt" in cls,
        "cheese" in cls,
   ])

     # — E) Dairy rules —
    if dairy:
        # milk
        if fam=="milk" or cls.startswith("milk"):
            if fatg > 1:
                req_errs.append(f"Milk fat {fatg}g → must be ≤1g")
            if ARTIFICIAL_SWEET_RX.search(ing):
                req_errs.append("Milk must be unsweetened & unflavored")
        # yogurt
        if "yogurt" in cls:
            if sugar > 27:
                req_errs.append(f"Yogurt sugar {sugar}g → exceeds 27g per 8oz")
            if not any(x in ing for x in ("non-fat","low-fat")):
                req_errs.append("Yogurt must be non-fat or low-fat")
            if ARTIFICIAL_SWEET_RX.search(ing):
                req_errs.append("Yogurt must have no artificial sweeteners")
        # processed cheese
        if "cheese" in cls and "processed" in cls:
            if sod > 230:
                req_errs.append(f"Processed cheese sodium {sod}mg → exceeds 230mg")
    # helper: grain/bakery?
    grain = any([
        seg.lower() in ("bread/bakery products","cereal/grain/pulse products","whole grain"),
        super_seg.lower() in ("bread/bakery products","cereal/grain/pulse products","whole grain"),
        sub_seg.lower() in ("bread/bakery products","cereal/grain/pulse products","whole grain"),
        any(x in cls for x in ("bread","tortilla","wrap","bun","roll","muffin","bagel","waffle","croissant")),
        any(x in fam for x in ("bread","grain","tortilla","wrap")),
        any(x in desc for x in ("bread","grain","tortilla","wrap")),
        any(x in ing  for x in ("bread","grain","tortilla","wrap")),
    ])
    # — F) Grains & starches —
    if grain:
        if any(x in cls for x in ("bread","tortilla","wrap")):
            if sod > 180:
                req_errs.append(f"Bread/tortilla sodium {sod}mg → exceeds 180mg")
            if fib < 2:
                req_errs.append(f"Grain fiber {fib}g → must be ≥2g")
        if any(x in cls for x in ("bun","roll","muffin","bagel","waffle","croissant")):
            if sod > 290:
                req_errs.append(f"Grain sodium {sod}mg → exceeds 290mg")
            if any(x in cls for x in ("muffin","croissant","pastry","bar")) and sugar > 12:
                req_errs.append(f"Pastry sugar {sugar}g → exceeds 12g")

    # — G) Cereal —
    if any(w in cls+fam+desc+ing for w in ("cereal",)):
        if sod > 215:
            req_errs.append(f"Cereal sodium {sod}mg → exceeds 215mg")
        if sugar > 10:
            req_errs.append(f"Cereal sugar {sugar}g → exceeds 10g")
        if fib < 2:
            req_errs.append(f"Cereal fiber {fib}g → must be ≥2g")

    # helper: veg/bean?
    veg = any([
        seg.lower()=="vegetable",
        super_seg.lower()=="vegetable",
        sub_seg.lower()=="vegetable",
        "vegetable" in cls or "bean" in cls,
        "vegetable" in fam or "bean" in fam,
        "vegetable" in desc or "bean" in desc,
        "vegetable" in ing  or "bean" in ing,
    ])
    # — H) Vegetables & beans —
    if veg and sod > 290:
        req_errs.append(f"Vegetable/bean sodium {sod}mg → exceeds 290mg")

    # helper: fruit?
    fruit = any([
        seg.lower()=="fruit",
        super_seg.lower()=="fruit",
        sub_seg.lower()=="fruit",
        "fruit" in cls or "fruit" in fam,
        "fruit" in desc or "fruit" in ing,
    ])
    # — I) Canned/frozen fruit —
    if fruit and any(x in cls for x in ("canned","frozen")):
        if "syrup" in ing or "syrup" in desc:
            req_errs.append("Canned/frozen fruit must be unsweetened")

    # — J) Canned/frozen seafood —
    if any(x in cls for x in ("seafood",)) and any(x in cls for x in ("canned","frozen")):
        if sod > 290:
            req_errs.append(f"Seafood sodium {sod}mg → exceeds 290mg")

    # — K) Beef & pork lean ≤10% fat —
    if any(w in cls+fam+desc+ing for w in ("beef","pork")):
        if cal and (fatg*9/cal*100) > 10:
            pct = fatg*9/cal*100
            req_errs.append(f"Meat fat% {pct:.1f}% → must be ≤10%")

    # — L) Poultry —
    if "poultry" in cls+fam+desc+ing:
        if any(x in cls for x in ("canned","frozen")) and sod > 290:
            req_errs.append(f"Poultry sodium {sod}mg → exceeds 290mg")
        if "ground" in desc and cal and (fatg*9/cal*100) > 10:
            pct = fatg*9/cal*100
            req_errs.append(f"Ground poultry fat% {pct:.1f}% → must be ≤10%")

    # — M) Sausages —
    if "sausage" in cls+fam+desc+ing and sod > 480:
        req_errs.append(f"Sausage sodium {sod}mg → exceeds 480mg")

    # — N) Other processed meats —
    if any(x in cls for x in ("deli","luncheon","salami","ham")) and sod > 480:
        req_errs.append(f"Deli meat sodium {sod}mg → exceeds 480mg")
    if "bacon" in cls+fam+desc+ing and sod > 290:
        req_errs.append(f"Bacon sodium {sod}mg → exceeds 290mg")

    # — O) Frozen whole meals ≤280mg sodium —
    if "meal" in cls+fam+desc+ing and sod > 280:
        req_errs.append(f"Meal sodium {sod}mg → exceeds 280mg")

    # — P) Soups & gravies ≤480mg sodium —
    if any(w in ("soup","gravy") for w in cls+fam+desc+ing) and sod > 480:
        req_errs.append(f"Soup/gravy sodium {sod}mg → exceeds 480mg")

    # — Q) Nuts/seeds & butters —
    if any(w in ("nut","seed") for w in cls+fam+desc+ing):
        if sod > 230:
            req_errs.append(f"Nut/seed sodium {sod}mg → exceeds 230mg")
        if "butter" in cls+fam+desc+ing and sugar > 4:
            req_errs.append(f"Nut butter sugar {sugar}g → exceeds 4g")

    # — R) Condiments & sauces —
    if "dressing" in cls+fam+desc+ing and sod > 290:
        req_errs.append(f"Dressing sodium {sod}mg → exceeds 290mg")
    elif any(w in ("sauce","condiment") for w in cls+fam+desc+ing):
        if "soy sauce" not in ing and sod > 480:
            req_errs.append(f"Sauce/condiment sodium {sod}mg → exceeds 480mg")

    # — S) Desserts ≤200 kcal & ≤18g sugar —
    if any(w in ("cookie","cake","brownie","ice cream","dessert")
           for w in cls+fam+desc+ing):
        if cal > 200:
            req_errs.append(f"Dessert calories {cal}kcal → exceeds 200kcal")
        if sugar > 18:
            req_errs.append(f"Dessert sugar {sugar}g → exceeds 18g")

    # — T) Snacks —
    if "snack" in cls+fam+desc+ing:
        if cal > 250:
            req_errs.append(f"Snack calories {cal}kcal → exceeds 250kcal")
        if fatg > 7 and not any(x in ("nut","seed") for x in cls):
            req_errs.append(f"Snack fat {fatg}g → exceeds 7g")
        if satg > 1:
            req_errs.append(f"Snack sat-fat {satg}g → exceeds 1g")
        if sod > 230:
            req_errs.append(f"Snack sodium {sod}mg → exceeds 230mg")
        if sugar > 18 and not any(x in ("fruit","vegetable") for x in cls):
            req_errs.append(f"Snack sugar {sugar}g → exceeds 18g")
        if any(w in desc for w in ("gum","candy")) or ("chip" in desc and "baked" not in desc):
            req_errs.append("Gum/candy/non-baked chips are not allowed")

    req_ok   = not req_errs
    req_expl = "• " + "\n• ".join(req_errs) if req_errs else "Meets all Purchased Food Standards"

    # ——————————————————————————————————————————————
    # 2) Recommended checks
    rec_errs = []
    if not (sod <= 140 or LOW_SODIUM_RX.search(ing) or LOW_SODIUM_RX.search(desc)):
        rec_errs.append(f"Sodium {sod}mg → recommended ≤140mg or 'low/reduced sodium'")
    if bev and not fam.startswith("juice") and fam!="milk" and SWEETENED_BEV_RX.search(ing+desc):
        rec_errs.append("Recommend eliminating sugar-sweetened beverages")
    if grain and not WHOLE_GRAIN_RX.search(ing+desc):
        rec_errs.append("Recommended: whole-grain rich grain/starch")
    if any(w in ("cereal",) for w in cls+fam+desc+ing):
        rec_errs.append("Recommended: reduce cereal sugar to ≤6g per dry ounce")
    if veg:
        rec_errs.append("Recommended: purchase fresh or frozen vegetables")
    if fruit:
        rec_errs.append("Recommended: purchase fresh raw or frozen fruit")
    if "cheese" in cls+fam+desc+ing:
        rec_errs.append("Recommended: unprocessed low-fat cheese (e.g. part-skim)")

    rec_ok   = not rec_errs
    rec_expl = "• " + "\n• ".join(rec_errs) if rec_errs else "Meets all Recommended Standards"

    return req_ok, req_expl, rec_ok, rec_expl


def main():
    # ——————————————————————————————————————————————
    # 1) open two connections
    #    a) update_conn for ALTER + UPDATEs
    #    b) fetch_conn  for streaming SELECT only
    # ——————————————————————————————————————————————
    update_conn = psycopg2.connect(dbname="nutrigence_db")
    fetch_conn  = psycopg2.connect(dbname="nutrigence_db")

    # a) add our four new columns, commit once
    with update_conn:
        with update_conn.cursor() as cur:
            cur.execute("""
              ALTER TABLE product_nutrition
                ADD COLUMN IF NOT EXISTS purchased_ok            boolean,
                ADD COLUMN IF NOT EXISTS purchased_explanation   text,
                ADD COLUMN IF NOT EXISTS recommended_ok          boolean,
                ADD COLUMN IF NOT EXISTS recommended_explanation text;
            """)

    # b) open server‐side cursor on fetch_conn
    fetch_cur = fetch_conn.cursor("fetch_products", cursor_factory=DictCursor)
    fetch_cur.itersize = 1000
    fetch_cur.execute("""
      SELECT
        pn.gtin,
        p.ingredients,
        p.description,
        p.family_title  AS family,
        p.class_title   AS cls,
        p.super_segment,
        p.segment,
        p.sub_segment,
        p.raw_data
      FROM product_nutrition pn
      JOIN products           p USING (gtin)
    """)

    upd_cur = update_conn.cursor()
    batch = 0

    for row in tqdm(fetch_cur, desc="PurchasedFood"):
        # build nutrients dict
        nutrients = {}
        raw = row["raw_data"]
        if isinstance(raw, list):
            raw = raw[0] if raw else {}
        for block in (raw or {}).get("nutrientInformation", []):
            for e in block.get("nutrientDetail", []):
                code = e.get("nutrientTypeCode","")
                qtys = e.get("quantityContained",[])
                try:
                    val = float(qtys[0].get("value",0)) if qtys else 0
                except:
                    val = 0
                nutrients[code] = (val, e.get("measurementPrecisionCode",""))

        req_ok, req_expl, rec_ok, rec_expl = classify_purchased(
            nutrients,
            row["ingredients"],
            row["description"],
            row["family"],
            row["cls"],
            row["super_segment"],
            row["segment"],
            row["sub_segment"],
        )

        upd_cur.execute("""
          UPDATE product_nutrition
             SET purchased_ok            = %s,
                 purchased_explanation    = %s,
                 recommended_ok          = %s,
                 recommended_explanation = %s
           WHERE gtin = %s
        """, (req_ok, req_expl, rec_ok, rec_expl, row["gtin"]))

        batch += 1
        if batch % 1000 == 0:
            update_conn.commit()

    # final commit & cleanup
    update_conn.commit()
    upd_cur.close()
    fetch_cur.close()
    update_conn.close()
    fetch_conn.close()


if __name__ == "__main__":
    main()
