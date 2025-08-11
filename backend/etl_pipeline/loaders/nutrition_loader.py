"""
Nutrition Loader Module
"""

from .base_loader import ETLLoader

class NutritionLoader(ETLLoader):
    """Loader for product_nutrition table"""
    
    def __init__(self, database_url):
        super().__init__("Nutrition", "product_nutrition", database_url)
        self.code_map = {
            "ENER-": "calories", "FATNLEA": "total_fat", "FASAT": "saturated_fat",
            "FATRN": "trans_fat", "CHOL-": "cholesterol", "NA": "sodium",
            "CHO-": "total_carbohydrate", "FIBTSW": "dietary_fiber",
            "SUGAR-": "sugars", "SUGAD": "added_sugars", "PRO-": "protein",
            "VITD-": "vitamin_d", "CA": "calcium", "FE": "iron", "K": "potassium"
        }
        
    def extract_data(self, item):
        gtin = item.get("gtin")
        rows = []
        
        nutrient_info = next((n for n in item.get("nutrientInformation", [])), None)
        if not nutrient_info:
            return rows
            
        for detail in nutrient_info.get("nutrientDetail", []):
            code = detail.get("nutrientTypeCode")
            label = self.code_map.get(code)
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
        
    def insert_data(self, cur, data_list):
        for row in data_list:
            cur.execute("""
                INSERT INTO product_nutrition (
                    gtin, nutrient_code, nutrient_label, value, unit
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (gtin, nutrient_code) DO UPDATE SET
                    nutrient_label = EXCLUDED.nutrient_label,
                    value = EXCLUDED.value,
                    unit = EXCLUDED.unit
            """, (
                row["gtin"], row["nutrient_code"], row["nutrient_label"],
                row["value"], row["unit"]
            )) 