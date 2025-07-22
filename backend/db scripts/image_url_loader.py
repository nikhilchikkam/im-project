
import os
import json
import time
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATA_FOLDER = r"E:\Projects\Mendon\results\products2"
RETRY_DELAY = 5
MAX_RETRIES = 5

def extract_image_urls(item):
    gtin = item.get("gtin")
    external_urls = []
    dam_urls = []
    for link in item.get("externalFileLink", []):
        url = link.get("uniformResourceIdentifier")
        if url:
            external_urls.append(url)
    for dam_entry in item.get("dam", []):
        general = dam_entry.get("general", {})
        url = general.get("uniformResourceIdentifier")
        if url:
            dam_urls.append(url)
    primary_url = external_urls[0] if external_urls else (dam_urls[0] if dam_urls else None)
    image_urls = {
        "externalFileLink": external_urls,
        "dam": dam_urls
    }
    return {
        "gtin": gtin,
        "primary_url": primary_url,
        "image_urls": image_urls
    }

def insert_image_urls_batch(image_data_list):
    for attempt in range(MAX_RETRIES):
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    for image_data in image_data_list:
                        gtin = image_data['gtin']
                        cur.execute("""
                            INSERT INTO product_images (gtin, primary_url, image_urls)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (gtin) DO UPDATE SET primary_url = EXCLUDED.primary_url, image_urls = EXCLUDED.image_urls
                        """, (gtin, image_data['primary_url'], json.dumps(image_data['image_urls'])))
                    conn.commit()
            return True
        except psycopg2.OperationalError as e:
            print(f"DB connection lost: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying batch in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise
        except Exception as e:
            print(f"Error during DB insert: {e}")
            raise
    return False

def main():
    files = sorted(f for f in os.listdir(DATA_FOLDER) if f.endswith('.json'))
    total_files = len(files)
    print(f"Found {total_files} JSON files in {DATA_FOLDER}.")

    for idx, file in enumerate(files, 1):
        file_path = os.path.join(DATA_FOLDER, file)
        print(f"[{idx}/{total_files}] Processing: {file}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
        except Exception as e:
            print(f"  Failed to load {file}: {e}")
            continue

        image_data_list = []
        for product in products:
            item = product.get('item', {})
            image_data = extract_image_urls(item)
            if image_data['gtin']:
                image_data_list.append(image_data)

        if image_data_list:
            insert_image_urls_batch(image_data_list)
            print(f"  Inserted/updated {len(image_data_list)} records.")

if __name__ == "__main__":
    main()

