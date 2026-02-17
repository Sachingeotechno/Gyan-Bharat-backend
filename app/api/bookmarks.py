from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.bookmark import LessonBookmark
from app.models.course import Lesson
from app.models.user import User
from app.dependencies import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

# Pydantic models
class BookmarkCreate(BaseModel):
    lesson_id: int
    timestamp: int
    note: Optional[str] = None

class BookmarkResponse(BaseModel):
    id: int
    lesson_id: int
    timestamp: int
    note: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=BookmarkResponse)
def create_bookmark(
    bookmark: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bookmark for the current user."""
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == bookmark.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    new_bookmark = LessonBookmark(
        user_id=current_user.id,
        lesson_id=bookmark.lesson_id,
        timestamp=bookmark.timestamp,
        note=bookmark.note
    )
    
    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    return new_bookmark

@router.get("/lesson/{lesson_id}", response_model=List[BookmarkResponse])
def get_lesson_bookmarks(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookmarks for a specific lesson for the current user."""
    bookmarks = db.query(LessonBookmark).filter(
        LessonBookmark.user_id == current_user.id,
        LessonBookmark.lesson_id == lesson_id
    ).order_by(LessonBookmark.timestamp).all()
    
    return bookmarks

@router.delete("/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bookmark."""
    bookmark = db.query(LessonBookmark).filter(
        LessonBookmark.id == bookmark_id,
        LessonBookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    db.delete(bookmark)
    db.commit()
    return {"message": "Bookmark deleted successfully"}
