# ETL Pipeline Documentation
## Nutrigence Data Processing System

### 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Components](#components)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The ETL (Extract, Transform, Load) pipeline processes OneWorldSync product data and loads it into the Nutrigence PostgreSQL database. The system handles data extraction, filtering, transformation, and loading with parallel processing capabilities.

### 🎯 Key Features
- **Parallel Processing**: Multi-threaded data loading for performance
- **Data Filtering**: GPC code-based product filtering
- **Error Handling**: Comprehensive error recovery and logging
- **Progress Tracking**: Real-time progress monitoring
- **Batch Processing**: Efficient memory management
- **Checkpointing**: Resume capability for interrupted processes

---

## Architecture

### 🏗️ System Design

```
OneWorldSync API → DigitalOcean Spaces → ETL Pipeline → PostgreSQL
```

### 📊 Dependency Order
1. **Products** (loaded first - base table)
2. **Related Data** (loaded in parallel after products exist):
   - Allergens
   - Nutrition
   - Serving
   - Diet Claims
   - Image URLs

### 🔄 Processing Flow
1. **Data Preparation**: Download GPC mapping from Spaces
2. **Product Loading**: Load products with filtering
3. **Parallel Processing**: Load related data simultaneously
4. **Progress Tracking**: Monitor and log progress
5. **Error Recovery**: Handle failures gracefully

---

## Data Flow

### 📥 Data Sources
- **OneWorldSync API**: Product data source
- **DigitalOcean Spaces**: File storage for batch data
- **Excel Files**: GPC mapping and reference data

### 🔄 Processing Steps
1. **Extract**: Download batch files from Spaces
2. **Transform**: Filter and process product data
3. **Load**: Insert data into PostgreSQL tables
4. **Validate**: Verify data integrity
5. **Log**: Record processing statistics

---

## Components

### 🚀 Main Orchestrator

#### etl_orchestrator.py
```python
#!/usr/bin/env python3
"""
ETL Orchestrator for batch-parallel processing
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any
from multiprocessing import Pool, Queue, Manager
from queue import Empty
import psycopg2
from dotenv import load_dotenv

from loaders.batch_loader import BatchLoader

class ETLOrchestrator:
    def __init__(self):
        self.config = ETLConfig()
        self.logger = logging.getLogger(__name__)
        
    def run(self, session_id: str = None):
        """Main ETL execution"""
        try:
            # Initialize checkpoint manager
            checkpoint_manager = CheckpointManager()
            
            # Get available batches
            batches = self.get_available_batches(session_id)
            
            # Process batches
            for batch in batches:
                self.process_batch(batch, checkpoint_manager)
                
        except Exception as e:
            self.logger.error(f"ETL process failed: {str(e)}")
            raise
```

### 📦 Data Loaders

#### ProductLoader
```python
class ProductLoader:
    """Loads core product information"""
    
    def load_products(self, products_data: List[Dict]) -> int:
        """Load products into database"""
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        loaded_count = 0
        for product in products_data:
            try:
                cur.execute("""
                    INSERT INTO products (
                        gtin, name, description, ingredients, brand,
                        product_type, gpc_code, class_title, family_title,
                        is_smart_snack, nova_label, is_good_choice,
                        recommended_ok, image_urls, raw_data, last_updated
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (gtin) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        last_updated = NOW()
                """, (
                    product.get('gtin'),
                    product.get('name'),
                    product.get('description'),
                    product.get('ingredients'),
                    product.get('brand'),
                    product.get('product_type'),
                    product.get('gpc_code'),
                    product.get('class_title'),
                    product.get('family_title'),
                    product.get('is_smart_snack'),
                    product.get('nova_label'),
                    product.get('is_good_choice'),
                    product.get('recommended_ok'),
                    json.dumps(product.get('image_urls', [])),
                    json.dumps(product)
                ))
                loaded_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to load product {product.get('gtin')}: {str(e)}")
                
        conn.commit()
        cur.close()
        conn.close()
        
        return loaded_count
```

#### AllergenLoader
```python
class AllergenLoader:
    """Loads allergen information"""
    
    def load_allergens(self, products_data: List[Dict]) -> int:
        """Load allergen data into database"""
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        loaded_count = 0
        for product in products_data:
            allergens = self.extract_allergens(product)
            for allergen in allergens:
                try:
                    cur.execute("""
                        INSERT INTO product_allergen (gtin, allergen_name, allergen_code)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (gtin, allergen_name) DO NOTHING
                    """, (allergen['gtin'], allergen['name'], allergen['code']))
                    loaded_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to load allergen: {str(e)}")
                    
        conn.commit()
        cur.close()
        conn.close()
        
        return loaded_count
```

### ⚙️ Configuration Management

#### config.py
```python
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
    ETL_MAX_WORKERS = int(os.getenv('ETL_MAX_WORKERS', '4'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'etl_pipeline.log')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['SPACES_BUCKET', 'SPACES_ACCESS_KEY', 'SPACES_SECRET_KEY']
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
        return True
```

---

## Configuration

### 🔧 Environment Variables

#### Required Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# DigitalOcean Spaces
SPACES_ACCESS_KEY=your_spaces_key
SPACES_SECRET_KEY=your_spaces_secret
SPACES_REGION=sfo3
SPACES_BUCKET=nutrigence-etl

# ETL Settings
ETL_BATCH_SIZE=1000
ETL_MAX_WORKERS=4
OWS_BATCH_SIZE=1000
OWS_MAX_RETRIES=3
```

#### Optional Variables
```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE=etl_pipeline.log

