from app.models.user import User, UserProfile, UserSession
from app.models.course import Course, Lesson, CourseLevel
from app.models.enrollment import Enrollment
from app.models.subject import Subject
from app.models.module import Module
from app.models.question import Question
from app.models.user_test_attempt import UserTestAttempt
from app.models.daily_mcq import DailyMCQ
from app.models.lesson_progress import LessonProgress
from app.database import Base
from app.models.models_kyc import College, StandardCourse
from app.models.test import Test

# Export all models for Alembic migrations
__all__ = [
    "User", "UserProfile", "UserSession", "Base", "Course", "Lesson", 
    "Enrollment", "CourseLevel", "Subject", "Module", "Question", 
    "UserTestAttempt", "DailyMCQ", "LessonProgress",
    "Test", "College", "StandardCourse"
]
