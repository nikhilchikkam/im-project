#!/usr/bin/env python3
"""
Simple Loader Base Class for individual data loaders
Used by ProductLoader, ServingLoader, DietClaimLoader, ImageURLLoader
"""

class SimpleLoader:
    """Simple base class for individual loaders that don't need staging tables"""
    
    def __init__(self, name: str, table_name: str, database_url: str):
        self.name = name
        self.table_name = table_name
        self.database_url = database_url
    
    def extract_data(self, item):
        """Extract data from item - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement extract_data")
    
    def insert_data(self, cur, data_list):
        """Insert data into database - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement insert_data")
