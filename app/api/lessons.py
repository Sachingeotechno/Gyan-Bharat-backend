from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.course import Lesson, Course
from app.models.lesson_progress import LessonProgress
from app.models.enrollment import Enrollment
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.course import LessonHistoryResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("/user/history", response_model=list[LessonHistoryResponse])
def get_user_history(
    completed: bool = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's watch history.
    - list of lessons with progress details.
    - filter by completed (optional).
    - sort by last_watched_at desc.
    """
    query = db.query(Lesson, LessonProgress).join(
        LessonProgress, Lesson.id == LessonProgress.lesson_id
    ).filter(
        LessonProgress.user_id == current_user.id
    )

    if completed is not None:
        query = query.filter(LessonProgress.completed == completed)

    # Sort by last watched
    results = query.order_by(LessonProgress.last_watched_at.desc()).limit(limit).all()

    history = []
    for lesson, progress in results:
        # Create a response object combining lesson and progress
        # We use the LessonHistoryResponse schema which inherits from LessonResponse
        
        # Manually construct to ensure all fields are mapped correctly
        item = LessonHistoryResponse(
            # Lesson fields
            id=lesson.id,
            course_id=lesson.course_id,
            subject_id=lesson.subject_id,
            title=lesson.title,
            description=lesson.description,
            content_url=lesson.content_url,
            video_url=lesson.video_url,
            duration=lesson.duration,
            order=lesson.order,
            is_preview=lesson.is_preview,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
            
            # Progress fields
            progress_completed=progress.completed,
            progress_watch_time=progress.watch_time,
            progress_last_position=progress.last_position,
            last_watched_at=progress.last_watched_at
        )
        history.append(item)

    return history


class UpdateProgressRequest(BaseModel):
    watch_time: int  # in seconds
    last_position: int = 0  # current playback position
    completed: bool = False


class LessonProgressResponse(BaseModel):
    lesson_id: int
    completed: bool
    watch_time: int
    last_position: int = 0  # Default to 0 if None
    last_watched_at: datetime


class CourseProgressResponse(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    progress_percentage: int
    lessons: list[LessonProgressResponse]


@router.post("/{lesson_id}/progress")
def update_lesson_progress(
    lesson_id: int,
    request: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update or create lesson progress for current user"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if progress record exists
    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    
    if progress:
        # Update existing
        progress.watch_time = request.watch_time
        progress.last_position = request.last_position
        progress.completed = request.completed
        progress.last_watched_at = datetime.utcnow()
    else:
        # Create new
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            course_id=lesson.course_id,
            watch_time=request.watch_time,
            last_position=request.last_position,
            completed=request.completed,
            last_watched_at=datetime.utcnow()
        )
        db.add(progress)
    
    db.commit()
    
    # Recalculate course progress
    update_course_progress(current_user.id, lesson.course_id, db)
    
    return {
        "success": True,
        "lesson_id": lesson_id,
        "completed": progress.completed,
        "watch_time": progress.watch_time
    }


@router.get("/course/{course_id}/progress", response_model=CourseProgressResponse)
def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get all lessons for this course
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
    total_lessons = len(lessons)
    
    # Get user's progress for these lessons
    lesson_progress_list = []
    completed_count = 0
    
    for lesson in lessons:
        progress = db.query(LessonProgress).filter(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson.id
        ).first()
        
        if progress:
            lesson_progress_list.append(LessonProgressResponse(
                lesson_id=lesson.id,
                completed=progress.completed,
                watch_time=progress.watch_time,
                last_position=progress.last_position or 0,
                last_watched_at=progress.last_watched_at
            ))
            if progress.completed:
                completed_count += 1
        else:
            lesson_progress_list.append(LessonProgressResponse(
                lesson_id=lesson.id,
                completed=False,
                watch_time=0,
                last_position=0,
                last_watched_at=datetime.utcnow()
            ))
    
    progress_percentage = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0
    
    return CourseProgressResponse(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_count,
        progress_percentage=progress_percentage,
        lessons=lesson_progress_list
    )


def update_course_progress(user_id: int, course_id: int, db: Session):
    """Helper function to recalculate and update enrollment progress"""
    # Get total lessons
    total_lessons = db.query(func.count(Lesson.id)).filter(Lesson.course_id == course_id).scalar()
    
    if total_lessons == 0:
        return
    
    # Get completed lessons
    completed_lessons = db.query(func.count(LessonProgress.id)).filter(
        LessonProgress.user_id == user_id,
        LessonProgress.course_id == course_id,
        LessonProgress.completed == True
    ).scalar()
    
    # Calculate percentage
    progress_percentage = int((completed_lessons / total_lessons) * 100)
    
    # Update enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    ).first()
    
    if enrollment:
        enrollment.progress = progress_percentage
        db.commit()
