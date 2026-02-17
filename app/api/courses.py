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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get course details with lesson locking logic.
    - If enrolled: All lessons unlocked.
    - If not enrolled: Only first 3 lessons of first subject are unlocked.
    """
    course = CourseService.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check enrollment
    is_enrolled = False
    if current_user:
        # We need to import Enrollment inside to avoid circular imports if any, 
        # or better, do it at top level if safe. 
        # Checking local import first or assuming imports are clean.
        from app.models.enrollment import Enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id
        ).first()
        if enrollment:
            is_enrolled = True
            
    # Apply Lock Logic
    # Default: Lock everything first
    for lesson in course.lessons:
        lesson.is_locked = not is_enrolled
        if lesson.is_locked:
            lesson.video_url = None
            lesson.content_url = None

    if not is_enrolled:
        # Unlock logic for free tier
        # Find first subject
        subjects = sorted(course.subjects, key=lambda s: s.order)
        if subjects:
            first_subject = subjects[0]
            # Get lessons of first subject
            # We need to filter lessons that belong to this subject
            # Depending on how relationships are loaded, first_subject.lessons is best
            first_sub_lessons = sorted(first_subject.lessons, key=lambda l: l.order)
            
            # Unlock first 3
            for i, lesson in enumerate(first_sub_lessons):
                if i < 3:
                    lesson.is_locked = False
                    # No need to restore URL as it was not cleared for these if we handle order carefully
                    # actually we iterated course.lessons and locked ALL first.
                    # So we need to restore logic. 
                    # Wait, course.lessons might NOT be the same objects if accessed via course.lessons vs subject.lessons depending on session identity map. 
                    # But usually they are.
                    # However, if I set keys to None on course.lessons, they should be None on subject.lessons.
                    # So I just need to set is_locked = False. 
                    # BUT I need to ensure the URLs are available. 
                    # The original objects had them. 
                    # If I set them to None in the first loop, they are gone from the definition in memory!
                    # I cannot "restore" them unless I re-fetch or store them.
                    
    # REVISED LOGIC to avoid destroying data before knowing if it should be kept.
    
    # 1. Determine which IDs are unlocked.
    unlocked_ids = set()
    
    # Find first subject
    subjects = sorted(course.subjects, key=lambda s: s.order)
    if subjects:
        first_subject = subjects[0]
        first_sub_lessons = sorted(first_subject.lessons, key=lambda l: l.order)
        for i, lesson in enumerate(first_sub_lessons):
            if i < 3:
                unlocked_ids.add(lesson.id)
    else:
        # Fallback
        sorted_lessons = sorted(course.lessons, key=lambda l: l.order)
        for i, lesson in enumerate(sorted_lessons):
            if i < 3:
                unlocked_ids.add(lesson.id)

    # 2. Iterate and Apply
    # 2. Iterate and Apply
    for lesson in course.lessons:
        # Determine effective lock status
        # Store original DB value if needed, but here we can check order of operations
        # Priority:
        # 1. Enrolled -> Unlocked
        # 2. Preview -> Unlocked (Free for everyone)
        # 3. Explicit Lock (DB) -> Locked (for non-enrolled, overrides "First 3")
        # 4. First 3 -> Unlocked
        # 5. Default -> Locked
        
        db_is_locked = lesson.is_locked # Value from Database
        
        should_be_locked = True # Default to locked
        
        if is_enrolled:
            should_be_locked = False
        elif lesson.is_preview:
            should_be_locked = False
        elif db_is_locked:
            should_be_locked = True
        elif lesson.id in unlocked_ids:
            should_be_locked = False
        
        lesson.is_locked = should_be_locked
        
        if should_be_locked:
             lesson.video_url = None
             lesson.content_url = None
                 
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
