"""
Base ETL Loader Class
"""

import psycopg2
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ETLLoader(ABC):
    """Base class for ETL loaders"""
    
    def __init__(self, name, table_name, database_url):
        self.name = name
        self.table_name = table_name
        self.database_url = database_url
        self.processed_count = 0
        self.error_count = 0
        
    @abstractmethod
    def extract_data(self, item):
        """Extract data from item - to be implemented by subclasses"""
        pass
        
    @abstractmethod
    def insert_data(self, cur, data_list):
        """Insert data into database - to be implemented by subclasses"""
        pass
        
    def process_batch(self, items):
        """Process a batch of items"""
        try:
            data_list = []
            for item in items:
                try:
                    data = self.extract_data(item)
                    if data:
                        if isinstance(data, list):
                            data_list.extend(data)
                        else:
                            data_list.append(data)
                except Exception as e:
                    logger.error(f"Error extracting data from item: {e}")
                    self.error_count += 1
                    
            if data_list:
                with psycopg2.connect(self.database_url) as conn:
                    with conn.cursor() as cur:
                        self.insert_data(cur, data_list)
                        conn.commit()
                        self.processed_count += len(data_list)
                        
            return len(data_list)
        except Exception as e:
            logger.error(f"Error processing batch for {self.name}: {e}")
            self.error_count += 1
            return 0
            
    def get_stats(self):
        """Get processing statistics"""
        return {
            'name': self.name,
            'table': self.table_name,
            'processed': self.processed_count,
            'errors': self.error_count
        } 