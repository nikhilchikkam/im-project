"""
Product Loader Module
"""

import json
from .simple_loader import SimpleLoader

class ProductLoader(SimpleLoader):
    """Loader for products table"""
    
    def __init__(self, database_url):
        super().__init__("Products", "products", database_url)
        
    def extract_data(self, item):
        return {
            "gtin": item.get("gtin"),
            "name": item.get("functionalName", [{}])[0].get("value") if item.get("functionalName") else None,
            "description": item.get("productDescription", [{}])[0].get("value") if item.get("productDescription") else None,
            "ingredients": item.get("ingredientStatement", [{}])[0].get("statement", [{}])[0].get("value") if item.get("ingredientStatement") else None,
            "brand": item.get("brandName"),
            "product_type": item.get("productType"),
            "is_consumer_unit": item.get("isConsumerUnit") == "true",
            "gpc_code": item.get("globalClassificationCategory", {}).get("code"),
            "last_updated": item.get("lastModifiedDate")
        }
        
    def insert_data(self, cur, data_list):
        for product in data_list:
            cur.execute("""
                INSERT INTO products (
                    gtin, name, description, ingredients, brand,
                    product_type, is_consumer_unit, gpc_code, last_updated
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (gtin) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    ingredients = EXCLUDED.ingredients,
                    brand = EXCLUDED.brand,
                    product_type = EXCLUDED.product_type,
                    is_consumer_unit = EXCLUDED.is_consumer_unit,
                    gpc_code = EXCLUDED.gpc_code,
                    last_updated = EXCLUDED.last_updated
            """, (
                product["gtin"], product["name"], product["description"],
                product["ingredients"], product["brand"], product["product_type"],
                product["is_consumer_unit"], product["gpc_code"],
                product["last_updated"]
            )) 