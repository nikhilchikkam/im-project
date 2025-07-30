import os
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from itsdangerous import URLSafeTimedSerializer
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr

# Database connection
def get_db():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Magic Link Configuration
MAGIC_LINK_SECRET_KEY = os.getenv("MAGIC_LINK_SECRET_KEY", "magic-link-secret-key")
MAGIC_LINK_EXPIRE_MINUTES = 15

# Email Configuration
MAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@nutrigence.app"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

# OAuth Configuration
config = Config('.env')
oauth = OAuth(config)

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Apple OAuth
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY")

# Models
class User(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    business_id: Optional[str] = None
    auth_provider: str  # 'email', 'google', 'apple'
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

class MagicLinkRequest(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    business_id: Optional[str] = None

class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None

# JWT Token Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def create_magic_link_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(MAGIC_LINK_SECRET_KEY)
    return serializer.dumps(email, salt='magic-link')

def verify_magic_link_token(token: str, max_age: int = MAGIC_LINK_EXPIRE_MINUTES * 60) -> str:
    serializer = URLSafeTimedSerializer(MAGIC_LINK_SECRET_KEY)
    try:
        email = serializer.loads(token, salt='magic-link', max_age=max_age)
        return email
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or expired magic link: {str(e)}")

def get_user_by_email(db: Session, email: str) -> Optional[Dict[str, Any]]:
    try:
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
            row = result.fetchone()
            return dict(row._mapping) if row else None
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def create_user(db: Session, user_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            query = text("""
                INSERT INTO users (email, first_name, last_name, company_name, phone, business_id, auth_provider, is_verified, created_at, updated_at)
                VALUES (:email, :first_name, :last_name, :company_name, :phone, :business_id, :auth_provider, :is_verified, NOW(), NOW())
                RETURNING *
            """)
            result = db.execute(query, user_data)
            db.commit()
            row = result.fetchone()
            return dict(row._mapping)
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO users (email, first_name, last_name, company_name, phone, business_id, auth_provider, is_verified, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING *
            """, (
                user_data["email"], user_data["first_name"], user_data["last_name"],
                user_data["company_name"], user_data["phone"], user_data["business_id"],
                user_data["auth_provider"], user_data["is_verified"]
            ))
            row = cursor.fetchone()
            db.commit()
            return dict(row)
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

def update_user_verification(db: Session, email: str, is_verified: bool = True):
    try:
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            query = text("UPDATE users SET is_verified = :is_verified, updated_at = NOW() WHERE email = :email")
            db.execute(query, {"email": email, "is_verified": is_verified})
            db.commit()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("UPDATE users SET is_verified = %s, updated_at = NOW() WHERE email = %s", (is_verified, email))
            db.commit()
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user verification: {str(e)}")

async def send_magic_link_email(email: str, token: str):
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        magic_link = f"{frontend_url}/auth/verify?token={token}"
        
        mail = FastMail(MAIL_CONFIG)
        message = MessageSchema(
            subject="Your Magic Link - Nutrigence",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Welcome to Nutrigence!</h2>
                    <p>Click the link below to sign in to your account:</p>
                    <p><a href="{magic_link}">Sign In to Nutrigence</a></p>
                    <p>This link will expire in {MAGIC_LINK_EXPIRE_MINUTES} minutes.</p>
                    <p>If you didn't request this link, please ignore this email.</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        await mail.send_message(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            result = db.execute(text("SELECT * FROM users WHERE id = :user_id"), {"user_id": user_id})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="User not found")
            user_data = dict(row._mapping)
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="User not found")
            user_data = dict(row)
        
        return User(**user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> Optional[User]:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

def get_google_oauth_url():
    return f"https://accounts.google.com/oauth/authorize?client_id={GOOGLE_CLIENT_ID}&response_type=code&scope=email profile&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}"

def get_apple_oauth_url():
    return f"https://appleid.apple.com/auth/authorize?client_id={APPLE_CLIENT_ID}&response_type=code&scope=email name&redirect_uri={os.getenv('APPLE_REDIRECT_URI')}"

def create_users_table():
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
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
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users(auth_provider)")
        
        db.commit()
        db.close()
    except Exception as e:
        if 'db' in locals():
            db.close()
        raise HTTPException(status_code=500, detail=f"Failed to create users table: {str(e)}") 