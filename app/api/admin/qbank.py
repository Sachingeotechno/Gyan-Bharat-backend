from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.module import Module
from app.models.question import Question
from app.dependencies import get_admin_user
from datetime import datetime
import json
import csv
from io import StringIO

router = APIRouter(prefix="/admin/qbank", tags=["Admin - QBank"])


# ============= SUBJECTS =============

@router.get("/subjects", response_model=List[dict])
def get_subjects(
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all subjects (Admin only), optionally filtered by course."""
    query = db.query(Subject)
    
    if course_id:
        query = query.filter(Subject.course_id == course_id)
        
    subjects = query.order_by(Subject.order).all()
    
    return [{
        "id": sub.id,
        "name": sub.name,
        "description": sub.description,
        "course_id": sub.course_id,
        "modules_count": len(sub.modules),
        "questions_count": sum(len(m.questions) for m in sub.modules)
    } for sub in subjects]


@router.post("/subjects", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new subject (Admin only)."""
    # Validate course_id is provided
    course_id = subject_data.get('course_id')
    if not course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="course_id is required"
        )
    
    new_subject = Subject(
        name=subject_data.get('name'),
        description=subject_data.get('description'),
        course_id=course_id,
        created_at=datetime.utcnow()
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return {
        "id": new_subject.id,
        "name": new_subject.name,
        "description": new_subject.description,
        "course_id": new_subject.course_id,
        "created_at": new_subject.created_at.isoformat()
    }


@router.put("/subjects/{subject_id}")
def update_subject(
    subject_id: int,
    name: str = None,
    description: str = None,
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a subject (Admin only)."""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if name is not None:
        subject.name = name
    if description is not None:
        subject.description = description
    if course_id is not None:
        subject.course_id = course_id
    
    db.commit()
    db.refresh(subject)
    
    return subject


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a subject (Admin only)."""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    
    return None


# ============= MODULES =============

@router.post("/modules", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_module(
    module_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new module (Admin only)."""
    new_module = Module(
        name=module_data.get('name'),
        description=module_data.get('description'),
        subject_id=module_data.get('subject_id'),
        order=module_data.get('order', 0),
        created_at=datetime.utcnow()
    )
    
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    
    return {
        "id": new_module.id,
        "name": new_module.name,
        "description": new_module.description,
        "subject_id": new_module.subject_id,
        "order": new_module.order,
        "created_at": new_module.created_at.isoformat()
    }


@router.put("/modules/{module_id}")
def update_module(
    module_id: int,
    name: str = None,
    description: str = None,
    subject_id: int = None,
    order: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a module (Admin only)."""
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    if name is not None:
        module.name = name
    if description is not None:
        module.description = description
    if subject_id is not None:
        module.subject_id = subject_id
    if order is not None:
        module.order = order
    
    db.commit()
    db.refresh(module)
    
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a module (Admin only)."""
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    db.delete(module)
    db.commit()
    
    return None


# ============= QUESTIONS =============

@router.post("/questions", status_code=status.HTTP_201_CREATED)
def create_question(
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new question (Admin only)."""
    correct_answer = question_data.get('correct_answer')
    if correct_answer not in ['A', 'B', 'C', 'D']:
        raise HTTPException(status_code=400, detail="Correct answer must be A, B, C, or D")
    
    new_question = Question(
        question_text=question_data.get('question_text'),
        option_a=question_data.get('option_a'),
        option_b=question_data.get('option_b'),
        option_c=question_data.get('option_c'),
        option_d=question_data.get('option_d'),
        correct_answer=correct_answer,
        explanation=question_data.get('explanation'),
        module_id=question_data.get('module_id'),
        difficulty=question_data.get('difficulty', 'medium'),
        created_at=datetime.utcnow()
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    return new_question


@router.put("/questions/{question_id}")
def update_question(
    question_id: int,
    question_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a question (Admin only)."""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    correct_answer = question_data.get('correct_answer')
    if correct_answer and correct_answer not in ['A', 'B', 'C', 'D']:
        raise HTTPException(status_code=400, detail="Correct answer must be A, B, C, or D")
    
    # Update fields if provided
    if 'question_text' in question_data:
        question.question_text = question_data['question_text']
    if 'option_a' in question_data:
        question.option_a = question_data['option_a']
    if 'option_b' in question_data:
        question.option_b = question_data['option_b']
    if 'option_c' in question_data:
        question.option_c = question_data['option_c']
    if 'option_d' in question_data:
        question.option_d = question_data['option_d']
    if 'correct_answer' in question_data:
        question.correct_answer = question_data['correct_answer']
    if 'explanation' in question_data:
        question.explanation = question_data['explanation']
    if 'difficulty' in question_data:
        question.difficulty = question_data['difficulty']
    
    db.commit()
    db.refresh(question)
    
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a question (Admin only)."""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    
    return None


# ============= BULK UPLOAD =============

@router.post("/questions/bulk")
async def bulk_upload_questions(
    file: UploadFile = File(...),
    module_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Bulk upload questions from CSV or JSON file (Admin only).
    
    CSV Format: question_text,option_a,option_b,option_c,option_d,correct_answer,explanation,difficulty
    JSON Format: [{"question_text": "...", "option_a": "...", ...}]
    """
    content = await file.read()
    
    questions_created = 0
    errors = []
    
    try:
        if file.filename.endswith('.json'):
            # Parse JSON
            data = json.loads(content.decode('utf-8'))
            
            for idx, item in enumerate(data):
                try:
                    question = Question(
                        question_text=item['question_text'],
                        option_a=item['option_a'],
                        option_b=item['option_b'],
                        option_c=item['option_c'],
                        option_d=item['option_d'],
                        correct_answer=item['correct_answer'],
                        explanation=item.get('explanation'),
                        module_id=item.get('module_id', module_id),
                        difficulty=item.get('difficulty', 'medium'),
                        created_at=datetime.utcnow()
                    )
                    db.add(question)
                    questions_created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
        
        elif file.filename.endswith('.csv'):
            # Parse CSV
            csv_content = StringIO(content.decode('utf-8'))
            reader = csv.DictReader(csv_content)
            
            for idx, row in enumerate(reader):
                try:
                    question = Question(
                        question_text=row['question_text'],
                        option_a=row['option_a'],
                        option_b=row['option_b'],
                        option_c=row['option_c'],
                        option_d=row['option_d'],
                        correct_answer=row['correct_answer'],
                        explanation=row.get('explanation'),
                        module_id=row.get('module_id', module_id),
                        difficulty=row.get('difficulty', 'medium'),
                        created_at=datetime.utcnow()
                    )
                    db.add(question)
                    questions_created += 1
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")  # +2 because of header
        
        else:
            raise HTTPException(status_code=400, detail="File must be .csv or .json")
        
        db.commit()
        
        return {
            "message": f"Successfully uploaded {questions_created} questions",
            "questions_created": questions_created,
            "errors": errors if errors else None
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
