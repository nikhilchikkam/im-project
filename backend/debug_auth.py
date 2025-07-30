#!/usr/bin/env python3
"""
Debug script to test authentication system
"""

import os
import jwt
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv("db scripts/.env")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL")

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        return None

def get_user_by_id(user_id: int):
    """Get user by ID from database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return result
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def test_authentication():
    """Test the authentication system"""
    print("🔍 Authentication Debug Test")
    print("=" * 50)
    
    # Check environment variables
    print(f"SECRET_KEY exists: {'✅' if SECRET_KEY else '❌'}")
    print(f"DATABASE_URL exists: {'✅' if DATABASE_URL else '❌'}")
    
    # Check database connection
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        cur = conn.cursor()
        
        # Check users table
        cur.execute("SELECT COUNT(*) as count FROM users")
        user_count = cur.fetchone()
        print(f"Users in database: {user_count['count']}")
        
        # List all users
        cur.execute("SELECT id, email, is_verified FROM users ORDER BY id")
        users = cur.fetchall()
        print("\n📋 Users in database:")
        for user in users:
            print(f"  ID: {user['id']}, Email: {user['email']}, Verified: {user['is_verified']}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test with a sample token (you'll need to provide a real token)
    print("\n🔑 Token Verification Test")
    print("To test token verification, please provide a valid access token from your browser's localStorage")
    print("You can find it by opening browser dev tools -> Application -> Local Storage -> accessToken")
    
    # Uncomment the lines below and add a real token for testing
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzUzODAzMzA4fQ.4EGIbL61YPsD47IS37muWm6MHrniGwYLka9JNWSSJqc"
    payload = verify_token(sample_token)
    if payload:
        user_id = payload.get("sub")
        print(f"Token payload: {payload}")
        if user_id:
            user = get_user_by_id(int(user_id))
            if user:
                print(f"User found: {user['email']}")
            else:
                print("❌ User not found in database")

if __name__ == "__main__":
    test_authentication() 