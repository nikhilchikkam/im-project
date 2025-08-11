"""
Allergen Loader Module
"""

import pandas as pd
import os
import boto3
from .base_loader import ETLLoader

class AllergenLoader(ETLLoader):
    """Loader for product_allergen table"""
    
    def __init__(self, database_url):
        super().__init__("Allergens", "product_allergen", database_url)
        self.allergen_type_map = {}
        self.load_allergen_mapping()
        
    def load_allergen_mapping(self):
        """Load allergen mapping from Excel file in DigitalOcean Spaces reference folder"""
        try:
            excel_file_local = "allergen_mapping.xlsx"
            excel_file_spaces = "reference/allergen_mapping.xlsx"
            
            # Check if local file exists
            if os.path.exists(excel_file_local):
                print(f"Using local allergen mapping file: {excel_file_local}")
            else:
                # Download from DigitalOcean Spaces
                print(f"Downloading allergen mapping file from Spaces: {excel_file_spaces}")
                self.download_allergen_mapping_from_spaces(excel_file_spaces, excel_file_local)
            
            # Load the mapping
            if os.path.exists(excel_file_local):
                df = pd.read_excel(excel_file_local)
                self.allergen_type_map = dict(zip(df["Code"], df["Description"]))
                print(f"Loaded {len(self.allergen_type_map)} allergen mappings")
            else:
                print(f"Warning: Allergen mapping file not found: {excel_file_local}")
                self.allergen_type_map = {}
        except Exception as e:
            print(f"Error loading allergen mapping: {e}")
            self.allergen_type_map = {}
    
    def download_allergen_mapping_from_spaces(self, spaces_key, local_file):
        """Download allergen mapping Excel file from DigitalOcean Spaces"""
        try:
            # Get environment variables for Spaces
            import os
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv('../.env')
            load_dotenv('.env')
            
            spaces_access_key = os.getenv('SPACES_ACCESS_KEY')
            spaces_secret_key = os.getenv('SPACES_SECRET_KEY')
            spaces_region = os.getenv('SPACES_REGION', 'sfo3')
            spaces_bucket = os.getenv('SPACES_BUCKET', 'nutrigence-etl')
            
            if not spaces_access_key or not spaces_secret_key:
                print("Warning: Spaces credentials not found, skipping download")
                return False
            
            # Create Spaces client
            session = boto3.session.Session()
            spaces_client = session.client('s3',
                                        region_name=spaces_region,
                                        endpoint_url=f'https://{spaces_region}.digitaloceanspaces.com',
                                        aws_access_key_id=spaces_access_key,
                                        aws_secret_access_key=spaces_secret_key)
            
            # Download file
            response = spaces_client.get_object(Bucket=spaces_bucket, Key=spaces_key)
            with open(local_file, 'wb') as f:
                f.write(response['Body'].read())
            
            print(f"Downloaded allergen mapping file: {local_file}")
            return True
            
        except Exception as e:
            print(f"Error downloading allergen mapping from Spaces: {e}")
            return False
        
    def extract_data(self, item):
        gtin = item.get("gtin")
        rows = []
        
        for info in item.get("allergenRelatedInformation", []):
            agency = info.get("allergenSpecificationAgency")
            name = info.get("allergenSpecificationName")
            is_relevant = info.get("isAllergenRelevantDataProvided")
            statement = None
            
            if info.get("allergenStatement"):
                statement = info["allergenStatement"][0].get("value")
                
            allergens = info.get("allergen")
            if allergens:
                for a in allergens:
                    code = a.get("allergenTypeCode")
                    type_name = self.allergen_type_map.get(code)
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
                # No allergen array, still record the info (matching original logic)
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
        
    def insert_data(self, cur, data_list):
        for row in data_list:
            cur.execute("""
                INSERT INTO product_allergen (
                    gtin, allergenSpecificationAgency, allergenSpecificationName,
                    allergenTypeCode, allergenTypeName, levelOfContainmentCode, 
                    allergenStatement, isAllergenRelevantDataProvided
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (gtin, allergenSpecificationAgency, allergenSpecificationName, allergenTypeCode) 
                DO UPDATE SET
                    allergenTypeName = EXCLUDED.allergenTypeName,
                    levelOfContainmentCode = EXCLUDED.levelOfContainmentCode,
                    allergenStatement = EXCLUDED.allergenStatement,
                    isAllergenRelevantDataProvided = EXCLUDED.isAllergenRelevantDataProvided
            """, (
                row["gtin"], row["allergenSpecificationAgency"],
                row["allergenSpecificationName"], row["allergenTypeCode"],
                row["allergenTypeName"], row["levelOfContainmentCode"],
                row["allergenStatement"], row["isAllergenRelevantDataProvided"]
            )) 