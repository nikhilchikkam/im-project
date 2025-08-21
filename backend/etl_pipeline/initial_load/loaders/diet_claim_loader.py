"""
Diet Claim Loader Module
"""

import json
from .simple_loader import SimpleLoader

class DietClaimLoader(SimpleLoader):
    """Loader for product_diet_claims table"""
    
    def __init__(self, database_url):
        super().__init__("Diet Claims", "product_diet_claims", database_url)
        
    def extract_data(self, item):
        gtin = item.get('gtin')
        if not gtin:
            return None
            
        # Diet types
        diet_types = []
        for diet in item.get('foodAndBevDietTypeInfo', []):
            code = diet.get('dietTypeCode')
            if code:
                diet_types.append(code)
                
        # Claims
        claims = {}
        for detail in item.get('productInformationDetail', []):
            for claim in detail.get('claimDetail', []):
                claim_type = claim.get('claimTypeCode')
                claim_elem = claim.get('claimElementCode')
                if claim_type and claim_elem:
                    claims.setdefault(claim_type, []).append(claim_elem)
                    
        return {
            "gtin": gtin,
            "diet_types": json.dumps(diet_types),
            "claims": json.dumps(claims)
        }
        
    def insert_data(self, cur, data_list):
        for data in data_list:
            cur.execute("""
                INSERT INTO product_diet_claims (gtin, diet_types, claims)
                VALUES (%s, %s, %s)
                ON CONFLICT (gtin) DO UPDATE SET
                    diet_types = EXCLUDED.diet_types,
                    claims = EXCLUDED.claims
            """, (data["gtin"], data["diet_types"], data["claims"])) 