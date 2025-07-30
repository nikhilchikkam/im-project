import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(length)

def generate_magic_link_key(length=32):
    """Generate a secure random magic link key"""
    return secrets.token_urlsafe(length)

def main():
    print("Generating Secure Keys for Authentication")
    print("=" * 50)
    
    # Generate keys
    secret_key = generate_secret_key()
    magic_link_key = generate_magic_link_key()
    
    print("\nAdd these to your .env file:")
    print("-" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"MAGIC_LINK_SECRET_KEY={magic_link_key}")
    
    print("\nIMPORTANT SECURITY NOTES:")
    print("- Keep these keys secret and secure")
    print("- Never commit them to version control")
    print("- Use different keys for development and production")
    print("- Change these keys if they ever get compromised")
    
    print("\n Complete .env file example:")
    print("-" * 50)
    print("""# Database Configuration
DATABASE_URL=postgresql://doadmin:AVNS_NMYk0zxVj4qNKNLtPbT@db-postgresql-nyc3-53621-do-user-22167887-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require

# JWT Configuration
SECRET_KEY=""" + secret_key + """
MAGIC_LINK_SECRET_KEY=""" + magic_link_key + """

# Email Configuration (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_FROM=noreply@nutrigence.app
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password""")

if __name__ == "__main__":
    main() 