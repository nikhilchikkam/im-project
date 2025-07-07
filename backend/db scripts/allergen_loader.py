import json
import pandas as pd
import os

# Load allergen mapping from Excel
mapping_path = os.path.join(os.path.dirname(__file__), "allergen_mapping.xlsx")
df = pd.read_excel(mapping_path)
ALLERGEN_TYPE_MAP = dict(zip(df["Code"], df["Description"]))

def extract_allergens(item):
    gtin = item.get("gtin")
    rows = []
    for info in item.get("allergenRelatedInformation", []):
        agency = info.get("allergenSpecificationAgency")
        name = info.get("allergenSpecificationName")
        is_relevant = info.get("isAllergenRelevantDataProvided")
        statement = None
        if info.get("allergenStatement"):
            # Use first value if present
            statement = info["allergenStatement"][0].get("value")
        allergens = info.get("allergen")
        if allergens:
            for a in allergens:
                code = a.get("allergenTypeCode")
                type_name = ALLERGEN_TYPE_MAP.get(code)
                rows.append({
                    "gtin": gtin,
                    "allergenSpecificationAgency": agency,
                    "allergenSpecificationName": name,
                    "allergenTypeCode": code,
                    "allergenTypeName": type_name,
                    "levelOfContainmentCode": a.get("levelOfContainmentCode"),
                    "allergenStatement": statement,
                    "isAllergenRelevantDataProvided": is_relevant
                })
        else:
            # No allergen array, still record the info
            rows.append({
                "gtin": gtin,
                "allergenSpecificationAgency": agency,
                "allergenSpecificationName": name,
                "allergenTypeCode": None,
                "allergenTypeName": None,
                "levelOfContainmentCode": None,
                "allergenStatement": statement,
                "isAllergenRelevantDataProvided": is_relevant
            })
    return rows

def insert_allergens(cur, allergen_rows):
    for row in allergen_rows:
        cur.execute("""
            INSERT INTO product_allergen (
                gtin, allergenSpecificationAgency, allergenSpecificationName,
                allergenTypeCode, allergenTypeName, levelOfContainmentCode, allergenStatement, isAllergenRelevantDataProvided
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            row["gtin"],
            row["allergenSpecificationAgency"],
            row["allergenSpecificationName"],
            row["allergenTypeCode"],
            row["allergenTypeName"],
            row["levelOfContainmentCode"],
            row["allergenStatement"],
            row["isAllergenRelevantDataProvided"]
        )) 