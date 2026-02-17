from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.dependencies import get_current_user, get_admin_user
from datetime import datetime

router = APIRouter(prefix="/admin/courses", tags=["Admin - Courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new course (Admin only).
    """
    # Create course
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        course_id=course_data.course_id,  # Link to standard course
        instructor_id=course_data.instructor_id or current_user.id,  # Use provided instructor or fallback to current admin
        price=course_data.price if course_data.price is not None else 0.0,
        cover_image=course_data.cover_image,
        level=course_data.level if course_data.level else "beginner",
        language=course_data.language if course_data.language else "English",
        is_published=course_data.is_published if course_data.is_published is not None else False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update a course (Admin only).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update fields if provided
    if course_data.title is not None:
        course.title = course_data.title
    if course_data.description is not None:
        course.description = course_data.description
    if course_data.course_id is not None:
        course.course_id = course_data.course_id
    if course_data.instructor_id is not None:
        course.instructor_id = course_data.instructor_id
    if course_data.price is not None:
        course.price = course_data.price
    if course_data.cover_image is not None:
        course.cover_image = course_data.cover_image
    if course_data.level is not None:
        course.level = course_data.level
    if course_data.language is not None:
        course.language = course_data.language
    if course_data.is_published is not None:
        course.is_published = course_data.is_published
    
    course.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(course)
    
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a course (Admin only).
    This will also delete all associated enrollments, lessons, and progress.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Delete the course (cascade will handle lessons, enrollments, and progress)
    db.delete(course)
    db.commit()
    
    return None

