from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# =====================
# Subject Schemas
# =====================

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    course_id: Optional[int] = None


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[int] = None


class SubjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    course_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# =====================
# Module Schemas
# =====================

class ModuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject_id: Optional[int] = None
    order: int = 0


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject_id: Optional[int] = None
    order: Optional[int] = None


class ModuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    subject_id: Optional[int]
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


# =====================
# Question Schemas
# =====================

class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    module_id: Optional[int] = None
    difficulty: str = "medium"


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    module_id: Optional[int] = None
    difficulty: Optional[str] = None


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str]
    module_id: Optional[int]
    difficulty: str
    created_at: datetime

    class Config:
        from_attributes = True
