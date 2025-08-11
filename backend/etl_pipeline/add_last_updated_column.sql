-- SQL script to add last_updated column to products table
-- This script adds a timestamp column to store the lastModifiedDate from OneWorldSync data

-- Add the last_updated column to the products table
-- Using TIMESTAMP to store the lastModifiedDate from OneWorldSync
ALTER TABLE products 
ADD COLUMN last_updated TIMESTAMP;

-- Create an index on the last_updated column for better query performance
CREATE INDEX IF NOT EXISTS idx_products_last_updated ON products(last_updated);

-- Create a trigger function to automatically update last_updated on row updates
-- This will be useful for when you update products with new OneWorldSync data
CREATE OR REPLACE FUNCTION update_products_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if a new last_updated value is provided
    IF NEW.last_updated IS NOT NULL THEN
        NEW.last_updated = NEW.last_updated;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update last_updated when a row is updated
DROP TRIGGER IF EXISTS update_products_last_updated_trigger ON products;
CREATE TRIGGER update_products_last_updated_trigger
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_products_last_updated();

-- Verify the column was added successfully
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'products' AND column_name = 'last_updated';  