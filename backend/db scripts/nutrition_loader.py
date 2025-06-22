def extract_nutrition(item):
    gtin = item.get("gtin")
    rows = []

    nutrient_info = next((n for n in item.get("nutrientInformation", [])), None)
    if not nutrient_info:
        return rows

    code_map = {
        "ENER-": "calories",
        "FATNLEA": "total_fat",
        "FASAT": "saturated_fat",
        "FATRN": "trans_fat",
        "CHOL-": "cholesterol",
        "NA": "sodium",
        "CHO-": "total_carbohydrate",
        "FIBTSW": "dietary_fiber",
        "SUGAR-": "sugars",
        "SUGAD": "added_sugars",
        "PRO-": "protein",
        "VITD-": "vitamin_d",
        "CA": "calcium",
        "FE": "iron",
        "K": "potassium"
    }

    for detail in nutrient_info.get("nutrientDetail", []):
        code = detail.get("nutrientTypeCode")
        label = code_map.get(code)
        if label and "quantityContained" in detail:
            val = detail["quantityContained"][0]
            value = val.get("value")
            unit = val.get("qual")
            if value:
                rows.append({
                    "gtin": gtin,
                    "nutrient_code": code,
                    "nutrient_label": label,
                    "value": float(value),
                    "unit": unit
                })

    return rows


def insert_nutrition(cur, nutrition_rows):
    for n in nutrition_rows:
        cur.execute("""
            INSERT INTO product_nutrition (
                gtin, nutrient_code, nutrient_label, value, unit
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            n["gtin"],
            n["nutrient_code"],
            n["nutrient_label"],
            n["value"],
            n["unit"]
        ))
