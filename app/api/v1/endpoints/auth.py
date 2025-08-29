"""Authentication endpoints"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.auth.service import auth_service, AuthenticationError


router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Google authentication request"""
    token: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Authentication response"""
    access_token: str
    refresh_token: str
    token_type: str
    user: Dict[str, Any]


class RefreshResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str


@router.post("/google", response_model=TokenResponse)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with Google OAuth token
    
    - **token**: Google OAuth ID token
    """
    try:
        result = await auth_service.authenticate_with_google(
            db, request.token
        )
        return result
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    try:
        result = await auth_service.refresh_access_token(
            db, request.refresh_token
        )
        return result
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout():
    """
    Logout user (client should remove tokens)
    """
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user = Depends(auth_service.get_current_user)
):
    """
    Get current authenticated user information
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "is_verified": current_user.is_verified,
        "is_premium": current_user.is_premium,
        "preferred_language": current_user.preferred_language,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }