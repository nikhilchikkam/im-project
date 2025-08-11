"""
OneWorldSync API Client Module
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from oneworldsync import Content1Client, AuthenticationError, APIError
from .config import ETLConfig

logger = logging.getLogger(__name__)

class OneWorldSyncClient:
    """Client for interacting with OneWorldSync API"""
    
    def __init__(self):
        """Initialize OneWorldSync client"""
        self.client = Content1Client()
        self.config = ETLConfig()
    
    def get_incremental_criteria(self, last_sync_date: Optional[datetime] = None) -> Dict:
        """Get API criteria for incremental or full sync"""
        criteria = {
            "targetMarket": "US",
            "pullHierarchy": False,
            "sortFields": [
                {"field": "lastModifiedDate", "desc": True},
                {"field": "gtin", "desc": False}
            ],
            "fields": {
                "include": [
                    # Basic Product Information
                    "gtin",
                    "functionalName",
                    "productDescription", 
                    "ingredientStatement",
                    "brandName",
                    "productType",
                    "isConsumerUnit",
                    "globalClassificationCategory",
                    "lastModifiedDate",
                    
                    # Nutrition Information
                    "nutrientInformation",
                    
                    # Allergen Information
                    "allergenRelatedInformation",
                    
                    # Diet and Claims Information
                    "foodAndBevDietTypeInfo",
                    "productInformationDetail",
                    
                    # Image Information
                    "externalFileLink",
                    "dam"
                ],
                "exclude": []
            }
        }
        
        # Add date filter for incremental updates
        if last_sync_date:
            criteria["lastModifiedDate"] = {
                "gte": last_sync_date.isoformat()
            }
            logger.info(f"Incremental sync from: {last_sync_date}")
        else:
            logger.info("Performing full sync")
        
        return criteria
    
    def fetch_with_retry(self, criteria: Dict, page_size: int) -> Dict:
        """Fetch data from OneWorldSync with retry logic"""
        for attempt in range(self.config.OWS_MAX_RETRIES):
            try:
                logger.debug(f"API call attempt {attempt + 1}")
                return self.client.fetch_products(criteria=criteria, page_size=page_size)
            except (AuthenticationError, APIError) as e:
                logger.error(f"API error on attempt {attempt + 1}: {e}")
                if attempt == self.config.OWS_MAX_RETRIES - 1:
                    raise
                time.sleep(self.config.OWS_RETRY_DELAY * (attempt + 1))
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.OWS_MAX_RETRIES - 1:
                    raise
                time.sleep(self.config.OWS_RETRY_DELAY)
    
    def get_total_count(self, criteria: Dict) -> Optional[int]:
        """Get total count of products matching criteria"""
        try:
            return self.client.count_products(criteria)
        except Exception as e:
            logger.warning(f"Could not get total count: {e}")
            return None
    
    def fetch_all_products(self, criteria: Dict, progress_callback=None) -> List[Dict]:
        """Fetch all products matching criteria"""
        all_products = []
        search_after = None
        batch_count = 0
        
        # Get total count for progress tracking
        total_count = self.get_total_count(criteria)
        logger.info(f"Total products to fetch: {total_count if total_count else 'unknown'}")
        
        while True:
            # Add searchAfter to criteria if we have it
            if search_after:
                criteria["searchAfter"] = search_after
            
            # Fetch batch
            try:
                result = self.fetch_with_retry(criteria, self.config.OWS_BATCH_SIZE)
                products = result.get("items", [])
                
                if not products:
                    logger.info("No more products to fetch")
                    break
                
                all_products.extend(products)
                batch_count += 1
                
                logger.info(f"Fetched batch {batch_count}: {len(products)} products (Total: {len(all_products)})")
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(len(all_products), total_count, batch_count)
                
                # Check if we have more data
                if "searchAfter" not in result:
                    logger.info("No more pages available")
                    break
                
                search_after = result["searchAfter"]
                
                # Small delay to be respectful to the API
                time.sleep(self.config.API_DELAY)
                
            except Exception as e:
                logger.error(f"Error fetching batch {batch_count + 1}: {e}")
                raise
        
        logger.info(f"Completed fetching: {len(all_products)} products in {batch_count} batches")
        return all_products
    
    def test_connection(self) -> bool:
        """Test connection to OneWorldSync API"""
        try:
            # Try to get a small sample of products
            criteria = {
                "targetMarket": "US",
                "pullHierarchy": False,
                "fields": {
                    "include": ["gtin"],
                    "exclude": []
                }
            }
            
            result = self.fetch_with_retry(criteria, 1)
            if result and "items" in result:
                logger.info("OneWorldSync API connection successful")
                return True
            else:
                logger.error("OneWorldSync API returned unexpected response")
                return False
                
        except Exception as e:
            logger.error(f"OneWorldSync API connection failed: {e}")
            return False 