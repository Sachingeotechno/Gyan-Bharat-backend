from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.course import CourseResponse


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentUpdate(BaseModel):
    progress: Optional[float] = None
    is_completed: Optional[bool] = None


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    progress: float
    is_completed: bool
    completed_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    course: Optional[CourseResponse] = None

    class Config:
        from_attributes = True
