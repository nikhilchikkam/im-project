"""
Image URL Loader Module
"""

import json
from .simple_loader import SimpleLoader

class ImageURLLoader(SimpleLoader):
    """Loader for product_images table"""
    
    def __init__(self, database_url):
        super().__init__("Image URLs", "product_images", database_url)
        
    def extract_data(self, item):
        gtin = item.get("gtin")
        if not gtin:
            return None
            
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
            "image_urls": json.dumps(image_urls)
        }
        
    def insert_data(self, cur, data_list):
        for data in data_list:
            cur.execute("""
                INSERT INTO product_images (gtin, primary_url, image_urls)
                VALUES (%s, %s, %s)
                ON CONFLICT (gtin) DO UPDATE SET 
                    primary_url = EXCLUDED.primary_url, 
                    image_urls = EXCLUDED.image_urls
            """, (data["gtin"], data["primary_url"], data["image_urls"])) 