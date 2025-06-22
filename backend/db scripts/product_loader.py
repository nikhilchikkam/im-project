import json

def extract_product(item):
    return {
        "gtin": item.get("gtin"),
        "name": item.get("functionalName", [{}])[0].get("value"),
        "description": item.get("productDescription", [{}])[0].get("value"),
        "ingredients": item.get("ingredientStatement", [{}])[0].get("statement", [{}])[0].get("value"),
        "brand": item.get("brandName"),
        "product_type": item.get("productType"),
        "is_consumer_unit": item.get("isConsumerUnit") == "true",
        "gpc_code": item.get("globalClassificationCategory", {}).get("code"),
        "raw_data": json.dumps(item)
    }

def insert_product(cur, product):
    cur.execute("""
        INSERT INTO products (
            gtin, name, description, ingredients, brand,
            product_type, is_consumer_unit, gpc_code, raw_data
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (gtin) DO NOTHING
    """, (
        product["gtin"], product["name"], product["description"],
        product["ingredients"], product["brand"], product["product_type"],
        product["is_consumer_unit"], product["gpc_code"], product["raw_data"]
    ))
