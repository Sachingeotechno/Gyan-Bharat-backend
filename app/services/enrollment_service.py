from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.enrollment import Enrollment
from app.models.course import Course, Lesson
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate


class EnrollmentService:
    """Service class for enrollment and progress operations."""

    @staticmethod
    def enroll_user(db: Session, user_id: int, course_id: int) -> Enrollment:
        """
        Enroll a user in a course.
        
        Args:
            db: Database session
            user_id: User ID
            course_id: Course ID
            
        Returns:
            Created enrollment object
            
        Raises:
            HTTPException: If user is already enrolled or course not found
        """
        # Check if course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        # Check if already enrolled
        existing = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        
        if existing:
            # If already enrolled, just return the existing enrollment
            return existing

        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.utcnow(),
            progress=0.0,
            is_completed=False
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    @staticmethod
    def get_user_enrollments(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Enrollment]:
        """
        Get enrollments for a user with calculated progress based on watch time.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List of enrollments with calculated progress
        """
        from app.models.lesson_progress import LessonProgress
        
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == user_id)\
            .offset(skip).limit(limit).all()
        
        # Calculate progress for each enrollment based on watch time
        for enrollment in enrollments:
            # Get all lessons for this course
            lessons = db.query(Lesson).filter(Lesson.course_id == enrollment.course_id).all()
            
            if not lessons:
                enrollment.progress = 0.0
                continue
            
            total_progress = 0.0
            
            for lesson in lessons:
                # Get lesson progress
                lesson_prog = db.query(LessonProgress).filter(
                    LessonProgress.user_id == user_id,
                    LessonProgress.lesson_id == lesson.id
                ).first()
                
                if lesson_prog and lesson.duration > 0:
                    # Calculate percentage for this lesson
                    duration_seconds = lesson.duration * 60
                    watch_percentage = min((lesson_prog.watch_time / duration_seconds) * 100, 100)
                    total_progress += watch_percentage
                # If no progress or duration is 0, add 0%
            
            # Calculate average progress across all lessons
            enrollment.progress = round(total_progress / len(lessons), 2) if lessons else 0.0
        
        return enrollments

    @staticmethod
    def get_enrollment(db: Session, enrollment_id: int, user_id: int) -> Enrollment:
        """
        Get specific enrollment details.
        
        Args:
            db: Database session
            enrollment_id: Enrollment ID
            user_id: Requesting user ID (for security)
            
        Returns:
            Enrollment object
            
        Raises:
            HTTPException: If enrollment not found or not authorized
        """
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
            
        if enrollment.user_id != user_id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this enrollment")
             
        return enrollment

    @staticmethod
    def update_progress(db: Session, enrollment_id: int, user_id: int, progress: float) -> Enrollment:
        """
        Update learning progress.
        
        Args:
            db: Database session
            enrollment_id: Enrollment ID
            user_id: User ID
            progress: Progress percentage (0-100)
            
        Returns:
            Updated enrollment object
        """
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
            
        if enrollment.user_id != user_id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this enrollment")

        enrollment.progress = min(max(progress, 0.0), 100.0)
        enrollment.last_accessed_at = datetime.utcnow()
        
        if enrollment.progress >= 100.0 and not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.completed_at = datetime.utcnow()
            
        db.commit()
        db.refresh(enrollment)
        return enrollment
