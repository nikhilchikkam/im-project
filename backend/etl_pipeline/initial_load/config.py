"""
Configuration module for ETL Pipeline
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from backend directory
load_dotenv('../../.env')  # backend/.env

class ETLConfig:
    """Configuration class for ETL pipeline settings"""
    
    # OneWorldSync Configuration
    OWS_BATCH_SIZE = int(os.getenv('OWS_BATCH_SIZE', '1000'))
    OWS_MAX_RETRIES = int(os.getenv('OWS_MAX_RETRIES', '3'))
    OWS_RETRY_DELAY = int(os.getenv('OWS_RETRY_DELAY', '5'))
    
    # DigitalOcean Spaces Configuration
    SPACES_REGION = os.getenv('SPACES_REGION', 'sfo3')
    SPACES_BUCKET = os.getenv('SPACES_BUCKET', 'nutrigence-etl')
    SPACES_ACCESS_KEY = os.getenv('SPACES_ACCESS_KEY')
    SPACES_SECRET_KEY = os.getenv('SPACES_SECRET_KEY')
    
    # ETL Configuration
    ETL_BATCH_SIZE = int(os.getenv('ETL_BATCH_SIZE', '1000'))
    ETL_MAX_WORKERS = int(os.getenv('ETL_MAX_WORKERS', '8'))  # Increased to 8
    
    # Date range configuration for incremental loads
    LOOKBACK_DAYS = int(os.getenv('LOOKBACK_DAYS', '3'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'etl_pipeline.log')
    
    # API Configuration
    API_DELAY = float(os.getenv('API_DELAY', '0.1'))  # Delay between API calls
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'SPACES_BUCKET',
            'SPACES_ACCESS_KEY', 
            'SPACES_SECRET_KEY'
        ]
        
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
        
        return True
    
    @classmethod
    def get_spaces_endpoint(cls):
        """Get DigitalOcean Spaces endpoint URL"""
        return f"https://{cls.SPACES_REGION}.digitaloceanspaces.com"
    
    @classmethod
    def get_date_range(cls):
        """Get date range for incremental processing"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=cls.LOOKBACK_DAYS)
        return start_date, end_date
    
    @classmethod
    def build_incremental_criteria(cls):
        """Build criteria for incremental update with date filtering - using proven working format"""
        start_date, end_date = cls.get_date_range()
        return {
            "pullHierarchy": False,
            "targetMarket": "US",
            "lastModifiedDate": {
                "from": {
                    "date": start_date.strftime("%Y-%m-%d"),
                    "op": "GTE"
                },
                "to": {
                    "date": end_date.strftime("%Y-%m-%d"),
                    "op": "LTE"
                }
            },
            "sortFields": [
                {
                    "field": "lastModifiedDate",
                    "desc": "true"
                },
                {
                    "field": "gtin",
                    "desc": "false"
                }
            ],
            "fields": {
                "include": [
                    "gtin",
                    "functionalName",
                    "productDescription",
                    "ingredientStatement",
                    "brandName",
                    "productType",
                    "isConsumerUnit",
                    "globalClassificationCategory",
                    "lastModifiedDate",
                    "nutrientInformation",
                    "allergenRelatedInformation",
                    "foodAndBevDietTypeInfo",
                    "productInformationDetail",
                    "externalFileLink",
                    "dam"
                ],
                "exclude": []
            }
        }
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("ETL Pipeline Configuration:")
        print(f"  Spaces Region: {cls.SPACES_REGION}")
        print(f"  Spaces Bucket: {cls.SPACES_BUCKET}")
        print(f"  OWS Batch Size: {cls.OWS_BATCH_SIZE}")
        print(f"  ETL Batch Size: {cls.ETL_BATCH_SIZE}")
        print(f"  Max Workers: {cls.ETL_MAX_WORKERS}")
        print(f"  Lookback Days: {cls.LOOKBACK_DAYS}")
        print(f"  Max Retries: {cls.OWS_MAX_RETRIES}")
        print(f"  Retry Delay: {cls.OWS_RETRY_DELAY}s")
        print(f"  API Delay: {cls.API_DELAY}s")
        print(f"  Log Level: {cls.LOG_LEVEL}") 