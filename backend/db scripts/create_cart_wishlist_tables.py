import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv("db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def create_cart_wishlist_tables():
    """Create the cart_items and wishlist_items tables"""
    
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
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
            added_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, gtin),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
        
        # Create indexes for better performance
        create_cart_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id);
        CREATE INDEX IF NOT EXISTS idx_cart_items_gtin ON cart_items(gtin);
        """
        
        create_wishlist_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_wishlist_items_user_id ON wishlist_items(user_id);
        CREATE INDEX IF NOT EXISTS idx_wishlist_items_gtin ON wishlist_items(gtin);
        """
        
        print("Creating cart_items table...")
        cur.execute(create_cart_table_sql)
        
        print("Creating wishlist_items table...")
        cur.execute(create_wishlist_table_sql)
        
        print("Creating cart indexes...")
        cur.execute(create_cart_indexes_sql)
        
        print("Creating wishlist indexes...")
        cur.execute(create_wishlist_indexes_sql)
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('cart_items', 'wishlist_items')
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        if len(tables) == 2:
            print("Cart and wishlist tables created successfully!")
            
            # Show table structures
            for table_name in ['cart_items', 'wishlist_items']:
                print(f"\n{table_name} table structure:")
                print("-" * 80)
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                
                columns = cur.fetchall()
                print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Default'}")
                print("-" * 80)
                for col in columns:
                    print(f"{col['column_name']:<20} {col['data_type']:<15} {col['is_nullable']:<10} {col['column_default'] or 'None'}")
            
            return True
        else:
            print("Failed to create cart and wishlist tables")
            return False
            
    except Exception as e:
        print(f"Error creating cart and wishlist tables: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_existing_data():
    """Check if there are any existing cart or wishlist items"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        # Check cart items
        cur.execute("SELECT COUNT(*) as count FROM cart_items")
        cart_count = cur.fetchone()['count']
        
        # Check wishlist items
        cur.execute("SELECT COUNT(*) as count FROM wishlist_items")
        wishlist_count = cur.fetchone()['count']
        
        print(f"\n🛒 Current cart items: {cart_count}")
        print(f"❤️  Current wishlist items: {wishlist_count}")
        
        return cart_count, wishlist_count
        
    except Exception as e:
        print(f"Error checking data: {e}")
        return 0, 0
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to set up the cart and wishlist tables"""
    print("Setting up cart and wishlist tables...")
    print("=" * 50)
    
    # Create tables
    success = create_cart_wishlist_tables()
    
    if success:
        # Check existing data
        check_existing_data()
        
        print("\nCart and wishlist tables setup complete!")
        print("\nTables created:")
        print("- cart_items: Stores user cart items")
        print("- wishlist_items: Stores user wishlist items")
        print("\nFeatures:")
        print("- Foreign key constraints to users table")
        print("- Unique constraints to prevent duplicates")
        print("- Automatic timestamps")
        print("- Indexes for better performance")
    else:
        print("\nCart and wishlist tables setup failed!")
        print("Please check your DATABASE_URL and try again.")

if __name__ == "__main__":
    main() 