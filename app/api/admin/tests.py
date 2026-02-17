from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import csv
import io
from app.database import get_db
from app.models.user import User
from app.models.test import Test, TestQuestion, TestType, TestStatus
from app.models.question import Question
from app.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/admin/tests", tags=["Admin Tests"])


# Schemas
class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    test_type: str
    course_id: int  # Required field
    subject_id: Optional[int] = None
    duration_minutes: int
    total_questions: int
    is_pro: bool = False
    is_mock: bool = False
    scheduled_date: datetime
    end_date: Optional[datetime] = None
    status: str = "upcoming"


class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"


def verify_admin(current_user: User):
    """Verify user is admin."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/")
def get_all_tests(
    test_type: Optional[str] = None,
    status: Optional[str] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tests for admin management."""
    verify_admin(current_user)
    
    query = db.query(Test)
    
    if test_type:
        query = query.filter(Test.test_type == test_type)
    if status:
        query = query.filter(Test.status == status)
    if course_id:
        query = query.filter(Test.course_id == course_id)
    
    tests = query.order_by(Test.created_at.desc()).all()
    
    return [{
        "id": test.id,
        "title": test.title,
        "description": test.description,
        "course_id": test.course_id,
        "test_type": test.test_type,
        "duration_minutes": test.duration_minutes,
        "total_questions": test.total_questions,
        "is_pro": test.is_pro,
        "is_mock": test.is_mock,
        "scheduled_date": test.scheduled_date.isoformat(),
        "end_date": test.end_date.isoformat() if test.end_date else None,
        "status": test.status,
        "created_at": test.created_at.isoformat()
    } for test in tests]


@router.post("/")
def create_test(
    test_data: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new test."""
    verify_admin(current_user)
    
    new_test = Test(
        title=test_data.title,
        description=test_data.description,
        test_type=test_data.test_type,
        course_id=test_data.course_id,  # Use course_id from request
        subject_id=test_data.subject_id,
        duration_minutes=test_data.duration_minutes,
        total_questions=test_data.total_questions,
        is_pro=test_data.is_pro,
        is_mock=test_data.is_mock,
        scheduled_date=test_data.scheduled_date,
        end_date=test_data.end_date,
        status=test_data.status
    )
    
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    
    return {
        "id": new_test.id,
        "message": "Test created successfully"
    }


@router.put("/{test_id}")
def update_test(
    test_id: int,
    test_data: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing test."""
    verify_admin(current_user)
    
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test.title = test_data.title
    test.description = test_data.description
    test.test_type = test_data.test_type
    test.course_id = test_data.course_id  # Update course_id
    test.subject_id = test_data.subject_id
    test.duration_minutes = test_data.duration_minutes
    test.total_questions = test_data.total_questions
    test.is_pro = test_data.is_pro
    test.is_mock = test_data.is_mock
    test.scheduled_date = test_data.scheduled_date
    test.end_date = test_data.end_date
    test.status = test_data.status
    
    db.commit()
    
    return {"message": "Test updated successfully"}


@router.delete("/{test_id}")
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a test."""
    verify_admin(current_user)
    
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Delete associated test questions
    db.query(TestQuestion).filter(TestQuestion.test_id == test_id).delete()
    
    # Delete the test
    db.delete(test)
    db.commit()
    
    return {"message": "Test deleted successfully"}


@router.get("/{test_id}/questions")
def get_test_questions_admin(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions for a test (admin view with answers)."""
    verify_admin(current_user)
    
    test_questions = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).order_by(TestQuestion.order).all()
    
    return [{
        "id": tq.question.id,
        "question_text": tq.question.question_text,
        "option_a": tq.question.option_a,
        "option_b": tq.question.option_b,
        "option_c": tq.question.option_c,
        "option_d": tq.question.option_d,
        "correct_answer": tq.question.correct_answer,
        "explanation": tq.question.explanation,
        "difficulty": tq.question.difficulty,
        "order": tq.order
    } for tq in test_questions]


@router.post("/{test_id}/questions")
def add_question_to_test(
    test_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a single question to a test manually."""
    verify_admin(current_user)
    
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Create the question
    new_question = Question(
        question_text=question_data.question_text,
        option_a=question_data.option_a,
        option_b=question_data.option_b,
        option_c=question_data.option_c,
        option_d=question_data.option_d,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        difficulty=question_data.difficulty
    )
    
    db.add(new_question)
    db.flush()
    
    # Get next order number
    max_order = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).count()
    
    # Link to test
    test_question = TestQuestion(
        test_id=test_id,
        question_id=new_question.id,
        order=max_order + 1
    )
    
    db.add(test_question)
    db.commit()
    
    return {
        "id": new_question.id,
        "message": "Question added successfully"
    }


@router.post("/{test_id}/questions/csv")
async def upload_questions_csv(
    test_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload questions from CSV file."""
    verify_admin(current_user)
    
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    # Read CSV
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    # Validate headers
    required_headers = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    if not all(header in csv_reader.fieldnames for header in required_headers):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain headers: {', '.join(required_headers)}"
        )
    
    # Get current max order
    max_order = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id
    ).count()
    
    questions_added = 0
    errors = []
    
    for i, row in enumerate(csv_reader, start=1):
        try:
            # Create question
            new_question = Question(
                question_text=row['question_text'],
                option_a=row['option_a'],
                option_b=row['option_b'],
                option_c=row['option_c'],
                option_d=row['option_d'],
                correct_answer=row['correct_answer'].upper(),
                explanation=row.get('explanation', ''),
                difficulty=row.get('difficulty', 'medium')
            )
            
            db.add(new_question)
            db.flush()
            
            # Link to test
            test_question = TestQuestion(
                test_id=test_id,
                question_id=new_question.id,
                order=max_order + questions_added + 1
            )
            
            db.add(test_question)
            questions_added += 1
            
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    
    db.commit()
    
    return {
        "questions_added": questions_added,
        "errors": errors,
        "message": f"Successfully added {questions_added} questions"
    }


@router.delete("/{test_id}/questions/{question_id}")
def remove_question_from_test(
    test_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a question from a test."""
    verify_admin(current_user)
    
    test_question = db.query(TestQuestion).filter(
        TestQuestion.test_id == test_id,
        TestQuestion.question_id == question_id
    ).first()
    
    if not test_question:
        raise HTTPException(status_code=404, detail="Question not found in test")
    
    db.delete(test_question)
    db.commit()
    
    return {"message": "Question removed from test"}
