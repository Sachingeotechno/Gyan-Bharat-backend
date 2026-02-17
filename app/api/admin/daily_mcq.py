from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.daily_mcq import DailyMCQ
from app.dependencies import get_admin_user
from datetime import datetime, timedelta, date
from typing import List
import random

router = APIRouter(prefix="/admin/daily-mcq", tags=["Admin - Daily MCQ"])


@router.post("/schedule-upcoming")
def schedule_upcoming_daily_mcqs(
    days: int = 20,
    course_id: int = None,  # Optional: if provided, schedule for specific course
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Schedule daily MCQs for the upcoming days (Admin only).
    Automatically selects random questions from the question bank.
    """
    if not course_id:
        raise HTTPException(
            status_code=400,
            detail="course_id is required to schedule daily MCQs"
        )
    
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
    
    # Get all available questions
    all_questions = db.query(Question).all()
    
    if not all_questions:
        raise HTTPException(status_code=404, detail="No questions available in the question bank")
    
    if len(all_questions) < days:
        raise HTTPException(
            status_code=400, 
            detail=f"Not enough questions. Need {days} questions but only {len(all_questions)} available"
        )
    
    # Get already scheduled dates for this course
    existing_mcqs = db.query(DailyMCQ).filter(
        DailyMCQ.date >= date.today(),
        DailyMCQ.course_id == course_id
    ).all()
    existing_dates = {mcq.date for mcq in existing_mcqs}
    used_question_ids = {mcq.question_id for mcq in existing_mcqs}
    
    # Filter out already used questions
    available_questions = [q for q in all_questions if q.id not in used_question_ids]
    
    # Shuffle questions for random selection
    random.shuffle(available_questions)
    
    scheduled_count = 0
    today = date.today()
    
    for day_offset in range(days):
        target_date = today + timedelta(days=day_offset)
        
        # Skip if already scheduled
        if target_date in existing_dates:
            continue
        
        # Check if we have questions left
        if scheduled_count >= len(available_questions):
            break
        
        # Create daily MCQ entry
        new_daily_mcq = DailyMCQ(
            question_id=available_questions[scheduled_count].id,
            course_id=course_id,
            date=target_date,
            created_at=datetime.utcnow()
        )
        
        db.add(new_daily_mcq)
        scheduled_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully scheduled {scheduled_count} daily MCQs for course {course_id}",
        "scheduled_count": scheduled_count,
        "course_id": course_id,
        "days_requested": days,
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=scheduled_count - 1)).isoformat() if scheduled_count > 0 else today.isoformat()
    }


@router.get("/scheduled")
def get_scheduled_daily_mcqs(
    days: int = 30,
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get list of scheduled daily MCQs (Admin only).
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    
    query = db.query(DailyMCQ).filter(
        DailyMCQ.date >= today,
        DailyMCQ.date < end_date
    )
    
    if course_id:
        query = query.filter(DailyMCQ.course_id == course_id)
        
    scheduled_mcqs = query.order_by(DailyMCQ.date).all()
    
    result = []
    for mcq in scheduled_mcqs:
        question = db.query(Question).filter(Question.id == mcq.question_id).first()
        if question:
            result.append({
                "id": mcq.id,
                "date": mcq.date.isoformat(),
                "question_id": mcq.question_id,
                "question_text": question.question_text,
                "difficulty": question.difficulty
            })
    
    return {
        "total": len(result),
        "scheduled_mcqs": result
    }


@router.delete("/{mcq_id}")
def delete_scheduled_mcq(
    mcq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a scheduled daily MCQ (Admin only).
    """
    mcq = db.query(DailyMCQ).filter(DailyMCQ.id == mcq_id).first()
    
    if not mcq:
        raise HTTPException(status_code=404, detail="Scheduled MCQ not found")
    
    db.delete(mcq)
    db.commit()
    
    return {"message": "Scheduled MCQ deleted successfully"}


@router.post("/schedule-specific")
def schedule_specific_daily_mcq(
    question_id: int,
    target_date: str,  # Format: YYYY-MM-DD
    course_id: int,  # Required: Course ID for the daily MCQ
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Schedule a specific question for a specific date (Admin only).
    """
    # Parse date
    try:
        mcq_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Check if question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if date already has a question for this course
    existing = db.query(DailyMCQ).filter(
        DailyMCQ.date == mcq_date,
        DailyMCQ.course_id == course_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Date {target_date} already has a scheduled question for this course"
        )
    
    # Create daily MCQ
    new_daily_mcq = DailyMCQ(
        question_id=question_id,
        course_id=course_id,
        date=mcq_date,
        created_at=datetime.utcnow()
    )
    
    db.add(new_daily_mcq)
    db.commit()
    db.refresh(new_daily_mcq)
    
    return {
        "message": "Daily MCQ scheduled successfully",
        "id": new_daily_mcq.id,
        "date": new_daily_mcq.date.isoformat(),
        "question_id": question_id,
        "course_id": course_id
    }
