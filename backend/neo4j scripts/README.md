# Neo4j Scripts

This directory contains scripts for loading product hierarchy data into Neo4j database hosted on DigitalOcean.

## Current Scripts

### 1. `fetch_hierarchies_by_gtin.py`
**Purpose**: Fetches product hierarchy data from OneWorldSync API and saves it to local JSON files.

**Current Functionality**:
- Reads GTINs from `gtin.csv` file
- Fetches hierarchy data from OneWorldSync Content1 API
- Processes GTINs in batches of 1000
- Saves hierarchy data to JSON files in `results/hierarchies_by_gtin/`
- Includes comprehensive logging to `hierarchy_fetch_debug.log`
- Handles API retries and error recovery
- Creates batched output files (e.g., `hierarchies_batch_1.json`)

**Dependencies**:
- OneWorldSync Content1Client
- Requires valid API credentials in environment variables

**Usage**:
```bash
python fetch_hierarchies_by_gtin.py
```

**Input**: `gtin.csv` file with GTIN column
**Output**: JSON files in `results/hierarchies_by_gtin/` directory

### 2. `load_hierarchies_to_neo4j.py`
**Purpose**: Loads hierarchical relationships between products into Neo4j.

**Current Functionality**:
- Reads JSON files from `results/hierarchies_by_gtin/`
- Creates `CONTAINS` relationships between parent and child products
- Includes quantity and level properties on relationships
- Uses batch processing (500 relationships per batch)
- Includes comprehensive logging to `neo4j_loader.log`
- Skips existing relationships to avoid duplicates

**Usage**:
```bash
python load_hierarchies_to_neo4j.py
```

## Data Structure

### Hierarchy JSON Format
```json
[
  {
    "gtin": "00041303019337",
    "informationProviderGLN": "0751884000005",
    "targetMarket": "US",
    "hierarchy": [
      {
        "gtin": "10041303019334",
        "children": [
          {
            "gtin": "00041303019337",
            "quantity": "12"
          }
        ]
      }
    ]
  }
]
```

### Neo4j Graph Structure
- **Nodes**: `Product` nodes with `gtin` property
- **Relationships**: `CONTAINS` relationships with `quantity` and `level` properties
- **Example**: `(parent:Product {gtin: "123"})-[:CONTAINS {quantity: "12", level: 1}]->(child:Product {gtin: "456"})`

## Current Issues

### Problem
Currently, all three scripts work with local files, which is not scalable for production use:

1. **`fetch_hierarchies_by_gtin.py`**: Saves fetched data to local JSON files
2. **`load_hierarchies_to_neo4j.py`**: Reads from local JSON files


The scripts should follow the same pattern as the ETL pipeline, which uses DigitalOcean Spaces for data storage.



