#!/usr/bin/env python3
"""
Batch loader for nutrition and allergen data with staging tables
Implements the new batch-parallel architecture
"""

import logging
import json
import pandas as pd
from typing import Iterator, Dict, Any, List
from psycopg2.extras import RealDictCursor
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class BatchLoader(BaseLoader):
    """Loader for nutrition and allergen data using staging tables"""
    
    def __init__(self, database_url: str):
        super().__init__(database_url)
        self.allergen_mapping = None
        self._load_allergen_mapping()
    
    def _load_allergen_mapping(self):
        """Load allergen mapping from Excel file"""
        try:
            # Try multiple possible paths
            mapping_paths = [
                "allergen_mapping.xlsx",
                "../allergen_mapping.xlsx", 
                "../../allergen_mapping.xlsx",
                "db scripts/allergen_mapping.xlsx"
            ]
            
            for path in mapping_paths:
                try:
                    self.allergen_mapping = pd.read_excel(path)
                    logger.info(f"Loaded allergen mapping from: {path}")
                    break
                except FileNotFoundError:
                    continue
            
            if self.allergen_mapping is None:
                logger.warning("Could not load allergen mapping file")
                self.allergen_mapping = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading allergen mapping: {e}")
            self.allergen_mapping = pd.DataFrame()
    
    def _create_staging_tables(self):
        """Create staging tables for nutrition and allergen data"""
        
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
        
        # Create indexes on staging tables for better merge performance
        self.cursor.execute("CREATE INDEX ON staging_nutrition (gtin, nutrient_code)")
        self.cursor.execute("CREATE INDEX ON staging_allergen (gtin, allergentypecode)")
    
    def _truncate_staging_tables(self):
        """Truncate staging tables"""
        self.cursor.execute("TRUNCATE TABLE staging_nutrition")
        self.cursor.execute("TRUNCATE TABLE staging_allergen")
    
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
        if self.allergen_mapping.empty:
            return None
        
        # Look for exact match by code
        match = self.allergen_mapping[
            self.allergen_mapping['Code'] == allergen_code
        ]
        
        if not match.empty:
            return match.iloc[0]['Description']
        
        return None
    
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
            # Use executemany for batch insert
            insert_sql = """
                INSERT INTO staging_nutrition (
                    gtin, nutrient_code, nutrient_label, value, unit
                ) VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.executemany(insert_sql, [
                (row['gtin'], row['nutrient_code'], row['nutrient_label'], row['value'], row['unit'])
                for row in rows
            ])
        
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
            # Use executemany for batch insert
            insert_sql = """
                INSERT INTO staging_allergen (
                    gtin, allergenspecificationagency, allergenspecificationname, 
                    allergentypecode, allergentypename, levelofcontainmentcode, 
                    allergenstatement, isallergenrelevantdataprovided
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.executemany(insert_sql, [
                (row['gtin'], row['allergenSpecificationAgency'], row['allergenSpecificationName'],
                 row['allergenTypeCode'], row['allergenTypeName'], row['levelOfContainmentCode'],
                 row['allergenStatement'], row['isAllergenRelevantDataProvided'])
                for row in rows
            ])
        
        return count
    
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
