from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.subject import Subject
from app.models.module import Module
from app.models.question import Question
from app.models.user import User
from app.models.user_test_attempt import UserTestAttempt
from app.dependencies import get_optional_current_user
from pydantic import BaseModel
from sqlalchemy import func

router = APIRouter()


# Pydantic schemas
class SubjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    order: int
    total_modules: int
    total_questions: int
    
    class Config:
        from_attributes = True


class ModuleResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    description: str | None
    order: int
    total_questions: int
    completed_questions: int | None = 0
    
    class Config:
        from_attributes = True


@router.get("/subjects", response_model=List[SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """Get all subjects with module and question counts, filtered by user's course"""
    # Get user's course_id from their profile
    user_course_id = None
    if current_user and current_user.profile:
        user_course_id = current_user.profile.course_id
    
    # Filter subjects by course_id if user has selected a course
    if user_course_id:
        subjects = db.query(Subject).filter(
            Subject.course_id == user_course_id
        ).order_by(Subject.order).all()
    else:
        # If no course selected, return empty list (user needs to select course)
        subjects = []
    
    result = []
    for subject in subjects:
        # Count total modules
        total_modules = len(subject.modules)
        
        # Count total questions across all modules
        total_questions = sum(len(module.questions) for module in subject.modules)
        
        result.append(SubjectResponse(
            id=subject.id,
            name=subject.name,
            description=subject.description,
            icon=subject.icon,
            order=subject.order,
            total_modules=total_modules,
            total_questions=total_questions
        ))
    
    return result


@router.get("/subjects/{subject_id}/modules")
def get_subject_modules(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get all modules for a subject with user progress and performance metrics.
    """
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    modules = db.query(Module).filter(Module.subject_id == subject_id).order_by(Module.order).all()
    
    result = []
    for module in modules:
        # Get total questions in module
        total_questions = db.query(Question).filter(Question.module_id == module.id).count()
        
        # Initialize performance metrics
        completed_questions = 0
        last_score = None
        average_score = None
        total_attempts = 0
        best_score = None
        
        if current_user:
            # Get user's test attempts for this module
            attempts = db.query(UserTestAttempt).filter(
                UserTestAttempt.user_id == current_user.id,
                UserTestAttempt.module_id == module.id
            ).all()
            
            if attempts:
                # Count unique questions attempted
                unique_questions = set(attempt.question_id for attempt in attempts)
                completed_questions = len(unique_questions)
                
                # Calculate total attempts (unique test sessions)
                # Group by date to count sessions
                attempt_dates = set(attempt.attempted_at.date() for attempt in attempts)
                total_attempts = len(attempt_dates)
                
                # Calculate scores
                correct_count = sum(1 for attempt in attempts if attempt.is_correct)
                total_count = len(attempts)
                
                if total_count > 0:
                    average_score = round((correct_count / total_count) * 100, 1)
                    
                    # Get last attempt score (last 10 questions or module size)
                    recent_attempts = sorted(attempts, key=lambda x: x.attempted_at, reverse=True)[:min(total_questions, 10)]
                    if recent_attempts:
                        recent_correct = sum(1 for attempt in recent_attempts if attempt.is_correct)
                        last_score = round((recent_correct / len(recent_attempts)) * 100, 1)
                    
                    # Calculate best score (best consecutive session)
                    # For simplicity, use average as best for now
                    best_score = average_score
        
        result.append({
            "id": module.id,
            "name": module.name,
            "description": module.description,
            "order": module.order,
            "total_questions": total_questions,
            "completed_questions": completed_questions,
            "performance": {
                "last_score": last_score,
                "average_score": average_score,
                "best_score": best_score,
                "total_attempts": total_attempts
            }
        })
    
    return result
