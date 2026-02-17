from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# =====================
# Authentication Schemas
# =====================

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    
    # @validator('password')
    # def validate_password(cls, v):
    #     """Validate password strength."""
    #     if not any(char.isdigit() for char in v):
    #         raise ValueError('Password must contain at least one digit')
    #     if not any(char.isupper() for char in v):
    #         raise ValueError('Password must contain at least one uppercase letter')
    #     if not any(char.islower() for char in v):
    #         raise ValueError('Password must contain at least one lowercase letter')
    #     return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for access token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


# =====================
# User Response Schemas
# =====================

class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    full_name: Optional[str]
    phone: Optional[str]
    date_of_birth: Optional[datetime]
    avatar_url: Optional[str]
    bio: Optional[str]
    country: Optional[str]
    timezone: Optional[str]
    language: str
    college_id: Optional[int]
    course_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: Optional[UserProfileResponse] = None
    
    class Config:
        from_attributes = True


# =====================
# User Update Schemas
# =====================

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[datetime] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)


class ChangePassword(BaseModel):
    """Schema for changing password."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str


# =====================
# Common Response Schemas
# =====================

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None
