import json

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


def extract_daily_value_intake_percent(item):
    gtin = item.get("gtin")
    rows = []
    nutrient_info = next((n for n in item.get("nutrientInformation", [])), None)
    if not nutrient_info:
        return rows
    for detail in nutrient_info.get("nutrientDetail", []):
        code = detail.get("nutrientTypeCode")
        daily_value = detail.get("dailyValueIntakePercent")
        if code and daily_value is not None:
            rows.append({
                "gtin": gtin,
                "nutrient_code": code,
                "daily_value_intake_percent": str(daily_value)
            })
    return rows


def insert_daily_value_intake_percent(cur, rows):
    for n in rows:
        cur.execute("""
            UPDATE product_nutrition
            SET daily_value_intake_percent = %s
            WHERE gtin = %s AND nutrient_code = %s
        """, (
            n["daily_value_intake_percent"],
            n["gtin"],
            n["nutrient_code"]
        ))
