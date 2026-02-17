from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token
from typing import Optional

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    token_data = decode_token(token)
    if token_data is None or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current user (must be verified).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current user (doesn't raise error if not authenticated).
    
    Args:
        credentials: HTTP Authorization credentials (optional)
        db: Database session
        
    Returns:
        Current user object or None if not authenticated
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data is None or token_data.user_id is None:
        return None
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    return user if user and user.is_active else None


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current user (must be ADMIN or INSTRUCTOR).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current admin user
        
    Raises:
        HTTPException: If user is not admin or instructor
    """
    if current_user.role.upper() not in ["ADMIN", "INSTRUCTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Instructor access required"
        )
    return current_user
