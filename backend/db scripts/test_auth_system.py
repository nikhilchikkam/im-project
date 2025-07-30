import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv(dotenv_path="db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def test_database_connection():
    """Test database connection and users table"""
    print("🔍 Testing database connection...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        # Test if users table exists
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users'
        """)
        
        if cur.fetchone():
            print("Users table exists")
            
            # Count users
            cur.execute("SELECT COUNT(*) as count FROM users")
            result = cur.fetchone()
            print(f"Found {result['count']} users in database")
            
            return True
        else:
            print("Users table does not exist")
            print("Run create_users_table.py first")
            return False
            
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_magic_link_endpoint():
    """Test magic link endpoint"""
    print("\nTesting magic link endpoint...")
    
    test_email = "test@example.com"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/magic-link",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("Magic link endpoint working")
            data = response.json()
            print(f"   Response: {data.get('message', 'No message')}")
            return True
        else:
            print(f"Magic link endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to API server")
        print("   Make sure the backend server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"Error testing magic link: {e}")
        return False

def test_google_oauth_url():
    """Test Google OAuth URL endpoint"""
    print("\nTesting Google OAuth URL endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/google/url")
        
        if response.status_code == 200:
            print("Google OAuth URL endpoint working")
            data = response.json()
            print(f"   OAuth URL: {data.get('url', 'No URL')}")
            return True
        else:
            print(f"Google OAuth URL endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to API server")
        return False
    except Exception as e:
        print(f"Error testing Google OAuth: {e}")
        return False

def test_user_creation():
    """Test user creation in database"""
    print("\nTesting user creation...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        # Insert a test user
        test_user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "auth_provider": "email",
            "is_verified": False
        }
        
        cur.execute("""
            INSERT INTO users (email, first_name, last_name, auth_provider, is_verified)
            VALUES (%(email)s, %(first_name)s, %(last_name)s, %(auth_provider)s, %(is_verified)s)
            ON CONFLICT (email) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                auth_provider = EXCLUDED.auth_provider,
                is_verified = EXCLUDED.is_verified
            RETURNING id, email, is_verified
        """, test_user_data)
        
        result = cur.fetchone()
        conn.commit()
        
        if result:
            print(f"Test user created/updated: ID {result['id']}, Email: {result['email']}")
            print(f"   Verified: {result['is_verified']}")
            return True
        else:
            print("Failed to create test user")
            return False
            
    except Exception as e:
        print(f"Error creating test user: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_environment_variables():
    """Check if required environment variables are set"""
    print("Checking environment variables...")
    
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "MAGIC_LINK_SECRET_KEY",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_FROM",
        "FRONTEND_URL"
    ]
    
    optional_vars = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"{var}: Set")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"{var}: Set")
    
    if missing_required:
        print(f"\nMissing required environment variables:")
        for var in missing_required:
            print(f"   - {var}")
    
    if missing_optional:
        print(f"\nMissing optional environment variables:")
        for var in missing_optional:
            print(f"   - {var}")
    
    return len(missing_required) == 0

def main():
    """Main test function"""
    print("Testing Authentication System")
    print("=" * 50)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\nEnvironment variables not properly configured")
        print("Please check your .env file and try again")
        return
    
    # Test database
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\nDatabase test failed")
        return
    
    # Test user creation
    user_ok = test_user_creation()
    
    # Test API endpoints (only if server is running)
    api_ok = test_magic_link_endpoint()
    oauth_ok = test_google_oauth_url()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"   Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"   Database Connection: {'✅' if db_ok else '❌'}")
    print(f"   User Creation: {'✅' if user_ok else '❌'}")
    print(f"   Magic Link API: {'✅' if api_ok else '❌'}")
    print(f"   Google OAuth API: {'✅' if oauth_ok else '❌'}")
    
    if all([env_ok, db_ok, user_ok]):
        print("\nCore authentication system is ready!")
        if not api_ok:
            print("API tests failed - make sure the backend server is running")
    else:
        print("\nSome tests failed - please check the issues above")

if __name__ == "__main__":
    main() 