# Performance
API_DELAY=0.1
RETRY_DELAY=5
```

### 📊 Processing Settings

#### Batch Processing
- **Batch Size**: 1000 products per batch (configurable)
- **Max Workers**: 4 parallel processes (configurable)
- **Memory Management**: Efficient memory usage with batch processing

#### Error Handling
- **Retry Logic**: Automatic retry for failed operations
- **Error Logging**: Comprehensive error tracking
- **Graceful Degradation**: Continue processing despite individual failures

---

## Usage

### 🚀 Running the ETL Pipeline

#### Basic Usage
```bash
# Process all available batches
python run_etl.py

# Process specific session
python run_etl.py --session-id session_20231201_143022

# Estimate processing time
python run_etl.py --estimate
```

#### Command Line Options
```bash
python run_etl.py [OPTIONS]

Options:
  --session-id TEXT    Process specific session
  --estimate          Estimate processing time only
  --workers INTEGER   Number of worker processes
  --batch-size INTEGER Batch size for processing
  --help              Show help message
```

### 📋 Setup Process

#### 1. Install Dependencies
```bash
cd backend/etl_pipeline
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@host:port/database"
export SPACES_ACCESS_KEY="your_spaces_key"
export SPACES_SECRET_KEY="your_spaces_secret"
```

#### 3. Upload Reference Data
```bash
# Upload Excel file to Spaces
python upload_excel_to_spaces.py
```

#### 4. Run ETL Process
```bash
# Start ETL processing
python run_etl.py
```

---

## Monitoring

### 📊 Progress Tracking

#### Console Output
```
2024-01-15 10:30:00 - INFO - Starting ETL process...
2024-01-15 10:30:01 - INFO - Loaded 1,247 valid GPC codes from Excel file
2024-01-15 10:30:02 - INFO - Processing batch 1/65: filtered_batches/batch_session_20240115_103000/batch_0001_products.json
2024-01-15 10:30:03 - INFO - Loading 150 products...
2024-01-15 10:30:04 - INFO - Processing related data for 150 products...
2024-01-15 10:30:05 - INFO - Allergens: Processed 450 records
2024-01-15 10:30:05 - INFO - Nutrition: Processed 1,200 records
2024-01-15 10:30:05 - INFO - Serving: Processed 150 records
2024-01-15 10:30:05 - INFO - Diet Claims: Processed 75 records
2024-01-15 10:30:05 - INFO - Image URLs: Processed 150 records
```

#### Log File
```python
# Log file configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_orchestrator.log'),
        logging.StreamHandler()
    ]
)
```

### 📈 Performance Metrics

#### Expected Performance
- **Products**: ~100-200 records/second
- **Related Data**: ~500-1000 records/second (parallel)
- **Total**: ~2-5 minutes per 1000 products

#### Monitoring Tools
```python
class PerformanceMonitor:
    """Monitor ETL performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.processed_records = 0
        
    def update_progress(self, records_processed: int):
        """Update progress metrics"""
        self.processed_records += records_processed
        elapsed_time = time.time() - self.start_time
        rate = self.processed_records / elapsed_time if elapsed_time > 0 else 0
        
        self.logger.info(f"Processed {self.processed_records} records at {rate:.2f} records/sec")
```

---

## Troubleshooting

### 🚨 Common Issues

#### 1. Database Connection Failed
```
ValueError: DATABASE_URL environment variable is required
```
**Solution**: Check your `.env` file and ensure `DATABASE_URL` is set correctly.

#### 2. Spaces Access Denied
```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```
**Solution**: Verify your Spaces credentials and permissions.

#### 3. Excel File Not Found
```
Failed to download Excel file from Spaces
```
**Solution**: Ensure `family_class_brick.xlsx` exists in `reference/` folder in your Spaces bucket.

#### 4. Table Does Not Exist
```
psycopg2.errors.UndefinedTable: relation "products" does not exist
```
**Solution**: Create the required database tables first.

### 🔧 Debug Mode

#### Enable Debug Logging
```python
# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, ...)
```

#### Debug Configuration
```python
# Debug mode settings
DEBUG_MODE = True
VERBOSE_LOGGING = True
```

### 📝 Error Recovery

#### Checkpoint Management
```python
class CheckpointManager:
    """Manages checkpointing to track processed batches"""
    
    def __init__(self):
        self.checkpoint_file = "etl_checkpoint.json"
        
    def save_checkpoint(self, batch_id: str, status: str):
        """Save processing checkpoint"""
        checkpoint = {
            'batch_id': batch_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)
            
    def load_checkpoint(self) -> Dict:
        """Load last checkpoint"""
        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
```

---

## 🎯 Key Takeaways

### 🏗️ Architecture Excellence
1. **Parallel Processing**: Multi-threaded data loading for performance
2. **Error Recovery**: Comprehensive error handling and recovery
3. **Progress Tracking**: Real-time monitoring and logging
4. **Scalable Design**: Efficient batch processing architecture

### 🔧 Technical Implementation
1. **Data Integrity**: Proper data validation and filtering
2. **Performance Optimization**: Strategic batch sizing and parallelization
3. **Resource Management**: Efficient memory and connection usage
4. **Monitoring**: Comprehensive logging and metrics

### 📈 Operational Features
1. **Resume Capability**: Checkpoint-based process recovery
2. **Error Handling**: Graceful failure handling with detailed logging
3. **Configuration Management**: Flexible environment-based configuration
4. **Performance Monitoring**: Real-time performance metrics and tracking

---

*This ETL pipeline documentation provides a comprehensive overview of the data processing system, including architecture, configuration, usage, and troubleshooting. For specific implementation details, refer to the individual ETL files and their inline documentation.*

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: Data Engineering Team
