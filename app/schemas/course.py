from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.course import CourseLevel


# =====================
# Lesson Schemas
# =====================

class LessonCreate(BaseModel):
    course_id: int
    subject_id: Optional[int] = None # Added subject_id
    title: str
    description: Optional[str] = None
    content_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = 0
    order: Optional[int] = 0
    is_preview: bool = False


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[int] = None # Added subject_id
    content_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    order: Optional[int] = None
    is_preview: Optional[bool] = None


class LessonResponse(BaseModel):
    id: int
    course_id: int
    subject_id: Optional[int]
    title: str
    description: Optional[str]
    content_url: Optional[str]
    video_url: Optional[str]
    duration: int
    order: int
    is_preview: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# =====================
# Course Subject Schemas
# =====================

class CourseSubjectCreate(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    order: Optional[int] = 0


class CourseSubjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None


class CourseSubjectResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    order: int
    created_at: datetime
    updated_at: Optional[datetime]
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True


# =====================
# Course Schemas
# =====================

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int  # Required: Link to StandardCourse (courses_kyc)
    instructor_id: Optional[int] = None # Added for instructor selection
    price: float = 0.0
    cover_image: Optional[str] = None
    level: CourseLevel = CourseLevel.BEGINNER
    language: str = "English"
    is_published: bool = False


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructor_id: Optional[int] = None # Added for instructor selection
    price: Optional[float] = None
    cover_image: Optional[str] = None
    level: Optional[CourseLevel] = None
    language: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    instructor_id: Optional[int]
    course_id: int  # Link to StandardCourse
    price: float
    cover_image: Optional[str]
    level: CourseLevel
    language: str
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime]
    subjects: List[CourseSubjectResponse] = [] # Added subjects
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True
