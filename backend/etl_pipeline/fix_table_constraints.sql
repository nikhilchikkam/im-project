-- SQL script to fix table constraints for proper conflict resolution
-- This script adds unique constraints that match the ON CONFLICT clauses in the loaders

-- Fix product_allergen table constraints
-- Add unique constraint for the combination that identifies each allergen record
ALTER TABLE product_allergen 
DROP CONSTRAINT IF EXISTS product_allergen_unique_constraint;

ALTER TABLE product_allergen 
ADD CONSTRAINT product_allergen_unique_constraint 
UNIQUE (gtin, allergenSpecificationAgency, allergenSpecificationName, allergenTypeCode);

-- Fix product_nutrition table constraints  
-- Add unique constraint for the combination that identifies each nutrition record
ALTER TABLE product_nutrition 
DROP CONSTRAINT IF EXISTS product_nutrition_unique_constraint;

ALTER TABLE product_nutrition 
ADD CONSTRAINT product_nutrition_unique_constraint 
UNIQUE (gtin, nutrient_code);

-- Verify the constraints were added successfully
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name IN ('product_allergen', 'product_nutrition')
    AND tc.constraint_type = 'UNIQUE'
ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position; 