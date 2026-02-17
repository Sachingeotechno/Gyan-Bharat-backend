from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserProfile, UserSession, UserRole
from app.schemas.user import UserRegister, UserProfileUpdate, ChangePassword
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.helpers import generate_verification_token, generate_reset_token


class UserService:
    """Service class for user-related operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserRegister) -> User:
        """
        Create a new user with profile.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            verification_token=generate_verification_token(),
            role=UserRole.STUDENT
        )
        db.add(user)
        db.flush()  # Flush to get user ID
        
        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            full_name=user_data.full_name
        )
        db.add(profile)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def create_user_tokens(db: Session, user: User, device_info: Optional[str] = None, ip_address: Optional[str] = None) -> dict:
        """
        Create access and refresh tokens for a user.
        
        Args:
            db: Database session
            user: User object
            device_info: Device information (optional)
            ip_address: IP address (optional)
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
        
        # Store refresh token in database
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(session)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def verify_email(db: Session, token: str) -> User:
        """
        Verify user email with verification token.
        
        Args:
            db: Database session
            token: Verification token
            
        Returns:
            Verified user object
            
        Raises:
            HTTPException: If token is invalid
        """
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        user.is_verified = True
        user.verification_token = None
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> str:
        """
        Generate password reset token for user.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            Reset token
            
        Raises:
            HTTPException: If user not found
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate reset token
        reset_token = generate_reset_token()
        user.reset_password_token = reset_token
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        return reset_token
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> User:
        """
        Reset user password with reset token.
        
        Args:
            db: Database session
            token: Reset token
            new_password: New password
            
        Returns:
            User object
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        user = db.query(User).filter(User.reset_password_token == token).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Check if token is expired
        if user.reset_password_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_profile(db: Session, user: User, profile_data: UserProfileUpdate) -> UserProfile:
        """
        Update user profile.
        
        Args:
            db: Database session
            user: User object
            profile_data: Profile update data
            
        Returns:
            Updated profile object
        """
        profile = user.profile
        
        # Update fields if provided
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return profile
    
    @staticmethod
    def change_password(db: Session, user: User, password_data: ChangePassword) -> User:
        """
        Change user password.
        
        Args:
            db: Database session
            user: User object
            password_data: Password change data
            
        Returns:
            User object
            
        Raises:
            HTTPException: If old password is incorrect
        """
        # Verify old password
        if not verify_password(password_data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        # Update password
        user.password_hash = hash_password(password_data.new_password)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            Dictionary with new access_token
            
        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        # Find session with refresh token
        session = db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if token is expired
        if session.expires_at < datetime.now(timezone.utc):
            db.delete(session)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        
        # Get user
        user = session.user
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
