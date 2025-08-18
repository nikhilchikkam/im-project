# Backend Database Scripts Documentation
## Nutrigence Database Setup & Management

### 📋 Table of Contents
1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Setup Scripts](#setup-scripts)
4. [Migration Scripts](#migration-scripts)
5. [Data Loading Scripts](#data-loading-scripts)
6. [Maintenance Scripts](#maintenance-scripts)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The backend database scripts handle database initialization, schema management, data loading, and maintenance operations for the Nutrigence platform. These scripts ensure proper database setup and data integrity.

### 🎯 Key Features
- **Database Initialization**: Complete database setup with all required tables
- **Schema Management**: Table creation, indexes, and constraints
- **Data Loading**: Product data and reference data loading
- **Migration Support**: Database schema evolution
- **Maintenance Tools**: Performance optimization and cleanup

---

## Database Schema

### 🗄️ Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(20),
    business_id VARCHAR(100),
    auth_provider VARCHAR(20) NOT NULL DEFAULT 'email',
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Cart Items Table
```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    gtin VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, gtin),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### Wishlist Items Table
```sql
CREATE TABLE wishlist_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    gtin VARCHAR(50) NOT NULL,
    group_id INTEGER,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, gtin),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES wishlist_groups(id) ON DELETE CASCADE
);
```

#### Wishlist Groups Table
```sql
CREATE TABLE wishlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### Products Table (ETL Generated)
```sql
CREATE TABLE products (
    gtin VARCHAR(50) PRIMARY KEY,
    name VARCHAR(500),
    description TEXT,
    ingredients TEXT,
    brand VARCHAR(255),
    product_type VARCHAR(100),
    is_consumer_unit BOOLEAN,
    gpc_code VARCHAR(50),
    class_title VARCHAR(255),
    family_title VARCHAR(255),
    is_smart_snack BOOLEAN,
    nova_label VARCHAR(50),
    is_good_choice VARCHAR(10),
    recommended_ok VARCHAR(10),
    image_urls JSONB,
    raw_data TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

### 🔗 Relationships & Indexes

#### Foreign Key Relationships
- **Users** → **Cart Items** (1:many)
- **Users** → **Wishlist Items** (1:many)
- **Users** → **Wishlist Groups** (1:many)
- **Wishlist Groups** → **Wishlist Items** (1:many)

#### Performance Indexes
```sql
-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_auth_provider ON users(auth_provider);

-- Cart indexes
CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);
CREATE INDEX idx_cart_items_gtin ON cart_items(gtin);

-- Wishlist indexes
CREATE INDEX idx_wishlist_items_user_id ON wishlist_items(user_id);
CREATE INDEX idx_wishlist_items_gtin ON wishlist_items(gtin);
CREATE INDEX idx_wishlist_items_group_id ON wishlist_items(group_id);

-- Product indexes
CREATE INDEX idx_products_gpc_code ON products(gpc_code);
CREATE INDEX idx_products_class_title ON products(class_title);
CREATE INDEX idx_products_family_title ON products(family_title);
CREATE INDEX idx_products_is_smart_snack ON products(is_smart_snack);
```

---

## Setup Scripts

### 🚀 Main Setup Script

#### setup_database.py
```python
#!/usr/bin/env python3
"""
Database Setup Script for Nutrigence Application
Creates all necessary database tables and indexes.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

def main():
    """Main setup function"""
    load_dotenv("db scripts/.env")
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Create tables
        create_users_table(conn, cur)
        create_cart_wishlist_tables(conn, cur)
        
        # Verify setup
        verify_tables(conn, cur)
        show_table_info(conn, cur)
        
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
```

### 🔧 Table Creation Functions

#### Users Table Creation
```python
def create_users_table(conn, cur):
    """Create the users table for authentication"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        company_name VARCHAR(255),
        phone VARCHAR(20),
        business_id VARCHAR(100),
        auth_provider VARCHAR(20) NOT NULL DEFAULT 'email',
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """
    
    create_trigger_function_sql = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """
    
    cur.execute(create_table_sql)
    cur.execute(create_index_sql)
    cur.execute(create_trigger_function_sql)
    conn.commit()
```

#### Cart & Wishlist Tables Creation
```python
def create_cart_wishlist_tables(conn, cur):
    """Create cart and wishlist tables"""
    # Create cart_items table
    create_cart_table_sql = """
    CREATE TABLE IF NOT EXISTS cart_items (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        gtin VARCHAR(50) NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        added_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(user_id, gtin),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    # Create wishlist_items table
    create_wishlist_table_sql = """
    CREATE TABLE IF NOT EXISTS wishlist_items (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        gtin VARCHAR(50) NOT NULL,
        group_id INTEGER,
        added_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(user_id, gtin),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (group_id) REFERENCES wishlist_groups(id) ON DELETE CASCADE
    );
    """
    
    # Create wishlist_groups table
    create_wishlist_groups_table_sql = """
    CREATE TABLE IF NOT EXISTS wishlist_groups (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    cur.execute(create_cart_table_sql)
    cur.execute(create_wishlist_table_sql)
    cur.execute(create_wishlist_groups_table_sql)
    conn.commit()
```

---

## Migration Scripts

### 📊 Schema Migration

#### add_last_updated_column.sql
```sql
-- Add last_updated column to products table
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT NOW();

-- Create trigger to update last_updated
CREATE OR REPLACE FUNCTION update_products_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_last_updated_trigger
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_products_last_updated();
```

#### fix_products_table.sql
```sql
-- Fix products table schema
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS raw_data TEXT;

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS name VARCHAR(500);

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS description TEXT;

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS ingredients TEXT;

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS brand VARCHAR(255);

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS product_type VARCHAR(100);

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS is_consumer_unit BOOLEAN;

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS gpc_code VARCHAR(50);
```

---

## Data Loading Scripts

### 📥 Reference Data Loading

#### allergen_loader.py
```python
#!/usr/bin/env python3
"""
Allergen Data Loader
Loads allergen information from OneWorldSync data.
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor

def extract_allergens(product_data):
    """Extract allergen information from product data"""
    allergens = []
    if 'allergens' in product_data:
        for allergen in product_data['allergens']:
            allergens.append({
                'gtin': product_data.get('gtin'),
                'allergen_name': allergen.get('name'),
                'allergen_code': allergen.get('code')
            })
    return allergens

def insert_allergens(conn, allergens):
    """Insert allergen data into database"""
    cur = conn.cursor()
    
    for allergen in allergens:
        cur.execute("""
            INSERT INTO product_allergen (gtin, allergen_name, allergen_code)
            VALUES (%s, %s, %s)
            ON CONFLICT (gtin, allergen_name) DO NOTHING
        """, (allergen['gtin'], allergen['allergen_name'], allergen['allergen_code']))
    
    conn.commit()
    cur.close()
```

#### nutrition_loader.py
```python
#!/usr/bin/env python3
"""
Nutrition Data Loader
Loads nutritional information from OneWorldSync data.
"""

def extract_nutrition(product_data):
    """Extract nutrition information from product data"""
    nutrition = []
    if 'nutrition' in product_data:
        for nutrient in product_data['nutrition']:
            nutrition.append({
                'gtin': product_data.get('gtin'),
                'nutrient_name': nutrient.get('name'),
                'nutrient_value': nutrient.get('value'),
                'nutrient_unit': nutrient.get('unit')
            })
    return nutrition

def insert_nutrition(conn, nutrition_data):
    """Insert nutrition data into database"""
    cur = conn.cursor()
    
    for nutrient in nutrition_data:
        cur.execute("""
            INSERT INTO product_nutrition (gtin, nutrient_name, nutrient_value, nutrient_unit)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (gtin, nutrient_name) DO UPDATE SET
                nutrient_value = EXCLUDED.nutrient_value,
                nutrient_unit = EXCLUDED.nutrient_unit
        """, (nutrient['gtin'], nutrient['nutrient_name'], 
              nutrient['nutrient_value'], nutrient['nutrient_unit']))
    
    conn.commit()
    cur.close()
```

---

## Maintenance Scripts

### 🔧 Database Maintenance

#### check_products_schema.py
```python
#!/usr/bin/env python3
"""
Script to check the current schema of the products table
"""

def check_products_schema():
    """Check the current schema of the products table"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if products table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'products'
        );
    """)
    
    table_exists = cur.fetchone()['exists']
    
    if not table_exists:
        print("❌ Products table does not exist!")
        return
    
    print("✅ Products table exists")
    
    # Get table schema
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'products'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    
    print(f"\n📋 Products table schema ({len(columns)} columns):")
    for col in columns:
        print(f"  {col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']}")
    
    cur.close()
    conn.close()
```

#### clean_spaces.py
```python
#!/usr/bin/env python3
"""
Clean up extra spaces in product data
"""

def clean_product_spaces():
    """Clean extra spaces in product names and descriptions"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Clean product names
    cur.execute("""
        UPDATE products 
        SET name = TRIM(REGEXP_REPLACE(name, '\s+', ' ', 'g'))
        WHERE name IS NOT NULL;
    """)
    
    # Clean descriptions
    cur.execute("""
        UPDATE products 
        SET description = TRIM(REGEXP_REPLACE(description, '\s+', ' ', 'g'))
        WHERE description IS NOT NULL;
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Product data cleaned successfully!")
```

---

## Troubleshooting

### 🚨 Common Issues

#### Database Connection Issues
```python
# Check database connection
def test_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
```

#### Table Verification
```python
def verify_tables(conn, cur):
    """Verify that all required tables exist"""
    required_tables = ['users', 'cart_items', 'wishlist_items', 'wishlist_groups']
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = ANY(%s)
        ORDER BY table_name
    """, (required_tables,))
    
    existing_tables = [row['table_name'] for row in cur.fetchall()]
    missing_tables = set(required_tables) - set(existing_tables)
    
    if missing_tables:
        print(f"❌ Missing tables: {list(missing_tables)}")
        return False
    else:
        print("✅ All required tables exist!")
        return True
```

### 🔧 Debugging Tools

#### Schema Inspection
```python
def inspect_table_schema(table_name):
    """Inspect table schema and constraints"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get columns
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    
    columns = cur.fetchall()
    print(f"\n📋 {table_name} table schema:")
    for col in columns:
        print(f"  {col['column_name']:<20} {col['data_type']:<15} {col['is_nullable']}")
    
    # Get constraints
    cur.execute("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name = %s;
    """, (table_name,))
    
    constraints = cur.fetchall()
    print(f"\n🔗 {table_name} table constraints:")
    for constraint in constraints:
        print(f"  {constraint['constraint_name']:<30} {constraint['constraint_type']}")
    
    cur.close()
    conn.close()
```

---

## 🎯 Key Takeaways

### 🏗️ Database Design Excellence
1. **Normalized Schema**: Proper table relationships and constraints
2. **Performance Indexes**: Strategic indexing for query optimization
3. **Data Integrity**: Foreign key constraints and triggers
4. **Scalable Design**: Efficient data structures for growth

### 🔧 Script Management
1. **Automated Setup**: Complete database initialization
2. **Migration Support**: Schema evolution capabilities
3. **Data Loading**: Efficient ETL processes
4. **Maintenance Tools**: Performance and cleanup utilities

### 📈 Operational Features
1. **Error Handling**: Comprehensive error checking and reporting
2. **Verification**: Table and data integrity validation
3. **Debugging**: Schema inspection and troubleshooting tools
4. **Documentation**: Clear script documentation and usage

---

*This database scripts documentation provides a comprehensive overview of database setup, management, and maintenance procedures. For specific implementation details, refer to the individual script files and their inline documentation.*

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: Database Development Team
