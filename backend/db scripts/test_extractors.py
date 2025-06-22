import json
from nutrition_loader import extract_nutrition
from product_loader import extract_product
from serving_loader import extract_serving

def test_extract_serving():
    with open("item.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    item = data[0].get("item", {})  # Use first record's item
    serving = extract_serving(item)
    print("\n=== Serving ===")
    for k, v in serving.items():
        print(f"{k}: {v}")
    assert serving["gtin"] is not None

def load_sample(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0].get("item", {})  # first record's item


def test_extract_product():
    item = load_sample("item.json")
    product = extract_product(item)
    print("=== Product ===")
    for k, v in product.items():
        print(f"{k}: {v}")
    assert product["gtin"] is not None
    assert "name" in product


def test_extract_nutrition():
    item = load_sample("item.json")
    nutrition_rows = extract_nutrition(item)
    print("\n=== Nutrition ===")
    for row in nutrition_rows:
        print(row)
    assert len(nutrition_rows) > 0
    assert "gtin" in nutrition_rows[0]
    assert "value" in nutrition_rows[0]


if __name__ == "__main__":
    # test_extract_product()
    # test_extract_nutrition()
    test_extract_serving()

