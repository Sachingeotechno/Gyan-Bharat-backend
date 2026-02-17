from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    LessonCreate, LessonUpdate, LessonResponse
)
from app.services.course_service import CourseService
from app.dependencies import get_current_user, get_optional_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new course.
    """
    return CourseService.create_course(db, course_data, current_user.id)


@router.get("/", response_model=List[CourseResponse])
def get_courses(
    skip: int = 0,
    limit: int = 100,
    course_id: int = None,
    course_id_filter: int = None, # For backward compatibility
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get all courses filtered by user's course.
    Students only see courses for their selected course.
    Admins can filter by any course_id.
    """
    # Determine the filter ID
    filter_id = None
    lang_filter = None
    
    # If user is admin, allow explicit filtering
    if current_user and current_user.role == "admin":
        filter_id = course_id or course_id_filter
    # If user is student/logged-in, restrict to their profile course and language
    elif current_user and current_user.profile:
        filter_id = current_user.profile.course_id
        
        # Determine language filter based on user profile
        user_lang = current_user.profile.language
        lang_filter = None
        if user_lang == "hi":
            lang_filter = "Hindi"
        elif user_lang == "en":
            lang_filter = "English"
            
    return CourseService.get_courses(
        db, 
        skip, 
        limit, 
        published_only=True,
        course_id_filter=filter_id,
        language_filter=lang_filter
    )


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    Get course details.
    """
    course = CourseService.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a course.
    """
    return CourseService.update_course(db, course_id, course_data, current_user)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a course.
    """
    CourseService.delete_course(db, course_id, current_user)
    return None


# =====================
# Lesson Endpoints
# =====================

@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def add_lesson(
    course_id: int,
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a lesson to a course.
    """
    return CourseService.add_lesson(db, course_id, lesson_data, current_user)


@router.put("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    course_id: int,
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a lesson.
    """
    return CourseService.update_lesson(db, course_id, lesson_id, lesson_data, current_user)


@router.delete("/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    course_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a lesson.
    """
    CourseService.delete_lesson(db, course_id, lesson_id, current_user)
    return None
