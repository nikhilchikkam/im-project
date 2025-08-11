-- SQL script to fix the products table schema
-- This script adds missing columns that ProductLoader requires

-- Add the raw_data column to store the full JSON data from OneWorldSync
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS raw_data TEXT;

-- Add other columns that might be missing
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

-- Verify the columns were added successfully
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'products' 
AND column_name IN ('raw_data', 'name', 'description', 'ingredients', 'brand', 'product_type', 'is_consumer_unit', 'gpc_code')
ORDER BY column_name; 