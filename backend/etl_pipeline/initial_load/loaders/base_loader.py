#!/usr/bin/env python3
"""
Base loader for batch-parallel ETL architecture
Supports staging tables, COPY operations, and single-transaction processing
"""

import logging
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor
import time

logger = logging.getLogger(__name__)

class BaseLoader(ABC):
    """Abstract base class for all loaders with staging table support"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.cursor = None
        self.staging_tables_created = False
        
    def connect(self):
        """Create database connection and set session parameters"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor()
            
            # Set session parameters outside any transaction
            self.connection.autocommit = True
            self._set_session_parameters()
            self.connection.autocommit = False
            
            logger.debug("Database connection established with optimized session parameters")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.debug("Database connection closed")
    
    def prepare_staging(self):
        """Create staging tables for this session"""
        if self.staging_tables_created:
            return
            
        try:
            # Ensure we're in autocommit mode for creating staging tables
            self.connection.autocommit = True
            self._create_staging_tables()
            self.connection.autocommit = False
            self.staging_tables_created = True
            logger.debug("Staging tables created")
        except Exception as e:
            logger.error(f"Failed to create staging tables: {e}")
            raise
    
    def truncate_staging(self):
        """Clear staging tables before processing a new batch"""
        try:
            self._truncate_staging_tables()
            logger.debug("Staging tables truncated")
        except Exception as e:
            logger.error(f"Failed to truncate staging tables: {e}")
            raise
    
    def process_batch(self, batch_data: Dict[str, Any]) -> Dict[str, int]:
        """Process a single batch with staging tables and single transaction"""
        start_time = time.time()
        
        try:
            # Begin transaction
            self.connection.autocommit = False
            
            # Set per-batch session parameters (inside transaction)
            self.cursor.execute("SET LOCAL synchronous_commit = OFF")
            
            # Clear staging tables
            self.truncate_staging()
            
            # Parse and extract data
            parse_start = time.time()
            nutrition_data = self._extract_nutrition_data(batch_data)
            allergen_data = self._extract_allergen_data(batch_data)
            parse_time = time.time() - parse_start
            
            # COPY nutrition data to staging
            nutrition_copy_start = time.time()
            nutrition_count = self._copy_nutrition_to_staging(nutrition_data)
            nutrition_copy_time = time.time() - nutrition_copy_start
            
            # COPY allergen data to staging
            allergen_copy_start = time.time()
            allergen_count = self._copy_allergen_to_staging(allergen_data)
            allergen_copy_time = time.time() - allergen_copy_start
            
            # Merge nutrition from staging to live table
            nutrition_merge_start = time.time()
            nutrition_merged = self._merge_nutrition_from_staging()
            nutrition_merge_time = time.time() - nutrition_merge_start
            
            # Merge allergen from staging to live table
            allergen_merge_start = time.time()
            allergen_merged = self._merge_allergen_from_staging()
            allergen_merge_time = time.time() - allergen_merge_start
            
            # Commit transaction
            self.connection.commit()
            
            total_time = time.time() - start_time
            
            # Log performance metrics
            logger.info(f"Batch processed in {total_time:.2f}s - "
                       f"Parse: {parse_time:.2f}s, "
                       f"Nutrition COPY: {nutrition_copy_time:.2f}s ({nutrition_count} rows), "
                       f"Allergen COPY: {allergen_copy_time:.2f}s ({allergen_count} rows), "
                       f"Nutrition merge: {nutrition_merge_time:.2f}s ({nutrition_merged} rows), "
                       f"Allergen merge: {allergen_merge_time:.2f}s ({allergen_merged} rows)")
            
            return {
                'nutrition_copied': nutrition_count,
                'allergen_copied': allergen_count,
                'nutrition_merged': nutrition_merged,
                'allergen_merged': allergen_merged,
                'total_time': total_time
            }
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            self.connection.rollback()
            raise
    
    def _set_session_parameters(self):
        """Set PostgreSQL session parameters for bulk loading"""
        self.cursor.execute("SET synchronous_commit = OFF")
        self.cursor.execute("SET work_mem = '256MB'")
        self.cursor.execute("SET temp_buffers = '256MB'")
        self.cursor.execute("SET maintenance_work_mem = '256MB'")
    
    @abstractmethod
    def _create_staging_tables(self):
        """Create staging tables for this loader"""
        pass
    
    @abstractmethod
    def _truncate_staging_tables(self):
        """Truncate staging tables"""
        pass
    
    @abstractmethod
    def _extract_nutrition_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract nutrition data from batch"""
        pass
    
    @abstractmethod
    def _extract_allergen_data(self, batch_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Extract allergen data from batch"""
        pass
    
    @abstractmethod
    def _copy_nutrition_to_staging(self, nutrition_data: Iterator[Dict[str, Any]]) -> int:
        """COPY nutrition data to staging table"""
        pass
    
    @abstractmethod
    def _copy_allergen_to_staging(self, allergen_data: Iterator[Dict[str, Any]]) -> int:
        """COPY allergen data to staging table"""
        pass
    
    @abstractmethod
    def _merge_nutrition_from_staging(self) -> int:
        """Merge nutrition data from staging to live table"""
        pass
    
    @abstractmethod
    def _merge_allergen_from_staging(self) -> int:
        """Merge allergen data from staging to live table"""
        pass

# Create an alias for backward compatibility
ETLLoader = BaseLoader 