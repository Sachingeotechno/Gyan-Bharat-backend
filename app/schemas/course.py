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
    is_locked: bool = False


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[int] = None # Added subject_id
    content_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    order: Optional[int] = None
    is_preview: Optional[bool] = None
    is_locked: Optional[bool] = None


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
    is_locked: bool = False

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
    subtitle: Optional[str] = None
    description: Optional[str] = None
    course_id: int  # Required: Link to StandardCourse (courses_kyc)
    instructor_id: Optional[int] = None
    price: float = 0.0
    discount_price: float = 0.0
    offer_price: float = 0.0
    is_free: bool = False
    validity_type: str = "lifetime"
    validity_days: Optional[int] = None
    validity_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    video_intro_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[str] = None
    level: CourseLevel = CourseLevel.BEGINNER
    language: str = "English"
    is_published: bool = False


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    instructor_id: Optional[int] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    offer_price: Optional[float] = None
    is_free: Optional[bool] = None
    validity_type: Optional[str] = None
    validity_days: Optional[int] = None
    validity_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    video_intro_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[str] = None
    level: Optional[CourseLevel] = None
    language: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(BaseModel):
    id: int
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    instructor_id: Optional[int]
    course_id: int
    price: float
    discount_price: float
    offer_price: float
    is_free: bool
    validity_type: str
    validity_days: Optional[int]
    validity_date: Optional[datetime]
    cover_image: Optional[str]
    banner_image: Optional[str]
    video_intro_url: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    tags: Optional[str]
    level: CourseLevel
    language: str
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime]
    subjects: List[CourseSubjectResponse] = [] # Added subjects
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True


class LessonHistoryResponse(LessonResponse):
    progress_completed: bool
    progress_watch_time: int
    progress_last_position: int
    last_watched_at: datetime
