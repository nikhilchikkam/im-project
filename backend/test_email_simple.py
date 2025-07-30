import os
import asyncio
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Load environment variables
load_dotenv(dotenv_path="db scripts/.env")

async def test_email():
    print("🧪 Testing Email Configuration")
    print("=" * 50)
    
    # Check environment variables
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")
    mail_server = os.getenv("MAIL_SERVER")
    mail_port = os.getenv("MAIL_PORT")
    
    print(f"📧 Email Configuration:")
    print(f"   Username: {mail_username}")
    print(f"   Server: {mail_server}")
    print(f"   Port: {mail_port}")
    print(f"   From: {mail_from}")
    print(f"   Password: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    
    if not all([mail_username, mail_password, mail_from, mail_server, mail_port]):
        print("\n❌ Missing email configuration!")
        print("Please check your .env file and ensure all email settings are configured.")
        return False
    
    try:
        # Configure FastMail
        mail_config = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=mail_from,
            MAIL_PORT=int(mail_port),
            MAIL_SERVER=mail_server,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True
        )
        
        # Create message
        message = MessageSchema(
            subject="Test Email - Nutrigence",
            recipients=[mail_username],  # Send to yourself
            body="""
            <html>
                <body>
                    <h2>Test Email</h2>
                    <p>This is a test email to verify your email configuration is working.</p>
                    <p>If you receive this, your magic link authentication should work!</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        # Send email
        fm = FastMail(mail_config)
        await fm.send_message(message)
        
        print("\n✅ Email sent successfully!")
        print("Check your inbox (and spam folder) for the test email.")
        return True
        
    except Exception as e:
        print(f"\n❌ Email test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your Gmail app password is correct")
        print("2. Make sure 2-factor authentication is enabled on your Gmail account")
        print("3. Verify the app password was generated for 'Mail'")
        print("4. Check your .env file has all required email settings")
        return False

if __name__ == "__main__":
    asyncio.run(test_email()) 