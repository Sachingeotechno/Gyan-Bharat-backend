from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Lesson
from app.schemas.course import LessonCreate, LessonUpdate, LessonResponse
from app.dependencies import get_admin_user
from datetime import datetime
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/admin/lessons", tags=["Admin - Lessons"])


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new lesson (Admin only).
    """
    new_lesson = Lesson(
        course_id=lesson_data.course_id,
        subject_id=lesson_data.subject_id, # Added subject_id
        title=lesson_data.title,
        description=lesson_data.description,
        content_url=lesson_data.content_url,
        video_url=lesson_data.video_url,
        duration=lesson_data.duration if lesson_data.duration is not None else 0,
        order=lesson_data.order if lesson_data.order is not None else 0,
        is_preview=lesson_data.is_preview if lesson_data.is_preview is not None else False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return new_lesson


@router.post("/{lesson_id}/video")
async def upload_lesson_video(
    lesson_id: int,
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Upload video for a lesson (Admin only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Validate file type
    if not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Create upload directory if it doesn't exist
    upload_dir = Path("static")
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(video.filename)[1]
    filename = f"{lesson_id}_{datetime.utcnow().timestamp()}{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    # Update lesson with video URL
    lesson.video_url = f"/static/{filename}"
    lesson.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lesson)
    
    return {"message": "Video uploaded successfully", "video_url": lesson.video_url}


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update a lesson (Admin only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Update fields if provided
    if lesson_data.title is not None:
        lesson.title = lesson_data.title
    if lesson_data.description is not None:
        lesson.description = lesson_data.description
    if lesson_data.subject_id is not None:
        lesson.subject_id = lesson_data.subject_id
    if lesson_data.content_url is not None:
        lesson.content_url = lesson_data.content_url
    if lesson_data.video_url is not None:
        lesson.video_url = lesson_data.video_url
    if lesson_data.duration is not None:
        lesson.duration = lesson_data.duration
    if lesson_data.order is not None:
        lesson.order = lesson_data.order
    if lesson_data.is_preview is not None:
        lesson.is_preview = lesson_data.is_preview
    
    lesson.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a lesson (Admin only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db.delete(lesson)
    db.commit()
    
    return None
