import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv("db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def update_wishlist_items_for_multiple_groups():
    """Update wishlist_items table to support items in multiple groups"""
    
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        print("Checking current wishlist_items table structure...")
        
        # Check if group_id column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'wishlist_items' AND column_name = 'group_id'
        """)
        
        group_id_exists = cur.fetchone()
        
        if not group_id_exists:
            print("Adding group_id column to wishlist_items table...")
            cur.execute("""
                ALTER TABLE wishlist_items 
                ADD COLUMN group_id INTEGER,
                ADD CONSTRAINT fk_wishlist_items_group_id 
                FOREIGN KEY (group_id) REFERENCES wishlist_groups(id) ON DELETE CASCADE
            """)
            print("✅ group_id column added successfully!")
        else:
            print("✅ group_id column already exists")
        
        # Check current unique constraints
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'wishlist_items' AND constraint_type = 'UNIQUE'
        """)
        
        unique_constraints = cur.fetchall()
        print(f"Current unique constraints: {[c['constraint_name'] for c in unique_constraints]}")
        
        # Find the constraint that includes user_id and gtin
        old_constraint_name = None
        for constraint in unique_constraints:
            cur.execute("""
                SELECT column_name
                FROM information_schema.constraint_column_usage
                WHERE constraint_name = %s
            """, (constraint['constraint_name'],))
            
            columns = [row['column_name'] for row in cur.fetchall()]
            if 'user_id' in columns and 'gtin' in columns and 'group_id' not in columns:
                old_constraint_name = constraint['constraint_name']
                break
        
        if old_constraint_name:
            print(f"Removing old unique constraint: {old_constraint_name}")
            cur.execute(f"ALTER TABLE wishlist_items DROP CONSTRAINT {old_constraint_name}")
            print("✅ Old unique constraint removed")
        
        # Add new unique constraint that includes group_id
        print("Adding new unique constraint for (user_id, gtin, group_id)...")
        cur.execute("""
            ALTER TABLE wishlist_items 
            ADD CONSTRAINT unique_wishlist_item_per_group 
            UNIQUE (user_id, gtin, group_id)
        """)
        print("✅ New unique constraint added")
        
        # Add index for better performance
        print("Adding index for group_id...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_wishlist_items_group_id ON wishlist_items(group_id)")
        print("✅ Index added")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        print("\nVerifying updated table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'wishlist_items'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("Updated wishlist_items table structure:")
        print("-" * 50)
        for col in columns:
            print(f"{col['column_name']:<15} {col['data_type']:<15} {col['is_nullable']}")
        
        # Check new constraints
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'wishlist_items' AND constraint_type = 'UNIQUE'
        """)
        
        new_constraints = cur.fetchall()
        print(f"\nNew unique constraints: {[c['constraint_name'] for c in new_constraints]}")
        
        print("\n✅ Migration completed successfully!")
        print("\nNow items can be part of multiple groups:")
        print("- Same user can have the same gtin in multiple groups")
        print("- Each group will have its own record")
        print("- Items can exist in main wishlist (group_id IS NULL) and in groups")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating wishlist_items table: {e}")
        conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_multiple_groups_functionality():
    """Test that items can now be in multiple groups"""
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment variables")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        print("\nTesting multiple groups functionality...")
        
        # Check if we can insert the same item in multiple groups
        test_user_id = 1  # Assuming user ID 1 exists
        test_gtin = "00041262287488"  # Test GTIN
        test_group_1 = 1  # Assuming group ID 1 exists
        test_group_2 = 2  # Assuming group ID 2 exists
        
        # Try to insert the same item in two different groups
        try:
            cur.execute("""
                INSERT INTO wishlist_items (user_id, gtin, group_id, added_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (user_id, gtin, group_id) DO NOTHING
            """, (test_user_id, test_gtin, test_group_1))
            
            cur.execute("""
                INSERT INTO wishlist_items (user_id, gtin, group_id, added_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (user_id, gtin, group_id) DO NOTHING
            """, (test_user_id, test_gtin, test_group_2))
            
            conn.commit()
            print("✅ Successfully added same item to multiple groups!")
            
            # Verify the records exist
            cur.execute("""
                SELECT group_id, added_at 
                FROM wishlist_items 
                WHERE user_id = %s AND gtin = %s
                ORDER BY group_id
            """, (test_user_id, test_gtin))
            
            records = cur.fetchall()
            print(f"Found {len(records)} records for this item:")
            for record in records:
                group_info = f"Group {record['group_id']}" if record['group_id'] else "Main Wishlist"
                print(f"  - {group_info}: {record['added_at']}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            conn.rollback()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to update wishlist_items for multiple groups support"""
    print("Updating wishlist_items table for multiple groups support...")
    print("=" * 60)
    
    # Update the table structure
    success = update_wishlist_items_for_multiple_groups()
    
    if success:
        # Test the functionality
        test_multiple_groups_functionality()
        
        print("\n🎉 Migration completed successfully!")
        print("\nKey changes made:")
        print("- Modified unique constraint to include group_id")
        print("- Items can now be in multiple groups simultaneously")
        print("- Each group maintains its own record for the same item")
        print("- Better performance with new indexes")
    else:
        print("\n❌ Migration failed!")
        print("Please check your DATABASE_URL and try again.")

if __name__ == "__main__":
    main() 