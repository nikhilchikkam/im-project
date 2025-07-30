#!/usr/bin/env python3
"""
Test authentication endpoint to isolate the issue
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from auth import get_current_user, User

router = APIRouter(prefix="/api/test-auth", tags=["test-auth"])

@router.get("/headers")
async def test_headers(request: Request):
    """Test to see what headers are being received"""
    print(f"🔍 Debug: test_headers called")
    print(f"🔍 Debug: Authorization header: {request.headers.get('authorization', 'NOT FOUND')}")
    print(f"🔍 Debug: All headers: {dict(request.headers)}")
    return {
        "authorization_header": request.headers.get('authorization', 'NOT FOUND'),
        "all_headers": dict(request.headers)
    }

@router.get("/simple")
async def test_auth_simple(current_user: User = Depends(get_current_user)):
    """Test if get_current_user works in a separate router"""
    print(f"🔍 Debug: test_auth_simple called for user {current_user.id} ({current_user.email})")
    return {
        "message": "Authentication works in separate router",
        "user_id": current_user.id,
        "user_email": current_user.email
    }

@router.get("/no-auth")
async def test_no_auth():
    """Test endpoint without authentication"""
    print("🔍 Debug: test_no_auth called")
    return {"message": "No auth endpoint works"} 