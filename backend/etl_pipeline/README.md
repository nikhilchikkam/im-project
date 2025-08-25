# ETL Pipeline Documentation

This ETL pipeline extracts product data from OneWorldSync (OWS), transforms it, and loads it into a PostgreSQL database. The pipeline is divided into two main sections: **Manual Incremental Load** and **Data Processing**.

## Overview

```
OWS API → DigitalOcean Spaces → PostgreSQL → Data Processing Scripts
```

## Section 1: Manual Incremental Load (Initial Load)

### Purpose
Extracts product data from OneWorldSync API, processes it in batches, and loads it into PostgreSQL via DigitalOcean Spaces.

### Key Components

#### 1.1 Main ETL Script
**File**: `initial_load/run_incremental_etl.py`
**Purpose**: End-to-end ETL pipeline from OWS to database

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/initial_load
python run_incremental_etl.py
```

**What it does**:
- Extracts data from OWS API with GPC code filtering
- Processes data in batches (1,000 products per batch)
- Uploads batch files to DigitalOcean Spaces
- Loads data into PostgreSQL using staging tables
- Handles upserts for existing products
- Processes: products, serving, diet_claims, images, nutrition, allergens
- Uses incremental mode to only process recent data

#### 1.2 ETL Orchestrator
**File**: `initial_load/etl_orchestrator.py`
**Purpose**: Core ETL orchestration with parallel processing

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/initial_load
python etl_orchestrator.py
```

**What it does**:
- Manages parallel batch processing with worker pools
- Handles checkpointing for resumable operations
- Coordinates data extraction, transformation, and loading
- Provides detailed logging and progress tracking

#### 1.3 Individual Loaders
**Directory**: `initial_load/loaders/`

- **`batch_loader.py`**: Core batch processing logic with staging tables
- **`base_loader.py`**: Base loader class with common functionality
- **`product_loader.py`**: Product-specific loading operations
- **`serving_loader.py`**: Serving information loading
- **`diet_claim_loader.py`**: Diet claims loading
- **`image_url_loader.py`**: Product image URL loading
- **`simple_loader.py`**: Simple loading operations


### Configuration
**File**: `initial_load/config.py`
**Purpose**: Centralized ETL configuration

**Key Settings**:
- `ETL_MAX_WORKERS`: Number of parallel workers
- `OWS_BATCH_SIZE`: Batch size for OWS API calls
- `LOOKBACK_DAYS`: Days to look back for incremental updates
- `SPACES_BUCKET`: DigitalOcean Spaces bucket name

### Environment Variables Required
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SPACES_KEY=your_spaces_key
SPACES_SECRET=your_spaces_secret
SPACES_BUCKET=your_bucket_name
OWS_API_KEY=your_ows_api_key
```

### Performance Notes
- Processes ~1,000 products per batch
- Uses multiprocessing for parallel loading
- Implements retry logic for network issues
- Uses staging tables for efficient bulk operations
- Supports incremental processing for faster updates
- **Nutrition standardization**: Now handled during ETL process in staging tables (no separate post-processing step)

---

## Section 2: Data Processing

### Purpose
Processes and evaluates loaded product data against various nutrition standards and classifications.

### Key Components

#### 2.1 Main Processing Orchestrator
**File**: `data_processing/run_all_processing.py`
**Purpose**: Runs all data processing scripts sequentially

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/data_processing
python run_all_processing.py
```

**Scripts executed in order**:
1. `add_unit_name.py` - Adds unit names to nutrition data
2. `update_availability_flags.py` - Updates product availability flags
3. `update_class_title.py` - Updates product classification titles
4. `name_normalizer.py` - Normalizes product names
5. `maintain_product_classification.py` - Ensures all products have classification records
6. `good_choice_evaluator.py` - Evaluates against "Good Choice" standards
7. `smart_snack_evaluator.py` - Evaluates against USDA Smart Snacks standards
8. `philadelphia_purchased_food_evaluator.py` - Evaluates against Philadelphia standards

#### 2.2 Individual Processing Scripts

##### **Data Standardization Scripts**
- **`add_unit_name.py`**: Adds human-readable unit names to nutrition data
- **`update_availability_flags.py`**: Updates product availability status
- **`update_class_title.py`**: Updates product classification titles
- **`name_normalizer.py`**: Normalizes product names for consistency

##### **Classification Maintenance**
- **`maintain_product_classification.py`**: Ensures all products with nutrition data have classification records

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/data_processing
python maintain_product_classification.py
```

**What it does**:
- Finds products with nutrition data missing from `product_classification`
- Creates missing records with default values
- Sets processing flags to `false` for new records

##### **Evaluation Scripts**

###### **Good Choice Evaluator**
**File**: `data_processing/good_choice_evaluator.py`
**Purpose**: Evaluates products against "Good Choice" nutrition standards

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/data_processing
python good_choice_evaluator.py
```

**What it does**:
- Evaluates products against calorie, sodium, fat, and sugar limits
- Updates `is_good_choice` column in `product_classification`
- Uses `good_choice_processed` flag for incremental processing
- Only processes unprocessed records (`good_choice_processed = false`)
- Uses SQL aggregation for optimized nutrient processing

