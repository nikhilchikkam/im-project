# ETL Orchestrator for OneWorldSync Data

This ETL pipeline orchestrates the loading of OneWorldSync data into your PostgreSQL database with proper dependency management and parallel processing.

## 🏗️ Architecture

### **Dependency Order (Maintains FK Integrity):**
1. **Products** (loaded first - base table)
2. **Related Data** (loaded in parallel after products exist):
   - Allergens
   - Nutrition
   - Serving
   - Diet Claims
   - Image URLs

### **Key Features:**
- ✅ **FK Integrity**: Products loaded first, then related data
- 🚀 **Parallel Processing**: Related data processed simultaneously
- 📊 **Progress Tracking**: Detailed logging and statistics
- 🔄 **Batch Processing**: Efficient memory usage
- 🛡️ **Error Handling**: Graceful failure handling with rollback
- 📝 **Comprehensive Logging**: Both file and console output

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend/etl_pipeline
pip install -r requirements.txt
```

### 2. Set Environment Variables
Ensure your `.env` file contains:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SPACES_ACCESS_KEY=your_spaces_key
SPACES_SECRET_KEY=your_spaces_secret
SPACES_REGION=sfo3
SPACES_BUCKET=nutrigence-etl
```

### 3. Run ETL Process
```bash
# Process all available batches
python run_etl.py

# Process specific session
python run_etl.py --session-id session_20231201_143022

# Estimate processing time
python run_etl.py --estimate
```

## 📋 Usage Examples

### **Process All Data:**
```bash
python run_etl.py
```

### **Process Specific Session:**
```bash
python run_etl.py --session-id session_20231201_143022
```

### **Estimate Processing Time:**
```bash
python run_etl.py --estimate
```

## 🔍 How It Works

### **Step 1: Data Preparation**
- Downloads GPC mapping Excel from DigitalOcean Spaces
- Loads valid GPC codes for filtering
- Lists available batch files

### **Step 2: Sequential Product Loading**
- Loads products table first (maintains FK integrity)
- Filters by valid GPC codes
- Uses `ON CONFLICT` for upserts

### **Step 3: Parallel Related Data Processing**
- Processes allergens, nutrition, serving, diet claims, and image URLs simultaneously
- Uses ThreadPoolExecutor for parallel execution
- Each loader maintains its own connection pool

### **Step 4: Progress Tracking**
- Real-time progress updates
- Detailed statistics for each loader
- Comprehensive error logging

## 📊 Output Structure

### **Console Output:**
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

### **Log File (`etl_orchestrator.log`):**
- Detailed execution log
- Error details and stack traces
- Performance metrics

## 🗄️ Database Tables

The orchestrator expects these tables to exist:

### **Core Tables:**
- `products` - Main product information
- `product_allergen` - Allergen data
- `product_nutrition` - Nutritional information
- `serving` - Serving size data
- `product_diet_claims` - Diet and claim information
- `product_images` - Image URLs

### **Required Columns:**
- All tables must have `gtin` as primary/foreign key
- Products table must have `last_updated` column

## ⚙️ Configuration

### **Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `SPACES_ACCESS_KEY` - DigitalOcean Spaces access key
- `SPACES_SECRET_KEY` - DigitalOcean Spaces secret key
- `SPACES_REGION` - Spaces region (default: sfo3)
- `SPACES_BUCKET` - Spaces bucket name (default: nutrigence-etl)

### **Processing Settings:**
- `MAX_WORKERS` - Parallel processing threads (default: 4)
- `BATCH_SIZE` - Batch size for processing (default: 1000)
- `RETRY_DELAY` - Retry delay in seconds (default: 5)
- `MAX_RETRIES` - Maximum retry attempts (default: 3)

## 🚨 Troubleshooting

### **Common Issues:**

#### **1. Database Connection Failed:**
```
ValueError: DATABASE_URL environment variable is required
```
**Solution:** Check your `.env` file and ensure `DATABASE_URL` is set correctly.

#### **2. Spaces Access Denied:**
```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```
**Solution:** Verify your Spaces credentials and permissions.

#### **3. Excel File Not Found:**
```
Failed to download Excel file from Spaces
```
**Solution:** Ensure `family_class_brick.xlsx` exists in `reference/` folder in your Spaces bucket.

#### **4. Table Does Not Exist:**
```
psycopg2.errors.UndefinedTable: relation "products" does not exist
```
**Solution:** Create the required database tables first.

### **Debug Mode:**
Enable detailed logging by modifying the logging level in `etl_orchestrator.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📈 Performance Tips

### **Optimization Strategies:**
1. **Increase MAX_WORKERS** for more parallel processing
2. **Adjust BATCH_SIZE** based on available memory
3. **Use connection pooling** for database connections
4. **Monitor database performance** during execution

### **Expected Performance:**
- **Products**: ~100-200 records/second
- **Related Data**: ~500-1000 records/second (parallel)
- **Total**: ~2-5 minutes per 1000 products

## 🔄 Integration with Existing Pipeline

### **Workflow:**
1. **Fetch Data**: Use `fetch_all_ows_data.py` to get data from OneWorldSync
2. **Store in Spaces**: Data automatically stored in DigitalOcean Spaces
3. **Load to Database**: Use this orchestrator to load data into PostgreSQL
4. **Schedule**: Set up cron jobs or use DigitalOcean App Platform scheduling

### **Scheduling Example:**
```bash
# Daily at 2 AM
0 2 * * * cd /path/to/backend/etl_pipeline && python run_etl.py

# Every 6 hours
0 */6 * * * cd /path/to/backend/etl_pipeline && python run_etl.py
```

## 📞 Support

For issues or questions:
1. Check the log file (`etl_orchestrator.log`)
2. Verify environment variables
3. Ensure database tables exist
4. Check DigitalOcean Spaces permissions

---

**Happy ETL-ing! 🚀** 