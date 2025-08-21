#!/usr/bin/env python3
"""
Test script for fetching actual data from OneWorldSync API
Fetches 2 batches and stores them in DigitalOcean Spaces
"""

import os
import sys
import logging
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv('../../.env')
load_dotenv('../.env')
load_dotenv('.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_from_ows_api(criteria: dict, batch_size: int = 1000) -> list:
    """
    Fetch actual data from OneWorldSync API using the same client as fetch_products.py
    Returns a list of batches (each batch is a list of products)
    """
    logger.info("🌐 Fetching data from OneWorldSync API...")
    
    try:
        from oneworldsync import Content1Client, AuthenticationError, APIError
        
        # Create client instance (same as fetch_products.py)
        client = Content1Client()
        
        batches = []
        batch_count = 0
        max_batches = 2  # Only fetch 2 batches for testing
        search_after = None
        
        while batch_count < max_batches:
            logger.info(f"Fetching batch {batch_count + 1}...")
            
            # Update criteria with searchAfter if we have it
            current_criteria = criteria.copy()
            if search_after:
                current_criteria["searchAfter"] = search_after
            
            try:
                # Fetch products using the same method as fetch_products.py
                result = client.fetch_products(criteria=current_criteria, page_size=batch_size)
                products = result.get("items", [])
                
                if not products:
                    logger.info("No more products found, stopping...")
                    break
                
                logger.info(f"Received {len(products)} products in batch {batch_count + 1}")
                
                # Add batch to our list
                batches.append(products)
                batch_count += 1
                
                # Get searchAfter for next batch
                if "searchAfter" in result:
                    search_after = result["searchAfter"]
                else:
                    logger.info("No searchAfter token, stopping...")
                    break
                    
            except AuthenticationError as e:
                logger.error(f"Authentication error: {e}")
                raise
            except APIError as e:
                logger.error(f"API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Error fetching products: {e}")
                raise
        
        logger.info(f"✅ Successfully fetched {len(batches)} batches from OWS API")
        return batches
        
    except ImportError:
        logger.error("oneworldsync library not found. Please install it: pip install oneworldsync")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize OWS client: {e}")
        raise

def test_real_ows_fetch():
    """Test fetching real data from OWS API and storing in DigitalOcean Spaces"""
    logger.info("🧪 Testing Real OWS API Fetch and Storage...")
    
    try:
        # Import the IncrementalLoader
        from incremental_loader import IncrementalLoader
        
        # Create loader instance
        logger.info("Creating IncrementalLoader instance...")
        loader = IncrementalLoader()
        
        # Setup Spaces client
        logger.info("Setting up DigitalOcean Spaces client...")
        loader.setup_spaces_client()
        
        # Build criteria for last 7 days
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        logger.info(f"Fetching products modified between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")
        
        # Build incremental criteria
        criteria = loader.build_incremental_criteria(start_date, end_date)
        logger.info(f"Using criteria: {json.dumps(criteria, indent=2)}")
        
        # Fetch actual data from OWS API
        batches = fetch_from_ows_api(criteria, batch_size=1000)
        
        if not batches:
            logger.warning("No data fetched from OWS API")
            return {
                'status': 'no_data',
                'message': 'No products found in the specified date range'
            }
        
        # Generate session ID
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Session ID: {session_id}")
        
        # Save batches to DigitalOcean Spaces
        logger.info("Saving batches to DigitalOcean Spaces...")
        batch_keys = loader.save_batches_to_spaces(batches, session_id)
        
        logger.info(f"✅ Successfully saved {len(batch_keys)} batches to Spaces:")
        for i, batch_key in enumerate(batch_keys, 1):
            logger.info(f"  Batch {i}: {batch_key}")
        
        # Test retrieving batches from Spaces
        logger.info("Testing batch retrieval from Spaces...")
        retrieved_batches = []
        total_products = 0
        
        for i, batch_key in enumerate(batch_keys):
            logger.info(f"Retrieving batch {i+1} from Spaces...")
            batch_data = loader.get_batch_from_spaces(batch_key)
            
            # Verify the data
            products = batch_data.get('products', [])
            metadata = batch_data.get('metadata', {})
            
            logger.info(f"  Batch {i+1} metadata: {metadata}")
            logger.info(f"  Batch {i+1} products: {len(products)}")
            
            # Show sample product info
            if products:
                first_product = products[0]
                logger.info(f"  Sample product GTIN: {first_product.get('gtin')}")
                logger.info(f"  Sample product name: {first_product.get('functionalName')}")
                logger.info(f"  Sample product last modified: {first_product.get('lastModifiedDate')}")
            
            retrieved_batches.append(batch_data)
            total_products += len(products)
        
        # Summary
        logger.info(f"✅ Successfully retrieved {len(retrieved_batches)} batches with {total_products} total products")
        
        return {
            'status': 'success',
            'session_id': session_id,
            'batches_saved': len(batch_keys),
            'total_products': total_products,
            'batch_keys': batch_keys,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

def main():
    """Main test function"""
    logger.info("🧪 Starting Real OWS API Fetch Test...")
    
    result = test_real_ows_fetch()
    
    if result['status'] == 'success':
        logger.info("\n🎉 Test completed successfully!")
        logger.info(f"Session ID: {result['session_id']}")
        logger.info(f"Batches saved: {result['batches_saved']}")
        logger.info(f"Total products: {result['total_products']}")
        logger.info(f"Date range: {result['date_range']['start']} to {result['date_range']['end']}")
        logger.info("You can now check your DigitalOcean Spaces to see the saved batches!")
    elif result['status'] == 'no_data':
        logger.info(f"\n⚠️  {result['message']}")
        logger.info("Try adjusting the date range or check if there are any products in the specified period.")
    else:
        logger.error(f"❌ Test failed: {result.get('error')}")

if __name__ == "__main__":
    main()
