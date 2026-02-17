from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.question import Question
from app.models.module import Module
from app.models.user_test_attempt import UserTestAttempt
from app.models.user import User
from app.models.daily_mcq import DailyMCQ
from app.dependencies import get_current_user, get_optional_current_user
from pydantic import BaseModel
from datetime import date, datetime

router = APIRouter()


# Pydantic schemas
class QuestionResponse(BaseModel):
    id: int
    module_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str
    # Don't send correct_answer or explanation initially
    
    class Config:
        from_attributes = True


class QuestionWithAnswerResponse(BaseModel):
    id: int
    module_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: str | None
    difficulty: str
    
    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    selected_answer: str  # 'A', 'B', 'C', or 'D'
    time_taken: int | None = None  # seconds


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str | None
    selected_answer: str


class UserProgressResponse(BaseModel):
    total_questions_attempted: int
    total_correct: int
    total_incorrect: int
    accuracy: float
    subjects_progress: List[dict]


@router.get("/modules/{module_id}/questions", response_model=List[QuestionResponse])
def get_module_questions(module_id: int, db: Session = Depends(get_db)):
    """Get all questions for a module (without answers)"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    questions = db.query(Question).filter(Question.module_id == module_id).all()
    
    return [QuestionResponse(
        id=q.id,
        module_id=q.module_id,
        question_text=q.question_text,
        option_a=q.option_a,
        option_b=q.option_b,
        option_c=q.option_c,
        option_d=q.option_d,
        difficulty=q.difficulty
    ) for q in questions]


@router.post("/questions/{question_id}/attempt", response_model=SubmitAnswerResponse)
def submit_answer(
    question_id: int,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an answer for a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Use authenticated user
    user_id = current_user.id
    
    # Check if answer is correct
    is_correct = request.selected_answer.upper() == question.correct_answer.upper()
    
    # Save attempt
    attempt = UserTestAttempt(
        user_id=user_id,
        question_id=question_id,
        module_id=question.module_id,
        selected_answer=request.selected_answer.upper(),
        is_correct=is_correct,
        time_taken=request.time_taken,
        attempted_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    
    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        selected_answer=request.selected_answer.upper()
    )


@router.get("/daily-mcq", response_model=QuestionResponse)
def get_daily_mcq(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """Get today's daily MCQ for the user's course"""
    today = date.today()
    
    # Get user's course_id
    user_course_id = None
    if current_user and current_user.profile:
        user_course_id = current_user.profile.course_id
    
    # Filter by course_id if user has selected a course
    if user_course_id:
        daily_mcq = db.query(DailyMCQ).filter(
            DailyMCQ.date == today,
            DailyMCQ.course_id == user_course_id
        ).first()
    else:
        raise HTTPException(
            status_code=400, 
            detail="User must select a course to access daily MCQs"
        )
    
    if not daily_mcq:
        raise HTTPException(status_code=404, detail="No daily MCQ set for today for your course")
    
    question = db.query(Question).filter(Question.id == daily_mcq.question_id).first()
    
    return QuestionResponse(
        id=question.id,
        module_id=question.module_id,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        difficulty=question.difficulty
    )


@router.get("/daily-mcq/status")
def get_daily_mcq_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has already answered today's daily MCQ"""
    today = date.today()
    daily_mcq = db.query(DailyMCQ).filter(DailyMCQ.date == today).first()
    
    if not daily_mcq:
        raise HTTPException(status_code=404, detail="No daily MCQ set for today")
    
    # Use authenticated user
    user_id = current_user.id
    
    # Check if user already answered today
    attempt = db.query(UserTestAttempt).filter(
        UserTestAttempt.user_id == user_id,
        UserTestAttempt.question_id == daily_mcq.question_id,
        func.date(UserTestAttempt.attempted_at) == today
    ).first()
    
    if attempt:
        question = db.query(Question).filter(Question.id == daily_mcq.question_id).first()
        return {
            "answered": True,
            "selected_answer": attempt.selected_answer,
            "is_correct": attempt.is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation
        }
    
    return {
        "answered": False
    }


@router.post("/daily-mcq/attempt", response_model=SubmitAnswerResponse)
def submit_daily_mcq(
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answer for daily MCQ"""
    today = date.today()
    daily_mcq = db.query(DailyMCQ).filter(DailyMCQ.date == today).first()
    
    if not daily_mcq:
        raise HTTPException(status_code=404, detail="No daily MCQ set for today")
    
    question = db.query(Question).filter(Question.id == daily_mcq.question_id).first()
    user_id = current_user.id
    
    is_correct = request.selected_answer.upper() == question.correct_answer.upper()
    
    # Save attempt
    attempt = UserTestAttempt(
        user_id=user_id,
        question_id=question.id,
        module_id=question.module_id,
        selected_answer=request.selected_answer.upper(),
        is_correct=is_correct,
        time_taken=request.time_taken,
        attempted_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    
    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        selected_answer=request.selected_answer.upper()
    )
