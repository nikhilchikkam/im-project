#!/usr/bin/env python3
"""
Wishlist Groups Database Setup Script

This script creates the necessary tables for wishlist grouping functionality:
- wishlist_groups (for organizing wishlists)
- wishlist_items (updated to reference groups)

Run this script to set up the wishlist grouping feature.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_wishlist_groups_tables(conn, cur):
    """Create wishlist groups and update wishlist items table"""
    print("Setting up wishlist groups functionality...")
    
    # Create wishlist_groups table
    create_groups_table_sql = """
    CREATE TABLE IF NOT EXISTS wishlist_groups (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        is_public BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, name)
    );
    """
    
    # Create wishlist_group_members table for sharing
    create_members_table_sql = """
    CREATE TABLE IF NOT EXISTS wishlist_group_members (
        id SERIAL PRIMARY KEY,
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role VARCHAR(20) DEFAULT 'member', -- 'owner', 'admin', 'member'
        joined_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (group_id) REFERENCES wishlist_groups(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(group_id, user_id)
    );
    """
    
    # Update wishlist_items table to include group_id
    update_wishlist_items_sql = """
    ALTER TABLE wishlist_items 
    ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES wishlist_groups(id) ON DELETE CASCADE;
    """
    
    # Create indexes for better performance
    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_wishlist_groups_user_id ON wishlist_groups(user_id);
    CREATE INDEX IF NOT EXISTS idx_wishlist_groups_name ON wishlist_groups(name);
    CREATE INDEX IF NOT EXISTS idx_wishlist_group_members_group_id ON wishlist_group_members(group_id);
    CREATE INDEX IF NOT EXISTS idx_wishlist_group_members_user_id ON wishlist_group_members(user_id);
    CREATE INDEX IF NOT EXISTS idx_wishlist_items_group_id ON wishlist_items(group_id);
    """
    
    # Create trigger function for updated_at
    create_trigger_function_sql = """
    CREATE OR REPLACE FUNCTION update_wishlist_groups_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """
    
    # Create trigger for wishlist_groups
    create_trigger_sql = """
    DROP TRIGGER IF EXISTS update_wishlist_groups_updated_at ON wishlist_groups;
    CREATE TRIGGER update_wishlist_groups_updated_at
        BEFORE UPDATE ON wishlist_groups
        FOR EACH ROW
        EXECUTE FUNCTION update_wishlist_groups_updated_at();
    """
    
    print("Creating wishlist_groups table...")
    cur.execute(create_groups_table_sql)
    
    print("Creating wishlist_group_members table...")
    cur.execute(create_members_table_sql)
    
    print("Updating wishlist_items table...")
    cur.execute(update_wishlist_items_sql)
    
    print("Creating indexes...")
    cur.execute(create_indexes_sql)
    
    print("Creating trigger function...")
    cur.execute(create_trigger_function_sql)
    
    print("Creating trigger...")
    cur.execute(create_trigger_sql)
    
    print("Wishlist groups tables created successfully!")

def create_default_wishlist(conn, cur):
    """Create a default wishlist for existing users"""
    print("Creating default wishlists for existing users...")
    
    # Get all users who don't have a default wishlist
    cur.execute("""
        SELECT DISTINCT u.id, u.email 
        FROM users u 
        LEFT JOIN wishlist_groups wg ON u.id = wg.user_id AND wg.name = 'My Wishlist'
        WHERE wg.id IS NULL
    """)
    
    users_without_default = cur.fetchall()
    
    if users_without_default:
        print(f"Creating default wishlists for {len(users_without_default)} users...")
        
        for user in users_without_default:
            # Create default wishlist group
            cur.execute("""
                INSERT INTO wishlist_groups (user_id, name, description, is_public)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (user['id'], 'My Wishlist', 'Default wishlist', False))
            
            group_id = cur.fetchone()['id']
            
            # Move existing wishlist items to the default group
            cur.execute("""
                UPDATE wishlist_items 
                SET group_id = %s 
                WHERE user_id = %s AND group_id IS NULL
            """, (group_id, user['id']))
            
            print(f"Created default wishlist for user {user['email']}")
    else:
        print("All users already have default wishlists")

def verify_wishlist_groups(conn, cur):
    """Verify that wishlist groups functionality is working"""
    print("\nVerifying wishlist groups setup...")
    
    # Check tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name IN ('wishlist_groups', 'wishlist_group_members')
        ORDER BY table_name
    """)
    
    tables = [row['table_name'] for row in cur.fetchall()]
    print(f"Created tables: {tables}")
    
    # Check wishlist_items has group_id column
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'wishlist_items' AND column_name = 'group_id'
    """)
    
    if cur.fetchone():
        print("wishlist_items table has group_id column")
    else:
        print("wishlist_items table missing group_id column")
        return False
    
    # Count wishlist groups
    cur.execute("SELECT COUNT(*) as count FROM wishlist_groups")
    groups_count = cur.fetchone()['count']
    print(f"Total wishlist groups: {groups_count}")
    
    # Count group members
    cur.execute("SELECT COUNT(*) as count FROM wishlist_group_members")
    members_count = cur.fetchone()['count']
    print(f"Total group members: {members_count}")
    
    return True

def show_wishlist_groups_info(conn, cur):
    """Show information about wishlist groups"""
    print("\nWishlist Groups Information:")
    print("=" * 60)
    
    # Show sample wishlist groups
    cur.execute("""
        SELECT wg.*, u.email as owner_email, 
               COUNT(wgm.user_id) as member_count,
               COUNT(wi.id) as item_count
        FROM wishlist_groups wg
        LEFT JOIN users u ON wg.user_id = u.id
        LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
        LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
        GROUP BY wg.id, u.email
        ORDER BY wg.created_at DESC
        LIMIT 10
    """)
    
    groups = cur.fetchall()
    
    if groups:
        print(f"\nSample Wishlist Groups:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Owner':<25} {'Members':<10} {'Items':<8} {'Public'}")
        print("-" * 80)
        for group in groups:
            print(f"{group['id']:<5} {group['name']:<20} {group['owner_email']:<25} {group['member_count']:<10} {group['item_count']:<8} {group['is_public']}")
    else:
        print("No wishlist groups found")

def main():
    """Main function to set up wishlist groups"""
    print("Wishlist Groups Setup")
    print("=" * 50)
    
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        print(f"Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        print("Database connection successful!")
        
        # Create wishlist groups tables
        create_wishlist_groups_tables(conn, cur)
        
        # Create default wishlists for existing users
        create_default_wishlist(conn, cur)
        
        # Commit all changes
        conn.commit()
        
        # Verify setup
        if not verify_wishlist_groups(conn, cur):
            print(" Wishlist groups verification failed!")
            return False
        
        # Show information
        show_wishlist_groups_info(conn, cur)
        
        print("\nWishlist groups setup completed successfully!")
        print("\nFeatures added:")
        print("- Multiple named wishlists per user")
        print("- Wishlist sharing and collaboration")
        print("- Public/private wishlist settings")
        print("- Default wishlist for all users")
        print("- Proper database relationships and constraints")
        
        return True
        
    except Exception as e:
        print(f"Error during wishlist groups setup: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1) 