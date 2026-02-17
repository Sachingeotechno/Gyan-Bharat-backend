from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from app.services.enrollment_service import EnrollmentService
from app.dependencies import get_current_user

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enroll current user in a course.
    """
    return EnrollmentService.enroll_user(db, current_user.id, enrollment_data.course_id)


@router.get("/", response_model=List[EnrollmentResponse])
def get_my_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all enrollments for current user.
    """
    return EnrollmentService.get_user_enrollments(db, current_user.id, skip, limit)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific enrollment details.
    """
    return EnrollmentService.get_enrollment(db, enrollment_id, current_user.id)


@router.patch("/{enrollment_id}/progress", response_model=EnrollmentResponse)
def update_progress(
    enrollment_id: int,
    progress_data: EnrollmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update enrollment progress.
    """
    if progress_data.progress is None:
        raise HTTPException(status_code=400, detail="Progress value required")
        
    return EnrollmentService.update_progress(db, enrollment_id, current_user.id, progress_data.progress)
