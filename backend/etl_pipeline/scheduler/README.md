# ETL Scheduler for Incremental Updates

This scheduler handles incremental updates from OneWorldSync, following the same pattern as the initial load:
**OWS → DigitalOcean Spaces → Database**

## Features

- **Scheduled Updates**: Runs weekly at 2 AM by default
- **Manual Updates**: Trigger updates on-demand with custom lookback periods
- **Date Range Filtering**: Uses `lastModifiedDate` to fetch only updated products
- **Consistent Workflow**: Same OWS → Spaces → Database pattern as initial load
- **Error Handling**: Comprehensive error handling and logging
- **Status Monitoring**: Track scheduler status and last run times

## Workflow

The scheduler follows the same 3-step process as the initial load:

1. **Step 1**: Fetch incremental data from OneWorldSync API
2. **Step 2**: Save data to DigitalOcean Spaces (incremental batches)
3. **Step 3**: Load data from Spaces to Database

## Configuration

### Environment Variables

```bash
# Scheduler Configuration
SCHEDULE_INTERVAL_DAYS=7          # Weekly (default)
SCHEDULE_TIME=02:00               # 2 AM (default)
TIMEZONE=UTC                      # Timezone for scheduling

# Incremental Update Configuration
DEFAULT_LOOKBACK_DAYS=7           # Default days to look back
MAX_LOOKBACK_DAYS=30              # Maximum allowed lookback
SCHEDULER_BATCH_SIZE=1000         # Batch size for processing

# Inherits from initial_load:
# - OWS_BATCH_SIZE, OWS_MAX_RETRIES, OWS_RETRY_DELAY
# - SPACES_REGION, SPACES_BUCKET, SPACES_ACCESS_KEY, SPACES_SECRET_KEY
# - DATABASE_URL, API_DELAY
```

## Usage

### Start the Scheduler

```bash
# Start the scheduler (runs continuously)
python scheduler/scheduler.py

# Show scheduler status
python scheduler/scheduler.py --status

# Run manual update (default 7 days lookback)
python scheduler/scheduler.py --manual

# Run manual update with custom lookback
python scheduler/scheduler.py --manual --lookback 14
```

### Programmatic Usage

```python
from scheduler import IncrementalETLScheduler

# Create scheduler instance
scheduler = IncrementalETLScheduler()

# Start the scheduler
scheduler.start()

# Run manual update
result = scheduler.run_manual_update(lookback_days=7)

# Get status
status = scheduler.get_status()

# Stop the scheduler
scheduler.stop()
```

## Query Structure

The scheduler uses the following query structure for incremental updates:

```json
{
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
    ]
  },
  "lastModifiedDate": {
    "from": {
      "date": "2023-01-01",
      "op": "GTE"
    },
    "to": {
      "date": "2023-01-31",
      "op": "LTE"
    }
  },
  "pagination": {
    "limit": 1000,
    "offset": 0
  },
  "sort": [
    {
      "field": "lastModifiedDate",
      "direction": "desc"
    }
  ]
}
```

## DigitalOcean Spaces Structure

Incremental batches are stored in Spaces with the following structure:

```
nutrigence-etl/
├── incremental_batches/
│   └── batch_20231201_143022/
│       └── incremental_batch_20231201_143022_batch_0001_products.json
```

Each batch file contains:
```json
{
  "metadata": {
    "session_id": "20231201_143022",
    "batch_number": 1,
    "timestamp": "20231201_143022",
    "product_count": 1000,
    "type": "incremental"
  },
  "products": [...]
}
```

## Database Schema

The scheduler expects the following table for logging updates:

```sql
CREATE TABLE IF NOT EXISTS etl_update_log (
    id SERIAL PRIMARY KEY,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    products_processed INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_inserted INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    session_id VARCHAR(50) NOT NULL,
    batch_keys JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Logging

The scheduler logs to both file and console:

- **File**: `scheduler.log` (configurable via `SCHEDULER_LOG_FILE`)
- **Level**: Configurable via `SCHEDULER_LOG_LEVEL`
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Error Handling

- **API Failures**: Retries with exponential backoff
- **Database Errors**: Transaction rollback and error logging
- **Spaces Errors**: Proper error handling for upload/download failures
- **Configuration Errors**: Validation before startup
- **Graceful Shutdown**: Signal handling for clean shutdown

## Code Reuse

The scheduler reuses existing code from `initial_load`:

- **Configuration**: Extends `ETLConfig`
- **Utilities**: Uses `get_spaces_client()` and `filter_products_by_gpc()`
- **Patterns**: Follows same OWS → Spaces → Database workflow
- **Dependencies**: Minimal additional dependencies

## TODO

- [ ] Implement actual OneWorldSync API integration
- [ ] Add product update/insert logic using initial_load loaders
- [ ] Add monitoring and alerting
- [ ] Add web interface for manual triggers
- [ ] Add metrics collection
- [ ] Add backup and recovery procedures
