#!/usr/bin/env python3
"""
Comprehensive Batch loader for all data types with staging tables
Implements the batch-parallel architecture for products, serving, diet claims, image URLs, nutrition, and allergens
"""

import os
import logging
import json
import pandas as pd
from typing import Iterator, Dict, Any, List
from psycopg2.extras import RealDictCursor, Json, execute_values
from datetime import datetime
from .base_loader import BaseLoader
import time

logger = logging.getLogger(__name__)

class BatchLoader(BaseLoader):
    """Comprehensive loader for all data types using staging tables"""
    
    def __init__(self, database_url: str):
        super().__init__(database_url)
        self.allergen_mapping = None
        self.allergen_mapping_dict = None
        self._load_allergen_mapping()
    
    def _load_allergen_mapping(self):
        """Load allergen mapping from Excel file or JSON file"""
        try:
            # First try to load JSON file from manual_etl directory
            json_paths = [
                "manual_etl/allergen_mapping.json",
                "../manual_etl/allergen_mapping.json",
                "../../manual_etl/allergen_mapping.json"
            ]
            
            for path in json_paths:
                try:
                    with open(path, 'r') as f:
                        allergen_data = json.load(f)
                    # Store JSON directly as dictionary for efficient lookup
                    self.allergen_mapping_dict = allergen_data
                    # Also keep DataFrame for backward compatibility
                    allergen_list = []
                    for code, description in allergen_data.items():
                        allergen_list.append({
                            'Code': code,
                            'Description': description
                        })
                    self.allergen_mapping = pd.DataFrame(allergen_list)
                    logger.info(f"Loaded allergen mapping from JSON: {path} ({len(allergen_data)} mappings)")
                    break
                except FileNotFoundError:
                    continue
                except Exception as e:
                    logger.warning(f"Error reading JSON file {path}: {e}")
                    continue
            
            # If JSON not found, try Excel files
            if self.allergen_mapping is None:
                mapping_paths = [
                    "allergen_mapping.xlsx",
                    "../allergen_mapping.xlsx", 
                    "../../allergen_mapping.xlsx",
                    "db scripts/allergen_mapping.xlsx"
                ]
                
                for path in mapping_paths:
                    try:
                        self.allergen_mapping = pd.read_excel(path)
                        logger.info(f"Loaded allergen mapping from Excel: {path}")
                        break
                    except FileNotFoundError:
                        continue
            
            # If not found locally, log warning
            if self.allergen_mapping is None:
                logger.warning("Could not load allergen mapping file from any local source")
            
            if self.allergen_mapping is None:
                logger.warning("Could not load allergen mapping file from any source")
                self.allergen_mapping = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading allergen mapping: {e}")
            self.allergen_mapping = pd.DataFrame()
    
    def _create_staging_tables(self):
        """Create staging tables for all data types"""
        
        # Create nutrition staging table - matches original loader exactly
        self.cursor.execute("""
            CREATE TEMP TABLE staging_nutrition (
                gtin VARCHAR(50),
                nutrient_code VARCHAR(20),
                nutrient_label VARCHAR(100),
                value DECIMAL(10,3),
                unit VARCHAR(20)
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Create allergen staging table - use lowercase column names
        self.cursor.execute("""
            CREATE TEMP TABLE staging_allergen (
                gtin VARCHAR(50),
                allergenspecificationagency VARCHAR(100),
                allergenspecificationname VARCHAR(100),
                allergentypecode VARCHAR(20),
                allergentypename VARCHAR(100),
                levelofcontainmentcode VARCHAR(20),
                allergenstatement TEXT,
                isallergenrelevantdataprovided BOOLEAN
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Create products staging table
        self.cursor.execute("""
            CREATE TEMP TABLE staging_products (
                gtin TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                ingredients TEXT,
                brand TEXT,
                product_type TEXT,
                is_consumer_unit BOOLEAN,
                gpc_code TEXT,
                last_updated TIMESTAMP WITHOUT TIME ZONE
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Create serving staging table
        self.cursor.execute("""
            CREATE TEMP TABLE staging_serving (
                gtin TEXT PRIMARY KEY,
                gpc_code TEXT,
                serving_size_value DOUBLE PRECISION,
                serving_size_unit TEXT,
                serving_description TEXT,
                basis_quantity_value DOUBLE PRECISION,
                basis_quantity_unit TEXT,
                basis_quantity_type TEXT
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Create diet claims staging table
        self.cursor.execute("""
            CREATE TEMP TABLE staging_diet_claims (
                gtin CHARACTER VARYING PRIMARY KEY,
                diet_types JSONB,
                claims JSONB
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Create image URLs staging table
        self.cursor.execute("""
            CREATE TEMP TABLE staging_image_urls (
                gtin TEXT PRIMARY KEY,
                primary_url TEXT,
                image_urls JSONB
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Create indexes on staging tables for better merge performance
        self.cursor.execute("CREATE INDEX ON staging_nutrition (gtin, nutrient_code)")
        self.cursor.execute("CREATE INDEX ON staging_allergen (gtin, allergentypecode)")
        self.cursor.execute("CREATE INDEX ON staging_products (gtin)")
        self.cursor.execute("CREATE INDEX ON staging_serving (gtin)")
        self.cursor.execute("CREATE INDEX ON staging_diet_claims (gtin)")
        self.cursor.execute("CREATE INDEX ON staging_image_urls (gtin)")
    
    def _truncate_staging_tables(self):
        """Truncate all staging tables"""
        self.cursor.execute("TRUNCATE TABLE staging_nutrition")
        self.cursor.execute("TRUNCATE TABLE staging_allergen")
        self.cursor.execute("TRUNCATE TABLE staging_products")
        self.cursor.execute("TRUNCATE TABLE staging_serving")
        self.cursor.execute("TRUNCATE TABLE staging_diet_claims")
        self.cursor.execute("TRUNCATE TABLE staging_image_urls")

    def _extract_product_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract product data from batch"""
        products = batch_data.get('products', [])
        
        for product in products:
            # Handle nested data structure from DO Spaces
            actual_product = product.get('item', product)
            gtin = actual_product.get('gtin')
            
            if not gtin:
                continue
            
            # Convert last_updated string to timestamp
            last_updated = None
            if actual_product.get("lastModifiedDate"):
                try:
                    date_str = actual_product["lastModifiedDate"]
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    last_updated = datetime.fromisoformat(date_str)
                except Exception as e:
                    logger.debug(f"Could not parse lastModifiedDate '{actual_product['lastModifiedDate']}': {e}")
                    last_updated = None
            
            yield {
                'gtin': gtin,
                'name': actual_product.get('functionalName', [{}])[0].get("value") if actual_product.get('functionalName') else None,
                'description': actual_product.get('productDescription', [{}])[0].get("value") if actual_product.get('productDescription') else None,
                'ingredients': actual_product.get('ingredientStatement', [{}])[0].get("statement", [{}])[0].get("value") if actual_product.get('ingredientStatement') else None,
                'brand': actual_product.get('brandName'),
                'product_type': actual_product.get('productType'),
                'is_consumer_unit': actual_product.get('isConsumerUnit') == "true",
                'gpc_code': actual_product.get('globalClassificationCategory', {}).get('code'),
                'last_updated': last_updated
            }

    def _extract_serving_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract serving data from batch"""
        products = batch_data.get('products', [])
        
        for product in products:
            actual_product = product.get('item', product)
            gtin = actual_product.get('gtin')
            gpc_code = actual_product.get('globalClassificationCategory', {}).get('code')
            
            if not gtin:
                continue
            
            # Extract serving information using the same logic as ServingLoader
            nutrient_info = next((n for n in actual_product.get("nutrientInformation", [])), None)
            
            if not nutrient_info:
                continue
                
            ss = nutrient_info.get("servingSize", [{}])[0]
            desc = nutrient_info.get("servingSizeDescription", [{}])[0]
            basis = nutrient_info.get("nutrientBasisQuantity", {})
            
            yield {
                'gtin': gtin,
                'gpc_code': gpc_code,
                'serving_size_value': float(ss.get("value", 0)) if ss.get("value") else None,
                'serving_size_unit': ss.get("qual"),
                'serving_description': desc.get("value"),
                'basis_quantity_value': float(basis.get("value", 0)) if basis.get("value") else None,
                'basis_quantity_unit': basis.get("qual"),
                'basis_quantity_type': nutrient_info.get("nutrientBasisQuantityTypeCode")
            }

    def _extract_diet_claim_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract diet claim data from batch"""
        products = batch_data.get('products', [])
        
        for product in products:
            actual_product = product.get('item', product)
            gtin = actual_product.get('gtin')
            
            if not gtin:
                continue
            
            # Diet types - using the same logic as DietClaimLoader
            diet_types = []
            for diet in actual_product.get('foodAndBevDietTypeInfo', []):
                code = diet.get('dietTypeCode')
                if code:
                    diet_types.append(code)
                    
            # Claims - using the same logic as DietClaimLoader
            claims = {}
            for detail in actual_product.get('productInformationDetail', []):
                for claim in detail.get('claimDetail', []):
                    claim_type = claim.get('claimTypeCode')
                    claim_elem = claim.get('claimElementCode')
                    if claim_type and claim_elem:
                        claims.setdefault(claim_type, []).append(claim_elem)
            
            if diet_types or claims:
                yield {
                    'gtin': gtin,
                    'diet_types': diet_types,
                    'claims': claims
                }

    def _extract_image_url_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract image URL data from batch"""
        products = batch_data.get('products', [])
        
        for product in products:
            actual_product = product.get('item', product)
            gtin = actual_product.get('gtin')
            
            if not gtin:
                continue
            
            # Extract image URLs using the same logic as ImageURLLoader
            external_urls = []
            dam_urls = []
            
            for link in actual_product.get("externalFileLink", []):
                url = link.get("uniformResourceIdentifier")
                if url:
                    external_urls.append(url)
                    
            for dam_entry in actual_product.get("dam", []):
                general = dam_entry.get("general", {})
                url = general.get("uniformResourceIdentifier")
                if url:
                    dam_urls.append(url)
                    
            primary_url = external_urls[0] if external_urls else (dam_urls[0] if dam_urls else None)
            image_urls = {
                "externalFileLink": external_urls,
                "dam": dam_urls
            }
            
            if external_urls or dam_urls:
                yield {
                    'gtin': gtin,
                    'primary_url': primary_url,
                    'image_urls': image_urls
                }

    def _extract_nutrition_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract nutrition data from batch using original logic"""
        products = batch_data.get('products', [])
        
        code_map = {
            "ENER-": "calories",
            "FATNLEA": "total_fat",
            "FASAT": "saturated_fat",
            "FATRN": "trans_fat",
            "CHOL-": "cholesterol",
            "NA": "sodium",
            "CHO-": "total_carbohydrate",
            "FIBTSW": "dietary_fiber",
            "SUGAR-": "sugars",
            "SUGAD": "added_sugars",
            "PRO-": "protein",
            "VITD-": "vitamin_d",
            "CA": "calcium",
            "FE": "iron",
            "K": "potassium"
        }
        
        for product in products:
            # Get the item object (like original loaders)
            item = product.get('item', {})
            gtin = item.get('gtin')  # Use item.gtin, not product.gln
            
            if not gtin:
                continue
            
            # Extract nutrition information using original logic
            nutrient_info = next((n for n in item.get("nutrientInformation", [])), None)
            if not nutrient_info:
                continue
            
            for detail in nutrient_info.get("nutrientDetail", []):
                code = detail.get("nutrientTypeCode")
                label = code_map.get(code)
                if label and "quantityContained" in detail:
                    val = detail["quantityContained"][0]
                    value = val.get("value")
                    unit = val.get("qual")
                    if value:
                        yield {
                            'gtin': gtin,
                            'nutrient_code': code,
                            'nutrient_label': label,
                            'value': float(value),
                            'unit': unit
                        }
    
    def _extract_allergen_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract allergen data from batch using original logic"""
        products = batch_data.get('products', [])
        
        for product in products:
            # Get the item object (like original loaders)
            item = product.get('item', {})
            gtin = item.get('gtin')  # Use item.gtin, not product.gln
            
            if not gtin:
                continue
            
            # Extract allergen information using original logic
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
                        type_name = self._map_allergen_name(code) if code else None
                        yield {
                            'gtin': gtin,
                            'allergenSpecificationAgency': agency,
                            'allergenSpecificationName': name,
                            'allergenTypeCode': code,
                            'allergenTypeName': type_name,
                            'levelOfContainmentCode': a.get("levelOfContainmentCode"),
                            'allergenStatement': statement,
                            'isAllergenRelevantDataProvided': is_relevant
                        }
                else:
                    # No allergen array, still record the info
                    yield {
                        'gtin': gtin,
                        'allergenSpecificationAgency': agency,
                        'allergenSpecificationName': name,
                        'allergenTypeCode': None,
                        'allergenTypeName': None,
                        'levelOfContainmentCode': None,
                        'allergenStatement': statement,
                        'isAllergenRelevantDataProvided': is_relevant
                    }
    
    def _map_allergen_name(self, allergen_code: str) -> str:
        """Map allergen code using the mapping table"""
        # First try JSON dictionary (more efficient)
        if self.allergen_mapping_dict and allergen_code in self.allergen_mapping_dict:
            return self.allergen_mapping_dict[allergen_code]
        
        # Fallback to DataFrame (for backward compatibility)
        if self.allergen_mapping is not None and not self.allergen_mapping.empty:
            # Look for exact match by code
            match = self.allergen_mapping[
                self.allergen_mapping['Code'] == allergen_code
            ]
            
            if not match.empty:
                return match.iloc[0]['Description']
        
        return None

    def _copy_products_to_staging(self, product_data: Iterator[Dict[str, Any]]) -> int:
        """Copy product data to staging table"""
        count = 0
        
        # Convert iterator to list and deduplicate
        product_dict = {}  # Use dict to deduplicate by gtin
        for row in product_data:
            product_dict[row['gtin']] = row  # Keep the last occurrence if duplicates exist
        
        rows = list(product_dict.values())
        count = len(rows)
        
        if rows:
            insert_sql = """
                INSERT INTO staging_products (
                    gtin, name, description, ingredients, brand,
                    product_type, is_consumer_unit, gpc_code, last_updated
                ) VALUES %s
            """
            values = [
                (row['gtin'], row['name'], row['description'], row['ingredients'],
                 row['brand'], row['product_type'], row['is_consumer_unit'],
                 row['gpc_code'], row['last_updated'])
                for row in rows
            ]
            execute_values(self.cursor, insert_sql, values)
        
        return count

    def _copy_serving_to_staging(self, serving_data: Iterator[Dict[str, Any]]) -> int:
        """Copy serving data to staging table"""
        count = 0
        
        # Convert iterator to list and deduplicate
        serving_dict = {}  # Use dict to deduplicate by gtin
        for row in serving_data:
            serving_dict[row['gtin']] = row  # Keep the last occurrence if duplicates exist
        
        rows = list(serving_dict.values())
        count = len(rows)
        
        if rows:
            insert_sql = """
                INSERT INTO staging_serving (
                    gtin, gpc_code, serving_size_value, serving_size_unit,
                    serving_description, basis_quantity_value, basis_quantity_unit,
                    basis_quantity_type
                ) VALUES %s
            """
            values = [
                (row['gtin'], row['gpc_code'], row['serving_size_value'],
                 row['serving_size_unit'], row['serving_description'],
                 row['basis_quantity_value'], row['basis_quantity_unit'],
                 row['basis_quantity_type'])
                for row in rows
            ]
            execute_values(self.cursor, insert_sql, values)
        
        return count

    def _copy_diet_claims_to_staging(self, diet_claim_data: Iterator[Dict[str, Any]]) -> int:
        """Copy diet claim data to staging table"""
        count = 0
        
        # Convert iterator to list and deduplicate
        diet_claim_dict = {}  # Use dict to deduplicate by gtin
        for row in diet_claim_data:
            diet_claim_dict[row['gtin']] = row  # Keep the last occurrence if duplicates exist
        
        rows = list(diet_claim_dict.values())
        count = len(rows)
        
        if rows:
            insert_sql = """
                INSERT INTO staging_diet_claims (gtin, diet_types, claims)
                VALUES %s
            """
            values = [
                (row['gtin'], Json(row['diet_types']) if row['diet_types'] is not None else None,
                 Json(row['claims']) if row['claims'] is not None else None)
                for row in rows
            ]
            execute_values(self.cursor, insert_sql, values)
        
        return count

    def _copy_image_urls_to_staging(self, image_url_data: Iterator[Dict[str, Any]]) -> int:
        """Copy image URL data to staging table"""
        count = 0
        
        # Convert iterator to list and deduplicate
        image_url_dict = {}  # Use dict to deduplicate by gtin
        for row in image_url_data:
            image_url_dict[row['gtin']] = row  # Keep the last occurrence if duplicates exist
        
        rows = list(image_url_dict.values())
        count = len(rows)
        
        if rows:
            insert_sql = """
                INSERT INTO staging_image_urls (gtin, primary_url, image_urls)
                VALUES %s
            """
            values = [
                (row['gtin'], row['primary_url'], Json(row['image_urls']))
                for row in rows
            ]
            execute_values(self.cursor, insert_sql, values)
        
        return count
    
    def _copy_nutrition_to_staging(self, nutrition_data: Iterator[Dict[str, Any]]) -> int:
        """INSERT nutrition data to staging table using batch INSERT statements with deduplication"""
        count = 0
        
        # Convert iterator to list and deduplicate
        nutrition_dict = {}  # Use dict to deduplicate by (gtin, nutrient_code)
        for row in nutrition_data:
            key = (row['gtin'], row['nutrient_code'])
            nutrition_dict[key] = row  # Keep the last occurrence if duplicates exist
        
        rows = list(nutrition_dict.values())
        count = len(rows)
        
        if rows:
            insert_sql = """
                INSERT INTO staging_nutrition (
                    gtin, nutrient_code, nutrient_label, value, unit
                ) VALUES %s
            """
            values = [
                (row['gtin'], row['nutrient_code'], row['nutrient_label'], row['value'], row['unit'])
                for row in rows
            ]
            execute_values(self.cursor, insert_sql, values)
        
        return count
    
    def _copy_allergen_to_staging(self, allergen_data: Iterator[Dict[str, Any]]) -> int:
        """INSERT allergen data to staging table using batch INSERT statements with deduplication"""
        count = 0
        
        # Convert iterator to list and deduplicate
        allergen_dict = {}  # Use dict to deduplicate by (gtin, allergenspecificationagency, allergenspecificationname, allergentypecode)
        for row in allergen_data:
            key = (row['gtin'], row['allergenSpecificationAgency'], row['allergenSpecificationName'], row['allergenTypeCode'])
            allergen_dict[key] = row  # Keep the last occurrence if duplicates exist
        
        rows = list(allergen_dict.values())
        count = len(rows)
        
        if rows:
            insert_sql = """
                INSERT INTO staging_allergen (
                    gtin, allergenspecificationagency, allergenspecificationname, 
                    allergentypecode, allergentypename, levelofcontainmentcode, 
                    allergenstatement, isallergenrelevantdataprovided
                ) VALUES %s
            """
            values = [
                (row['gtin'], row['allergenSpecificationAgency'], row['allergenSpecificationName'],
                 row['allergenTypeCode'], row['allergenTypeName'], row['levelOfContainmentCode'],
                 (str(row['allergenStatement']) if isinstance(row['allergenStatement'], dict) else row['allergenStatement']),
                 True if str(row['isAllergenRelevantDataProvided']).lower() == 'true' else False if str(row['isAllergenRelevantDataProvided']).lower() == 'false' else None)
                for row in rows
            ]
            execute_values(self.cursor, insert_sql, values)
        
        return count

    def _merge_products_from_staging(self) -> int:
        """Merge products from staging to final table"""
        self.cursor.execute("""
            INSERT INTO products (gtin, name, description, ingredients, brand, product_type, is_consumer_unit, gpc_code, last_updated)
            SELECT gtin, name, description, ingredients, brand, product_type, is_consumer_unit, gpc_code, last_updated
            FROM staging_products
            ON CONFLICT (gtin) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                ingredients = EXCLUDED.ingredients,
                brand = EXCLUDED.brand,
                product_type = EXCLUDED.product_type,
                is_consumer_unit = EXCLUDED.is_consumer_unit,
                gpc_code = EXCLUDED.gpc_code,
                last_updated = EXCLUDED.last_updated
        """)
        return self.cursor.rowcount

    def _merge_serving_from_staging(self) -> int:
        """Merge serving from staging to final table"""
        self.cursor.execute("""
            INSERT INTO serving (gtin, gpc_code, serving_size_value, serving_size_unit, serving_description, basis_quantity_value, basis_quantity_unit, basis_quantity_type)
            SELECT gtin, gpc_code, serving_size_value, serving_size_unit, serving_description, basis_quantity_value, basis_quantity_unit, basis_quantity_type
            FROM staging_serving
            ON CONFLICT (gtin) DO UPDATE SET
                gpc_code = EXCLUDED.gpc_code,
                serving_size_value = EXCLUDED.serving_size_value,
                serving_size_unit = EXCLUDED.serving_size_unit,
                serving_description = EXCLUDED.serving_description,
                basis_quantity_value = EXCLUDED.basis_quantity_value,
                basis_quantity_unit = EXCLUDED.basis_quantity_unit,
                basis_quantity_type = EXCLUDED.basis_quantity_type
        """)
        return self.cursor.rowcount

    def _merge_diet_claims_from_staging(self) -> int:
        """Merge diet claims from staging to final table"""
        self.cursor.execute("""
            INSERT INTO product_diet_claims (gtin, diet_types, claims)
            SELECT gtin, diet_types, claims
            FROM staging_diet_claims
            ON CONFLICT (gtin) DO UPDATE SET
                diet_types = EXCLUDED.diet_types,
                claims = EXCLUDED.claims
        """)
        return self.cursor.rowcount

    def _merge_image_urls_from_staging(self) -> int:
        """Merge image URLs from staging to final table"""
        self.cursor.execute("""
            INSERT INTO product_images (gtin, primary_url, image_urls)
            SELECT gtin, primary_url, image_urls
            FROM staging_image_urls
            ON CONFLICT (gtin) DO UPDATE SET
                primary_url = EXCLUDED.primary_url,
                image_urls = EXCLUDED.image_urls
        """)
        return self.cursor.rowcount
    
    def _merge_nutrition_from_staging(self) -> int:
        """Merge nutrition data from staging to live table - matches original exactly"""
        self.cursor.execute("""
            INSERT INTO product_nutrition (gtin, nutrient_code, nutrient_label, value, unit)
            SELECT gtin, nutrient_code, nutrient_label, value, unit
            FROM staging_nutrition
            ON CONFLICT (gtin, nutrient_code) DO UPDATE SET
                nutrient_label = EXCLUDED.nutrient_label,
                value = EXCLUDED.value,
                unit = EXCLUDED.unit
        """)
        
        return self.cursor.rowcount
    
    def _merge_allergen_from_staging(self) -> int:
        """Merge allergen data from staging to live table - matches original exactly"""
        self.cursor.execute("""
            INSERT INTO product_allergen (gtin, allergenSpecificationAgency, allergenSpecificationName, allergenTypeCode, allergenTypeName, levelOfContainmentCode, allergenStatement, isAllergenRelevantDataProvided)
            SELECT gtin, allergenspecificationagency, allergenspecificationname, allergentypecode, allergentypename, levelofcontainmentcode, allergenstatement, isallergenrelevantdataprovided
            FROM staging_allergen
            ON CONFLICT (gtin, allergenSpecificationAgency, allergenSpecificationName, allergenTypeCode) 
            DO UPDATE SET
                allergenTypeName = EXCLUDED.allergenTypeName,
                levelOfContainmentCode = EXCLUDED.levelOfContainmentCode,
                allergenStatement = EXCLUDED.allergenStatement,
                isAllergenRelevantDataProvided = EXCLUDED.isAllergenRelevantDataProvided
        """)
        
        return self.cursor.rowcount

    def process_batch(self, batch_data: Dict[str, Any]) -> Dict[str, int]:
        """Process a single batch with all data types through staging tables"""
        start_time = time.time()
        
        try:
            # Begin transaction
            self.connection.autocommit = False
            
            # Set per-batch session parameters
            self.cursor.execute("SET LOCAL synchronous_commit = OFF")
            
            # Clear staging tables
            self.truncate_staging()
            
            products = batch_data.get('products', [])
            logger.info(f"Processing {len(products)} products with all data types through staging")
            
            # Extract all data types
            parse_start = time.time()
            product_data = self._extract_product_data(batch_data)
            serving_data = self._extract_serving_data(batch_data)
            diet_claim_data = self._extract_diet_claim_data(batch_data)
            image_url_data = self._extract_image_url_data(batch_data)
            nutrition_data = self._extract_nutrition_data(batch_data)
            allergen_data = self._extract_allergen_data(batch_data)
            parse_time = time.time() - parse_start
            
            # Copy all data to staging tables
            copy_start = time.time()
            product_count = self._copy_products_to_staging(product_data)
            serving_count = self._copy_serving_to_staging(serving_data)
            diet_claim_count = self._copy_diet_claims_to_staging(diet_claim_data)
            image_url_count = self._copy_image_urls_to_staging(image_url_data)
            nutrition_count = self._copy_nutrition_to_staging(nutrition_data)
            allergen_count = self._copy_allergen_to_staging(allergen_data)
            copy_time = time.time() - copy_start
            
            # Merge all data from staging to final tables
            merge_start = time.time()
            products_merged = self._merge_products_from_staging()
            serving_merged = self._merge_serving_from_staging()
            diet_claims_merged = self._merge_diet_claims_from_staging()
            image_urls_merged = self._merge_image_urls_from_staging()
            nutrition_merged = self._merge_nutrition_from_staging()
            allergen_merged = self._merge_allergen_from_staging()
            merge_time = time.time() - merge_start
            
            # Commit transaction
            self.connection.commit()
            
            total_time = time.time() - start_time
            
            # Log comprehensive performance metrics
            logger.info(f"Comprehensive batch processed in {total_time:.2f}s - "
                       f"Parse: {parse_time:.2f}s, Copy: {copy_time:.2f}s, Merge: {merge_time:.2f}s - "
                       f"Products: {product_count} copied, {products_merged} merged, "
                       f"Serving: {serving_count} copied, {serving_merged} merged, "
                       f"Diet Claims: {diet_claim_count} copied, {diet_claims_merged} merged, "
                       f"Image URLs: {image_url_count} copied, {image_urls_merged} merged, "
                       f"Nutrition: {nutrition_count} copied, {nutrition_merged} merged, "
                       f"Allergen: {allergen_count} copied, {allergen_merged} merged")
            
            return {
                'products_copied': product_count,
                'serving_copied': serving_count,
                'diet_claims_copied': diet_claim_count,
                'image_urls_copied': image_url_count,
                'nutrition_copied': nutrition_count,
                'allergen_copied': allergen_count,
                'products_merged': products_merged,
                'serving_merged': serving_merged,
                'diet_claims_merged': diet_claims_merged,
                'image_urls_merged': image_urls_merged,
                'nutrition_merged': nutrition_merged,
                'allergen_merged': allergen_merged,
                'total_time': total_time
            }
            
        except Exception as e:
            logger.error(f"Error processing comprehensive batch: {e}")
            self.connection.rollback()
            raise
