import secrets
import string
import os

def generate_production_secret_key(length=64):
    """Generate a production-grade secret key"""
    return secrets.token_urlsafe(length)

def generate_production_magic_link_key(length=64):
    """Generate a production-grade magic link key"""
    return secrets.token_urlsafe(length)

def generate_database_password(length=32):
    """Generate a secure database password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Generating Production-Grade Security Keys")
    print("=" * 60)
    
    # Generate production keys
    secret_key = generate_production_secret_key()
    magic_link_key = generate_production_magic_link_key()
    db_password = generate_database_password()
    
    print("\n📋 PRODUCTION ENVIRONMENT VARIABLES:")
    print("-" * 60)
    print(f"SECRET_KEY={secret_key}")
    print(f"MAGIC_LINK_SECRET_KEY={magic_link_key}")
    print(f"DB_PASSWORD={db_password}")
    
    print("\n⚠️  PRODUCTION SECURITY CHECKLIST:")
    print("-" * 60)
    print("✅ Use different keys for each environment")
    print("✅ Store keys in DigitalOcean App Platform environment variables")
    print("✅ Never commit production keys to version control")
    print("✅ Use HTTPS in production")
    print("✅ Set up proper email domain (not Gmail for production)")
    print("✅ Configure production OAuth credentials")
    print("✅ Set up monitoring and logging")
    print("✅ Use production database (not development)")
    
    print("\n📧 PRODUCTION EMAIL RECOMMENDATIONS:")
    print("-" * 60)
    print("❌ Don't use Gmail for production")
    print("✅ Use dedicated email service:")
    print("   - SendGrid")
    print("   - AWS SES")
    print("   - Mailgun")
    print("   - Postmark")
    
    print("\n🔒 PRODUCTION DATABASE SECURITY:")
    print("-" * 60)
    print("✅ Use dedicated production database")
    print("✅ Enable SSL/TLS connections")
    print("✅ Use strong database passwords")
    print("✅ Restrict database access to App Platform IPs")
    print("✅ Enable database backups")
    
    print("\n🌐 PRODUCTION DOMAIN SETUP:")
    print("-" * 60)
    print("✅ Use custom domain (nutrigence.app)")
    print("✅ Set up SSL certificates")
    print("✅ Configure proper CORS settings")
    print("✅ Set up CDN for static assets")
    
    print("\n📝 DIGITALOCEAN APP PLATFORM SETUP:")
    print("-" * 60)
    print("1. Go to App Platform dashboard")
    print("2. Select your backend app")
    print("3. Settings → Environment Variables")
    print("4. Add each variable securely")
    print("5. Redeploy the app")
    
    # Save to file (optional)
    save_to_file = input("\n💾 Save production keys to file? (y/n): ").lower().strip()
    if save_to_file == 'y':
        filename = "production_keys.txt"
        with open(filename, 'w') as f:
            f.write("# PRODUCTION KEYS - KEEP SECURE!\n")
            f.write("# Never commit this file to version control!\n\n")
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write(f"MAGIC_LINK_SECRET_KEY={magic_link_key}\n")
            f.write(f"DB_PASSWORD={db_password}\n")
        print(f"✅ Keys saved to {filename}")
        print("⚠️  Remember to delete this file after setting up environment variables!")

if __name__ == "__main__":
    main() 