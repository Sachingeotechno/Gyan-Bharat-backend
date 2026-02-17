from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.course import Course, Lesson
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, LessonCreate, LessonUpdate


class CourseService:
    """Service class for course and lesson operations."""

    @staticmethod
    def get_courses(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        published_only: bool = True,
        course_id_filter: Optional[int] = None,
        language_filter: Optional[str] = None
    ) -> List[Course]:
        """
        Get list of courses.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            published_only: If True, only return published courses
            course_id_filter: If provided, only return courses for this StandardCourse
            language_filter: If provided, only return courses in this language
            
        Returns:
            List of course objects
        """
        query = db.query(Course)
        if published_only:
            query = query.filter(Course.is_published == True)
        if course_id_filter:
            query = query.filter(Course.course_id == course_id_filter)
        if language_filter:
            query = query.filter(Course.language == language_filter)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_course(db: Session, course_id: int) -> Optional[Course]:
        """
        Get course by ID.
        
        Args:
            db: Database session
            course_id: Course ID
            
        Returns:
            Course object or None
        """
        return db.query(Course).filter(Course.id == course_id).first()

    @staticmethod
    def create_course(db: Session, course_data: CourseCreate, instructor_id: int) -> Course:
        """
        Create a new course.
        """
        # Use instructor_id from course_data if provided, else use current_user.id
        final_instructor_id = course_data.instructor_id or instructor_id
        
        course = Course(
            title=course_data.title,
            description=course_data.description,
            course_id=course_data.course_id,
            instructor_id=final_instructor_id,
            price=course_data.price,
            cover_image=course_data.cover_image,
            level=course_data.level,
            language=course_data.language,
            is_published=course_data.is_published
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def update_course(db: Session, course_id: int, course_data: CourseUpdate, user: User) -> Course:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
        # Authorization: Admin or Owner
        if user.role != "admin" and course.instructor_id != user.id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this course")

        update_data = course_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def delete_course(db: Session, course_id: int, user: User):
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            
        # Authorization: Admin or Owner
        if user.role != "admin" and course.instructor_id != user.id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this course")

        db.delete(course)
        db.commit()

    # =====================
    # Lesson Operations
    # =====================

    @staticmethod
    def add_lesson(db: Session, course_id: int, lesson_data: LessonCreate, user: User) -> Lesson:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            
        # Authorization: Admin or Owner
        if user.role != "admin" and course.instructor_id != user.id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add lessons to this course")

        lesson = Lesson(
            **lesson_data.dict(),
            course_id=course_id
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return lesson

    @staticmethod
    def update_lesson(db: Session, course_id: int, lesson_id: int, lesson_data: LessonUpdate, user: User) -> Lesson:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.course_id == course_id).first()
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
            
        # Authorization: Admin or Owner
        if user.role != "admin" and lesson.course.instructor_id != user.id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this lesson")

        update_data = lesson_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lesson, field, value)

        db.commit()
        db.refresh(lesson)
        return lesson

    @staticmethod
    def delete_lesson(db: Session, course_id: int, lesson_id: int, user: User):
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.course_id == course_id).first()
        if not lesson:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
            
        # Authorization: Admin or Owner
        if user.role != "admin" and lesson.course.instructor_id != user.id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this lesson")
             
        db.delete(lesson)
        db.commit()
