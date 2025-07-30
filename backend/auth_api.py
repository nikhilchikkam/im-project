import os
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from auth import (
    get_db, create_magic_link_token, verify_magic_link_token, send_magic_link_email,
    create_access_token, create_refresh_token, get_user_by_email, create_user,
    update_user_verification, get_current_user, User, MagicLinkRequest, OAuthCallback,
    get_google_oauth_url, get_apple_oauth_url, create_users_table
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Initialize users table
create_users_table()

@router.post("/magic-link")
async def request_magic_link(request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Send a magic link to the user's email"""
    try:
        # Check if user exists - only allow existing users to login
        user = get_user_by_email(db, request.email)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="No account found with this email address. Please sign up first."
            )
        
        # Generate magic link token
        token = create_magic_link_token(request.email)
        
        # Check if email configuration is available
        mail_username = os.getenv("MAIL_USERNAME")
        mail_password = os.getenv("MAIL_PASSWORD")
        
        if not mail_username or not mail_password:
            # For testing purposes, return the token directly
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            magic_link = f"{frontend_url}/auth/verify?token={token}"
            return {
                "message": "Magic link generated (email not configured)",
                "email": request.email,
                "magic_link": magic_link,  # Only for testing!
                "token": token  # Only for testing!
            }
        
        # Send email
        await send_magic_link_email(request.email, token)
        
        return {
            "message": "Magic link sent to your email",
            "email": request.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send magic link: {str(e)}")

@router.post("/signup")
async def signup_user(request: MagicLinkRequest, db: Session = Depends(get_db)):
    """Create a new user account and send magic link"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=409, 
                detail="An account with this email address already exists. Please login instead."
            )
        
        # Create new user with provided data
        user_data = {
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "company_name": request.company_name,
            "phone": request.phone,
            "business_id": request.business_id,
            "auth_provider": "email",
            "is_verified": False
        }
        user = create_user(db, user_data)
        
        # Generate magic link token
        token = create_magic_link_token(request.email)
        
        # Send email
        await send_magic_link_email(request.email, token)
        
        return {
            "message": "Account created successfully! Magic link sent to your email.",
            "email": request.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")

@router.post("/verify")
async def verify_magic_link(request: dict, db: Session = Depends(get_db)):
    token = request.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    """Verify magic link and return JWT tokens"""
    try:
        # Verify token
        email = verify_magic_link_token(token)
        
        # Get or create user
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Mark user as verified
        update_user_verification(db, email, True)
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": str(user["id"])})
        refresh_token = create_refresh_token(data={"sub": str(user["id"])})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "company_name": user["company_name"],
                "is_verified": user["is_verified"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid magic link: {str(e)}")

@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        from auth import verify_token
        payload = verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify user exists
        user = get_user_by_email(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": str(user["id"])})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")

@router.get("/google/url")
async def get_google_oauth_url():
    """Get Google OAuth URL"""
    return {"url": get_google_oauth_url()}

@router.post("/google/callback")
async def google_oauth_callback(request: OAuthCallback, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "code": request.code,
                    "grant_type": "authorization_code",
                    "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI")
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
            
            tokens = token_response.json()
            access_token = tokens["access_token"]
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            user_info = user_response.json()
            
            # Get or create user
            user = get_user_by_email(db, user_info["email"])
            if not user:
                user_data = {
                    "email": user_info["email"],
                    "first_name": user_info.get("given_name"),
                    "last_name": user_info.get("family_name"),
                    "auth_provider": "google",
                    "is_verified": True
                }
                user = create_user(db, user_data)
            else:
                # Update existing user if needed
                if not user["is_verified"]:
                    update_user_verification(db, user_info["email"], True)
            
            # Create JWT tokens
            access_token = create_access_token(data={"sub": str(user["id"])})
            refresh_token = create_refresh_token(data={"sub": str(user["id"])})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "company_name": user["company_name"],
                    "is_verified": user["is_verified"]
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth failed: {str(e)}")

@router.get("/apple/url")
async def get_apple_oauth_url():
    """Get Apple OAuth URL"""
    return {"url": get_apple_oauth_url()}

@router.post("/apple/callback")
async def apple_oauth_callback(request: OAuthCallback, db: Session = Depends(get_db)):
    """Handle Apple OAuth callback"""
    try:
        # Apple OAuth implementation would go here
        # This is a simplified version - Apple OAuth requires additional setup
        # including JWT token generation and validation
        
        raise HTTPException(status_code=501, detail="Apple OAuth not yet implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apple OAuth failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "company_name": current_user.company_name,
        "phone": current_user.phone,
        "business_id": current_user.business_id,
        "auth_provider": current_user.auth_provider,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.post("/logout")
async def logout():
    """Logout user (client should discard tokens)"""
    return {"message": "Successfully logged out"}

@router.put("/profile")
async def update_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        body = await request.json()
        
        # Update user fields
        update_fields = {}
        allowed_fields = ["first_name", "last_name", "company_name", "phone", "business_id"]
        
        for field in allowed_fields:
            if field in body:
                update_fields[field] = body[field]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Build update query
        set_clause = ", ".join([f"{field} = :{field}" for field in update_fields.keys()])
        query = f"UPDATE users SET {set_clause}, updated_at = NOW() WHERE id = :user_id RETURNING *"
        
        update_fields["user_id"] = current_user.id
        
        from sqlalchemy import text
        result = db.execute(text(query), update_fields)
        db.commit()
        
        updated_user = dict(result.fetchone())
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": updated_user["id"],
                "email": updated_user["email"],
                "first_name": updated_user["first_name"],
                "last_name": updated_user["last_name"],
                "company_name": updated_user["company_name"],
                "phone": updated_user["phone"],
                "business_id": updated_user["business_id"],
                "auth_provider": updated_user["auth_provider"],
                "is_verified": updated_user["is_verified"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}") 