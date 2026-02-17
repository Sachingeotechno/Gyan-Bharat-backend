from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    ChangePassword,
    MessageResponse
)
from app.services.user_service import UserService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    
    Requires authentication.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    - **full_name**: Full name
    - **phone**: Phone number
    - **date_of_birth**: Date of birth
    - **avatar_url**: Avatar image URL
    - **bio**: User biography
    - **country**: Country
    - **timezone**: Timezone
    - **language**: Preferred language
    
    Requires authentication.
    """
    UserService.update_profile(db, current_user, profile_data)
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password", response_model=MessageResponse)
def change_my_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password.
    
    - **old_password**: Current password
    - **new_password**: New password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)
    
    Requires authentication.
    """
    UserService.change_password(db, current_user, password_data)
    return {"message": "Password changed successfully"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user by ID (public profile).
    
    - **user_id**: User ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
