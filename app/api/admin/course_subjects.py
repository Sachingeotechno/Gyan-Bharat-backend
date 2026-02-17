from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course, CourseSubject
from app.schemas.course import CourseSubjectCreate, CourseSubjectUpdate, CourseSubjectResponse
from app.dependencies import get_admin_user
from datetime import datetime

router = APIRouter(prefix="/admin/course-subjects", tags=["Admin - Course Subjects"])


@router.post("/", response_model=CourseSubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: CourseSubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new subject within a course (Admin only).
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == subject_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_subject = CourseSubject(
        course_id=subject_data.course_id,
        title=subject_data.title,
        description=subject_data.description,
        order=subject_data.order or 0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return new_subject


@router.get("/course/{course_id}", response_model=List[CourseSubjectResponse])
def get_course_subjects(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get all subjects for a specific course.
    """
    return db.query(CourseSubject).filter(CourseSubject.course_id == course_id).order_by(CourseSubject.order).all()


@router.put("/{subject_id}", response_model=CourseSubjectResponse)
def update_subject(
    subject_id: int,
    subject_data: CourseSubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update a subject (Admin only).
    """
    subject = db.query(CourseSubject).filter(CourseSubject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if subject_data.title is not None:
        subject.title = subject_data.title
    if subject_data.description is not None:
        subject.description = subject_data.description
    if subject_data.order is not None:
        subject.order = subject_data.order
    
    subject.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subject)
    
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a subject (Admin only).
    """
    subject = db.query(CourseSubject).filter(CourseSubject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    
    return None
