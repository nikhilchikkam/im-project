import os
import asyncio
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Load environment variables
load_dotenv(dotenv_path="db scripts/.env")

async def test_email_configuration():
    """Test email configuration"""
    
    print("Testing Email Configuration")
    print("=" * 50)
    
    # Get email configuration from environment
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM", "noreply@nutrigence.app")
    mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    
    print(f"Email Configuration:")
    print(f"   Username: {mail_username}")
    print(f"   Server: {mail_server}:{mail_port}")
    print(f"   From: {mail_from}")
    print(f"   Password: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    
    if not mail_username or not mail_password:
        print("Email configuration incomplete!")
        print("   Please set MAIL_USERNAME and MAIL_PASSWORD in your .env file")
        return False
    
    try:
        # Configure FastMail
        mail_config = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=mail_from,
            MAIL_PORT=mail_port,
            MAIL_SERVER=mail_server,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True
        )
        
        fm = FastMail(mail_config)
        
        # Create test message
        message = MessageSchema(
            subject="Nutrigence App - Email Test",
            recipients=[mail_username],  # Send to yourself for testing
            body="""
            <html>
                <body>
                    <h2>Email Configuration Test Successful!</h2>
                    <p>Your email configuration is working correctly.</p>
                    <p>This means magic links will be sent properly to your users.</p>
                    <hr>
                    <p><strong>Configuration Details:</strong></p>
                    <ul>
                        <li>Server: {server}</li>
                        <li>Port: {port}</li>
                        <li>From: {from_email}</li>
                    </ul>
                    <p>Ready for production!</p>
                </body>
            </html>
            """.format(server=mail_server, port=mail_port, from_email=mail_from),
            subtype="html"
        )
        
        print("\nSending test email...")
        await fm.send_message(message)
        
        print("Test email sent successfully!")
        print("   Check your inbox for the test email")
        print("\nEmail configuration is working!")
        return True
        
    except Exception as e:
        print(f"Email test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Gmail App Password is correct")
        print("2. Make sure 2-Factor Authentication is enabled")
        print("3. Verify the App Password was generated for 'Mail'")
        print("4. Check if 'Less secure app access' is disabled")
        return False

def check_environment_variables():
    """Check if required email environment variables are set"""
    print("Checking Environment Variables...")
    
    required_vars = [
        "MAIL_USERNAME",
        "MAIL_PASSWORD"
    ]
    
    optional_vars = [
        "MAIL_FROM",
        "MAIL_SERVER",
        "MAIL_PORT"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_required.append(var)
        else:
            print(f"{var}: Set")
    
    for var in optional_vars:
        value = os.getenv(var)
        if not value:
            missing_optional.append(var)
        else:
            print(f"{var}: {value}")
    
    if missing_required:
        print(f"\nMissing required variables:")
        for var in missing_required:
            print(f"   - {var}")
    
    if missing_optional:
        print(f"\nMissing optional variables (using defaults):")
        for var in missing_optional:
            print(f"   - {var}")
    
    return len(missing_required) == 0

async def main():
    """Main test function"""
    print("Testing Email Configuration for Magic Links")
    print("=" * 60)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\nEnvironment variables not properly configured")
        print("Please set up your .env file first")
        return
    
    # Test email configuration
    email_ok = await test_email_configuration()
    
    if email_ok:
        print("\nEmail setup complete!")
        print("Your magic link authentication is ready to use!")
    else:
        print("\nEmail setup failed")
        print("Please check the troubleshooting steps above")

if __name__ == "__main__":
    asyncio.run(main()) 