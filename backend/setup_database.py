#!/usr/bin/env python3
"""
Database Setup Script for Nutrigence Application

This script creates all necessary database tables for the application:
- users (authentication)
- cart_items (shopping cart)
- wishlist_items (user wishlists)

Run this script before starting the application to ensure all tables exist.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv("db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def create_users_table(conn, cur):
    """Create the users table for authentication"""
    print("Creating users table...")
    
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
    
    create_trigger_sql = """
    DROP TRIGGER IF EXISTS update_users_updated_at ON users;
    CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """
    
    cur.execute(create_table_sql)
    cur.execute(create_index_sql)
    cur.execute(create_trigger_function_sql)
    cur.execute(create_trigger_sql)
    
    print("✅ Users table created successfully!")

def create_cart_wishlist_tables(conn, cur):
    """Create cart and wishlist tables"""
    print("Creating cart and wishlist tables...")
    
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
    
    # Create indexes
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id);
    CREATE INDEX IF NOT EXISTS idx_cart_items_gtin ON cart_items(gtin);
    CREATE INDEX IF NOT EXISTS idx_wishlist_items_user_id ON wishlist_items(user_id);
    CREATE INDEX IF NOT EXISTS idx_wishlist_items_gtin ON wishlist_items(gtin);
    """
    
    cur.execute(create_cart_table_sql)
    cur.execute(create_wishlist_table_sql)
    cur.execute(create_indexes_sql)
    
    print("✅ Cart and wishlist tables created successfully!")

def verify_tables(conn, cur):
    """Verify that all required tables exist"""
    print("\nVerifying tables...")
    
    required_tables = ['users', 'cart_items', 'wishlist_items']
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = ANY(%s)
        ORDER BY table_name
    """, (required_tables,))
    
    existing_tables = [row['table_name'] for row in cur.fetchall()]
    
    print(f"Required tables: {required_tables}")
    print(f"Existing tables: {existing_tables}")
    
    missing_tables = set(required_tables) - set(existing_tables)
    
    if missing_tables:
        print(f"❌ Missing tables: {list(missing_tables)}")
        return False
    else:
        print("✅ All required tables exist!")
        return True

def show_table_info(conn, cur):
    """Show information about the created tables"""
    print("\n📊 Database Tables Information:")
    print("=" * 60)
    
    tables = ['users', 'cart_items', 'wishlist_items']
    
    for table_name in tables:
        print(f"\n📋 {table_name.upper()} TABLE:")
        print("-" * 40)
        
        # Get column information
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cur.fetchall()
        print(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Default'}")
        print("-" * 60)
        for col in columns:
            default = col['column_default'] or 'None'
            print(f"{col['column_name']:<20} {col['data_type']:<15} {col['is_nullable']:<10} {default}")
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cur.fetchone()['count']
        print(f"\n📈 Total rows: {count}")

def main():
    """Main function to set up the database"""
    print("🚀 Nutrigence Database Setup")
    print("=" * 50)
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please check your .env file in the 'db scripts' directory")
        return False
    
    try:
        # Connect to database
        print(f"🔗 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        print("✅ Database connection successful!")
        
        # Create tables
        create_users_table(conn, cur)
        create_cart_wishlist_tables(conn, cur)
        
        # Commit all changes
        conn.commit()
        
        # Verify tables
        if not verify_tables(conn, cur):
            print("❌ Table verification failed!")
            return False
        
        # Show table information
        show_table_info(conn, cur)
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the backend server: uvicorn api:app --reload")
        print("2. Test the authentication system")
        print("3. Test cart and wishlist functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1) 