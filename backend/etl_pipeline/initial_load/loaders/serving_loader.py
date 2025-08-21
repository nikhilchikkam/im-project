"""
Serving Loader Module
"""

from .simple_loader import SimpleLoader

class ServingLoader(SimpleLoader):
    """Loader for serving table"""
    
    def __init__(self, database_url):
        super().__init__("Serving", "serving", database_url)
        
    def extract_data(self, item):
        gtin = item.get("gtin")
        gpc_code = item.get("globalClassificationCategory", {}).get("code")
        nutrient_info = next((n for n in item.get("nutrientInformation", [])), None)
        
        if not nutrient_info:
            return None
            
        ss = nutrient_info.get("servingSize", [{}])[0]
        desc = nutrient_info.get("servingSizeDescription", [{}])[0]
        basis = nutrient_info.get("nutrientBasisQuantity", {})
        
        return {
            "gtin": gtin,
            "gpc_code": gpc_code,
            "serving_size_value": float(ss.get("value", 0)) if ss.get("value") else None,
            "serving_size_unit": ss.get("qual"),
            "serving_description": desc.get("value"),
            "basis_quantity_value": float(basis.get("value", 0)) if basis.get("value") else None,
            "basis_quantity_unit": basis.get("qual"),
            "basis_quantity_type": nutrient_info.get("nutrientBasisQuantityTypeCode")
        }
        
    def insert_data(self, cur, data_list):
        for data in data_list:
            if data:
                cur.execute("""
                    INSERT INTO serving (
                        gtin, gpc_code, serving_size_value, serving_size_unit,
                        serving_description, basis_quantity_value, basis_quantity_unit,
                        basis_quantity_type
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (gtin) DO UPDATE SET
                        gpc_code = EXCLUDED.gpc_code,
                        serving_size_value = EXCLUDED.serving_size_value,
                        serving_size_unit = EXCLUDED.serving_size_unit,
                        serving_description = EXCLUDED.serving_description,
                        basis_quantity_value = EXCLUDED.basis_quantity_value,
                        basis_quantity_unit = EXCLUDED.basis_quantity_unit,
                        basis_quantity_type = EXCLUDED.basis_quantity_type
                """, (
                    data["gtin"], data["gpc_code"], data["serving_size_value"],
                    data["serving_size_unit"], data["serving_description"],
                    data["basis_quantity_value"], data["basis_quantity_unit"],
                    data["basis_quantity_type"]
                )) 