###### **Smart Snack Evaluator**
**File**: `data_processing/smart_snack_evaluator.py`
**Purpose**: Evaluates products against USDA Smart Snacks in School standards

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/data_processing
python smart_snack_evaluator.py
```

**What it does**:
- Evaluates against USDA Smart Snacks standards
- Updates `is_smart_snack`, `snack_explanation`, `nova_group` columns
- Uses `smart_snack_processed` flag for incremental processing
- Only fetches required nutrients: `ENER-`, `NA`, `FATNLEA`, `FASAT`, `FATRN`, `SUGAR-`, `CHO-`
- Handles None values in raw data properly

###### **Philadelphia Purchased Food Evaluator**
**File**: `data_processing/philadelphia_purchased_food_evaluator.py`
**Purpose**: Evaluates products against Philadelphia School District standards

**Usage**:
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/data_processing
python philadelphia_purchased_food_evaluator.py
```

**What it does**:
- Evaluates against Philadelphia Purchased and Recommended standards
- Updates `purchased_ok`, `purchased_explanation`, `recommended_ok`, `recommended_explanation`
- Uses `philadelphia_processed` flag for incremental processing
- Only fetches required nutrients: `ENER-`, `NA`, `FATNLEA`, `FASAT`, `FATRN`, `SUGAR-`, `FIBTG`

#### 2.3 Additional Scripts
- **`run_processing.py`**: Alternative processing wrapper
- **`add_philadelphia_processed_column.sql`**: SQL script to add processing column
- **`remove_good_choice_from_products.sql`**: SQL script to clean up old columns

### Database Schema

#### Key Tables
- **`products`**: Main product data
- **`product_nutrition`**: Nutrition information
- **`product_classification`**: Evaluation results and processing flags

#### Processing Flags
- `good_choice_processed`: Tracks Good Choice evaluation status
- `smart_snack_processed`: Tracks Smart Snack evaluation status  
- `philadelphia_processed`: Tracks Philadelphia evaluation status

### Performance Optimizations

#### Query Optimizations
- **Incremental Processing**: Only processes unprocessed records
- **Nutrient Filtering**: Only fetches required nutrients per evaluator
- **Bulk Updates**: Uses `FROM (VALUES ...)` for efficient updates
- **Indexes**: Automatic index creation for better performance

#### Batch Processing
- **Good Choice**: Uses SQL aggregation for faster nutrient processing
- **Smart Snack**: Optimized nutrient fetching (7 nutrients vs all)
- **Philadelphia**: Optimized nutrient fetching (7 nutrients vs all)

### Error Handling
- **Timeouts**: 30s lock timeout, 10min statement timeout
- **Retries**: Exponential backoff for network issues
- **Transaction Management**: Proper commit/rollback handling
- **Progress Tracking**: tqdm progress bars for long operations

### Monitoring and Logging
- **Progress Bars**: Visual progress for long-running operations
- **Detailed Logging**: INFO level logging with timestamps
- **Statistics**: Counts of processed, successful, and failed records
- **Performance Metrics**: Processing time and record counts

---

## Quick Start Commands


### For Incremental Updates
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/initial_load

# 1. Run ETL for new products only (incremental mode)
python run_incremental_etl.py

# 2. Run data processing (only processes new/unprocessed records)
cd ../data_processing
python run_all_processing.py
```

### For Individual Processing
```bash
# Activate virtual environment first
cd backend/venv/Scripts
activate
cd ../../etl_pipeline/data_processing

# Run specific evaluator only
python good_choice_evaluator.py
python smart_snack_evaluator.py
python philadelphia_purchased_food_evaluator.py
```

---

## Troubleshooting

### Common Issues
1. **Database Connection**: Check `DATABASE_URL` environment variable
2. **API Limits**: OWS API has rate limits, scripts handle retries
3. **Memory Issues**: Scripts use streaming for large datasets
4. **Timeout Issues**: Increase timeout values in scripts if needed
5. **Missing SQL Files**: `standardize_nutrition.sql` is in `backend/db scripts/`

### Performance Tips
1. **Indexes**: Scripts create necessary indexes automatically
2. **Batch Size**: Adjust batch sizes in `config.py` if needed
3. **Parallel Processing**: ETL uses multiprocessing for faster loading
4. **Incremental Processing**: Subsequent runs are much faster due to processing flags

### Database Maintenance
```sql
-- Check processing status
SELECT 
    COUNT(*) as total_products,
    COUNT(*) FILTER (WHERE good_choice_processed = true) as good_choice_processed,
    COUNT(*) FILTER (WHERE smart_snack_processed = true) as smart_snack_processed,
    COUNT(*) FILTER (WHERE philadelphia_processed = true) as philadelphia_processed
FROM product_classification;

-- Reset processing flags if needed
UPDATE product_classification SET good_choice_processed = false;
UPDATE product_classification SET smart_snack_processed = false;
UPDATE product_classification SET philadelphia_processed = false;
```

### File Locations
- **ETL Scripts**: `backend/etl_pipeline/initial_load/`
- **Data Processing**: `backend/etl_pipeline/data_processing/`
- **SQL Scripts**: `backend/db scripts/` (for standardize_nutrition.sql)
- **Configuration**: `backend/etl_pipeline/initial_load/config.py`
