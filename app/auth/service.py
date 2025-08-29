"""Authentication and security utilities"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings
from app.models import User


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(Exception):
    """Authentication related errors"""
    pass


class TokenManager:
    """Manage JWT tokens"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None


class GoogleAuthProvider:
    """Google OAuth authentication provider"""
    
    @staticmethod
    async def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and extract user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            # Check if token is issued by Google
            if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                raise AuthenticationError("Invalid token issuer")
            
            return {
                'google_id': idinfo.get('sub'),
                'email': idinfo.get('email'),
                'full_name': idinfo.get('name'),
                'avatar_url': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
        except Exception as e:
            raise AuthenticationError(f"Google token verification failed: {str(e)}")


class UserService:
    """User management service"""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_google_id(db: AsyncSession, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        result = await db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user_from_google(
        db: AsyncSession, 
        google_data: Dict[str, Any]
    ) -> User:
        """Create new user from Google OAuth data"""
        user = User(
            email=google_data['email'],
            full_name=google_data.get('full_name'),
            avatar_url=google_data.get('avatar_url'),
            google_id=google_data['google_id'],
            is_verified=google_data.get('email_verified', False),
            last_login=datetime.utcnow()
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update_user_login(db: AsyncSession, user: User) -> User:
        """Update user last login timestamp"""
        user.last_login = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user


class AuthService:
    """Main authentication service"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.google_auth = GoogleAuthProvider()
        self.user_service = UserService()
    
    async def authenticate_with_google(
        self, 
        db: AsyncSession, 
        google_token: str
    ) -> Dict[str, Any]:
        """Authenticate user with Google OAuth token"""
        # Verify Google token
        google_data = await self.google_auth.verify_google_token(google_token)
        
        # Check if user exists
        user = await self.user_service.get_user_by_google_id(
            db, google_data['google_id']
        )
        
        if not user:
            # Check if user exists with same email
            user = await self.user_service.get_user_by_email(
                db, google_data['email']
            )
            
            if user:
                # Link Google account to existing user
                user.google_id = google_data['google_id']
                await db.commit()
            else:
                # Create new user
                user = await self.user_service.create_user_from_google(
                    db, google_data
                )
        
        # Update last login
        await self.user_service.update_user_login(db, user)
        
        # Generate tokens
        access_token = self.token_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = self.token_manager.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "is_verified": user.is_verified,
                "is_premium": user.is_premium
            }
        }
    
    async def refresh_access_token(
        self, 
        db: AsyncSession, 
        refresh_token: str
    ) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        payload = self.token_manager.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        
        user_id = payload.get("sub")
        user = await self.user_service.get_user_by_id(db, user_id)
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Generate new access token
        access_token = self.token_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_current_user(
        self, 
        db: AsyncSession, 
        token: str
    ) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.token_manager.verify_token(token)
        
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.user_service.get_user_by_id(db, user_id)
        return user if user and user.is_active else None


# Initialize auth service
auth_service = AuthService()