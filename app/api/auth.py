from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    MessageResponse,
    EmailVerification,
    PasswordResetRequest,
    PasswordReset,
    RefreshTokenRequest
)
from app.services.user_service import UserService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: User email address
    - **password**: Strong password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)
    - **full_name**: Optional full name
    
    Returns the created user with profile.
    """
    user = UserService.create_user(db, user_data)
    
    # TODO: Send verification email
    # send_verification_email(user.email, user.verification_token)
    
    return user


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    - **email**: User email
    - **password**: User password
    
    Returns access and refresh tokens.
    """
    user = UserService.authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get device info and IP address
    device_info = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    
    # Create tokens
    tokens = UserService.create_user_tokens(db, user, device_info, ip_address)
    
    return tokens


@router.post("/refresh", response_model=dict)
def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token.
    """
    tokens = UserService.refresh_access_token(db, refresh_request.refresh_token)
    return tokens


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """
    Verify user email with verification token.
    
    - **token**: Verification token sent via email
    """
    UserService.verify_email(db, verification.token)
    return {"message": "Email verified successfully"}


@router.post("/password-reset/request", response_model=MessageResponse)
def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset token.
    
    - **email**: User email address
    
    Sends reset token via email.
    """
    reset_token = UserService.request_password_reset(db, reset_request.email)
    
    # TODO: Send reset email
    # send_password_reset_email(reset_request.email, reset_token)
    
    return {"message": "Password reset email sent"}


@router.post("/password-reset/confirm", response_model=MessageResponse)
def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset password with reset token.
    
    - **token**: Password reset token
    - **new_password**: New password
    """
    UserService.reset_password(db, reset_data.token, reset_data.new_password)
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires authentication token.
    """
    return current_user
