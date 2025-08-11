#!/usr/bin/env python3
"""
Script to fix database table constraints for proper conflict resolution
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_table_constraints():
    """Fix table constraints for proper conflict resolution"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔧 Fixing table constraints for conflict resolution...")
        
        # Fix product_allergen table constraints
        print("📋 Fixing product_allergen constraints...")
        cur.execute("""
            ALTER TABLE product_allergen 
            DROP CONSTRAINT IF EXISTS product_allergen_unique_constraint;
        """)
        
        cur.execute("""
            ALTER TABLE product_allergen 
            ADD CONSTRAINT product_allergen_unique_constraint 
            UNIQUE (gtin, allergenSpecificationAgency, allergenSpecificationName, allergenTypeCode);
        """)
        print("✅ Added unique constraint to product_allergen")
        
        # Fix product_nutrition table constraints
        print("📋 Fixing product_nutrition constraints...")
        cur.execute("""
            ALTER TABLE product_nutrition 
            DROP CONSTRAINT IF EXISTS product_nutrition_unique_constraint;
        """)
        
        cur.execute("""
            ALTER TABLE product_nutrition 
            ADD CONSTRAINT product_nutrition_unique_constraint 
            UNIQUE (gtin, nutrient_code);
        """)
        print("✅ Added unique constraint to product_nutrition")
        
        # Verify the constraints
        print("\n🔍 Verifying constraints...")
        cur.execute("""
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
        """)
        
        constraints = cur.fetchall()
        
        print(f"\n📋 Found {len(constraints)} unique constraints:")
        print("-" * 80)
        print(f"{'Table':<20} {'Constraint':<35} {'Columns'}")
        print("-" * 80)
        
        current_table = ""
        current_constraint = ""
        columns = []
        
        for row in constraints:
            if row['table_name'] != current_table or row['constraint_name'] != current_constraint:
                if current_table:
                    print(f"{current_table:<20} {current_constraint:<35} {', '.join(columns)}")
                current_table = row['table_name']
                current_constraint = row['constraint_name']
                columns = [row['column_name']]
            else:
                columns.append(row['column_name'])
        
        # Print the last constraint
        if current_table:
            print(f"{current_table:<20} {current_constraint:<35} {', '.join(columns)}")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Table constraints fixed successfully!")
        print("The ETL pipeline should now work with proper conflict resolution.")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing constraints: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not found")
        print("Please check your .env file")
    else:
        success = fix_table_constraints()
        if success:
            print("\n🚀 Ready to run ETL pipeline!")
        else:
            print("\n❌ Failed to fix constraints") 