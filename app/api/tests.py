from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app.models.user import User
from app.models.test import Test, UserTestSession, TestQuestion, UserTestAnswer, TestType, TestStatus, SessionStatus
from app.models.question import Question
from app.dependencies import get_current_user, get_optional_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/tests", tags=["Tests"])


# Schemas
class TestResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    test_type: str
    subject_id: Optional[int]
    duration_minutes: int
    total_questions: int
    is_pro: bool
    is_mock: bool
    scheduled_date: datetime
    end_date: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True


class TestSessionResponse(BaseModel):
    id: int
    test_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    score: Optional[int]
    total_questions_attempted: int
    correct_answers: int
    time_taken_minutes: Optional[int]
    status: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[dict])
def get_tests(
    test_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Get all tests with optional filters, filtered by user's course.
    Returns tests grouped by month.
    """
    # Get user's course_id from their profile
    user_course_id = None
    if current_user and current_user.profile:
        user_course_id = current_user.profile.course_id
    
    query = db.query(Test)
    
    # Filter by user's course_id if available
    if user_course_id:
        query = query.filter(Test.course_id == user_course_id)
    else:
        # If no course selected, return empty list
        return []
    
    if test_type:
        query = query.filter(Test.test_type == test_type)
    
    if status:
        query = query.filter(Test.status == status)
    
    tests = query.order_by(Test.scheduled_date.desc()).all()
    
    # Group tests by month
    grouped_tests = {}
    for test in tests:
        month_key = test.scheduled_date.strftime("%b").upper()
        year = test.scheduled_date.year
        month_year = f"{month_key} {year}"
        
        if month_year not in grouped_tests:
            grouped_tests[month_year] = []
        
        # Check if user has attempted this test
        user_session = None
        if current_user:
            user_session = db.query(UserTestSession).filter(
                UserTestSession.user_id == current_user.id,
                UserTestSession.test_id == test.id,
                UserTestSession.status == SessionStatus.COMPLETED
            ).first()
        
        grouped_tests[month_year].append({
            "id": test.id,
            "title": test.title,
            "description": test.description,
            "test_type": test.test_type,
            "duration_minutes": test.duration_minutes,
            "total_questions": test.total_questions,
            "is_pro": test.is_pro,
            "is_mock": test.is_mock,
            "scheduled_date": test.scheduled_date.isoformat(),
            "end_date": test.end_date.isoformat() if test.end_date else None,
            "status": test.status,
            "user_attempted": user_session is not None,
            "user_score": user_session.score if user_session else None
        })
    
    # Convert to list format
    result = []
    for month_year, tests_list in grouped_tests.items():
        result.append({
            "month_year": month_year,
            "tests": tests_list
        })
    
    return result


@router.get("/{test_id}", response_model=dict)
def get_test_details(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """Get detailed information about a specific test."""
    test = db.query(Test).filter(Test.id == test_id).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Get user's sessions for this test
    user_sessions = []
    if current_user:
        sessions = db.query(UserTestSession).filter(
            UserTestSession.user_id == current_user.id,
            UserTestSession.test_id == test_id
        ).order_by(UserTestSession.started_at.desc()).all()
        
        user_sessions = [{
            "id": session.id,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "score": session.score,
            "status": session.status
        } for session in sessions]
    
    return {
        "id": test.id,
        "title": test.title,
        "description": test.description,
        "test_type": test.test_type,
        "duration_minutes": test.duration_minutes,
        "total_questions": test.total_questions,
        "is_pro": test.is_pro,
        "is_mock": test.is_mock,
        "scheduled_date": test.scheduled_date.isoformat(),
        "end_date": test.end_date.isoformat() if test.end_date else None,
        "status": test.status,
        "user_sessions": user_sessions
    }


@router.post("/{test_id}/start", response_model=dict)
def start_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new test session."""
    test = db.query(Test).filter(Test.id == test_id).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if user already has an active session
    active_session = db.query(UserTestSession).filter(
        UserTestSession.user_id == current_user.id,
        UserTestSession.test_id == test_id,
        UserTestSession.status == SessionStatus.IN_PROGRESS
    ).first()
    
    if active_session:
        return {
            "session_id": active_session.id,
            "message": "Resuming existing session"
        }
    
    # Create new session
    new_session = UserTestSession(
        user_id=current_user.id,
        test_id=test_id,
        started_at=datetime.utcnow(),
        status=SessionStatus.IN_PROGRESS
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {
        "session_id": new_session.id,
        "test_id": test_id,
        "duration_minutes": test.duration_minutes,
        "total_questions": test.total_questions,
        "message": "Test session started successfully"
    }


@router.get("/progress/overall")
def get_overall_progress(
    test_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's overall progress in tests, optionally filtered by test type."""
    # Build query for completed sessions
    query = db.query(UserTestSession).filter(
        UserTestSession.user_id == current_user.id,
        UserTestSession.status == SessionStatus.COMPLETED
    )
    
    # If test_type is provided, join with Test table and filter
    if test_type:
        query = query.join(Test).filter(Test.test_type == test_type)
    
    completed_sessions = query.all()
    
    if not completed_sessions:
        return {
            "total_tests_taken": 0,
            "average_score": 0,
            "total_questions_attempted": 0,
            "total_correct_answers": 0,
            "accuracy": 0
        }
    
    total_tests = len(completed_sessions)
    total_score = sum(session.score for session in completed_sessions if session.score)
    total_questions = sum(session.total_questions_attempted for session in completed_sessions)
    total_correct = sum(session.correct_answers for session in completed_sessions)
    
    return {
        "total_tests_taken": total_tests,
        "average_score": round(total_score / total_tests, 1) if total_tests > 0 else 0,
        "total_questions_attempted": total_questions,
        "total_correct_answers": total_correct,
        "accuracy": round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0
    }


@router.get("/{test_id}/questions")
def get_test_questions(
    test_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions for a test session."""
    # Verify session belongs to user
    session = db.query(UserTestSession).filter(
        UserTestSession.id == session_id,
        UserTestSession.user_id == current_user.id,
        UserTestSession.test_id == test_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    # Get test questions
    test_questions = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).order_by(TestQuestion.order).all()
    
    questions_data = []
    for tq in test_questions:
        question = tq.question
        questions_data.append({
            "id": question.id,
            "question_text": question.question_text,
            "option_a": question.option_a,
            "option_b": question.option_b,
            "option_c": question.option_c,
            "option_d": question.option_d,
            "difficulty": question.difficulty,
            "order": tq.order
        })
    
    return {
        "session_id": session.id,
        "test_id": test_id,
        "questions": questions_data,
        "total_questions": len(questions_data)
    }


@router.post("/{test_id}/submit")
def submit_test(
    test_id: int,
    session_id: int,
    answers: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit test answers and calculate score."""
    # Verify session
    session = db.query(UserTestSession).filter(
        UserTestSession.id == session_id,
        UserTestSession.user_id == current_user.id,
        UserTestSession.test_id == test_id,
        UserTestSession.status == SessionStatus.IN_PROGRESS
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Active test session not found")
    
    # Get test questions
    test_questions = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).all()
    
    # Process answers
    correct_count = 0
    total_attempted = 0
    
    for tq in test_questions:
        question_id = str(tq.question_id)
        if question_id in answers.get("answers", {}):
            selected_answer = answers["answers"][question_id]
            total_attempted += 1
            
            # Get correct answer
            question = tq.question
            is_correct = selected_answer == question.correct_answer
            
            if is_correct:
                correct_count += 1
            
            # Save user answer
            user_answer = UserTestAnswer(
                session_id=session.id,
                question_id=tq.question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                answered_at=datetime.utcnow()
            )
            db.add(user_answer)
    
    # Calculate score
    score = round((correct_count / len(test_questions)) * 100, 1) if len(test_questions) > 0 else 0
    
    # Update session
    session.completed_at = datetime.utcnow()
    session.score = score
    session.total_questions_attempted = total_attempted
    session.correct_answers = correct_count
    session.time_taken_minutes = answers.get("time_taken_minutes", 0)
    session.status = SessionStatus.COMPLETED
    
    db.commit()
    
    return {
        "session_id": session.id,
        "score": score,
        "correct_answers": correct_count,
        "total_questions": len(test_questions),
        "total_attempted": total_attempted,
        "percentage": score
    }


@router.get("/{test_id}/results/{session_id}")
def get_test_results(
    test_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed test results with answers."""
    # Verify session
    session = db.query(UserTestSession).filter(
        UserTestSession.id == session_id,
        UserTestSession.user_id == current_user.id,
        UserTestSession.test_id == test_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    # Get user answers
    user_answers = db.query(UserTestAnswer).filter(
        UserTestAnswer.session_id == session_id
    ).all()
    
    # Build results
    results = []
    for answer in user_answers:
        question = answer.question
        results.append({
            "question_id": question.id,
            "question_text": question.question_text,
            "option_a": question.option_a,
            "option_b": question.option_b,
            "option_c": question.option_c,
            "option_d": question.option_d,
            "correct_answer": question.correct_answer,
            "selected_answer": answer.selected_answer,
            "is_correct": answer.is_correct,
            "explanation": question.explanation
        })
    
    # Get total questions in test
    total_questions_in_test = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).count()
    
    return {
        "session_id": session.id,
        "test_id": test_id,
        "score": session.score,
        "correct_answers": session.correct_answers,
        "total_questions": total_questions_in_test,
        "total_attempted": session.total_questions_attempted,
        "time_taken_minutes": session.time_taken_minutes,
        "results": results
    }
