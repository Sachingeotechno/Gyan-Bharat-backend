from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.dependencies import get_admin_user
from typing import List

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])

@router.get("/instructors", response_model=List[UserResponse])
def get_instructors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get all users with instructor role.
    """
    instructors = db.query(User).filter(User.role == UserRole.INSTRUCTOR).all()
    return instructors
