import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv("db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def create_users_table():
    """Create the users table for authentication"""
    
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        # Create users table
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
        
        # Create index on email for faster lookups
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """
        
        # Create trigger to update updated_at timestamp
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
        
        print("Creating users table...")
        cur.execute(create_table_sql)
        
        print("Creating email index...")
        cur.execute(create_index_sql)
        
        print("Creating trigger function...")
        cur.execute(create_trigger_function_sql)
        
        print("Creating update trigger...")
        cur.execute(create_trigger_sql)
        
        # Commit changes
        conn.commit()
        
        # Verify table was created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users'
        """)
        
        if cur.fetchone():
            print("Users table created successfully!")
            
            # Show table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            print("\nTable structure:")
            print("-" * 80)
            print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Default'}")
            print("-" * 80)
            for col in columns:
                print(f"{col['column_name']:<20} {col['data_type']:<15} {col['is_nullable']:<10} {col['column_default'] or 'None'}")
            
            return True
        else:
            print("Failed to create users table")
            return False
            
    except Exception as e:
        print(f"Error creating users table: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_existing_users():
    """Check if there are any existing users in the table"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) as count FROM users")
        result = cur.fetchone()
        count = result['count'] if result else 0
        
        print(f"\n👥 Current users in database: {count}")
        
        if count > 0:
            cur.execute("SELECT id, email, auth_provider, is_verified, created_at FROM users LIMIT 5")
            users = cur.fetchall()
            print("\nSample users:")
            print("-" * 80)
            print(f"{'ID':<5} {'Email':<30} {'Provider':<10} {'Verified':<10} {'Created'}")
            print("-" * 80)
            for user in users:
                print(f"{user['id']:<5} {user['email']:<30} {user['auth_provider']:<10} {str(user['is_verified']):<10} {user['created_at']}")
        
        return count
        
    except Exception as e:
        print(f"Error checking users: {e}")
        return 0
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to set up the database"""
    print("Setting up authentication database...")
    print("=" * 50)
    
    # Create users table
    success = create_users_table()
    
    if success:
        # Check existing users
        check_existing_users()
        
        print("\nDatabase setup complete!")
        print("\nNext steps:")
        print("1. Configure your .env file with email settings")
        print("2. Set up Google OAuth credentials")
        print("3. Test the authentication system")
    else:
        print("\nDatabase setup failed!")
        print("Please check your DATABASE_URL and try again.")

if __name__ == "__main__":
    main() 