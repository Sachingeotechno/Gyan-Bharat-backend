from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.models_kyc import College, StandardCourse
from app.models.user import User, UserProfile
from app.dependencies import get_current_user

router = APIRouter()

# --- Schemas ---
class CollegeResponse(BaseModel):
    id: int
    name: str
    state: str
    city: Optional[str] = None

    class Config:
        orm_mode = True

class CourseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class KYCUpdateRequest(BaseModel):
    college_id: Optional[int] = None
    course_id: int
    language: Optional[str] = "en"

# --- Endpoints ---

@router.get("/colleges", response_model=List[CollegeResponse])
def get_colleges(state: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(College)
    if state:
        query = query.filter(College.state == state)
    if search:
        query = query.filter(College.name.ilike(f"%{search}%"))
    return query.all()

@router.get("/courses", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(StandardCourse).all()

@router.post("/users/kyc", status_code=status.HTTP_200_OK)
def update_kyc(
    kyc_data: KYCUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        # Create profile if it doesn't exist (should logically exist)
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Verify college if provided
    if kyc_data.college_id:
        college = db.query(College).filter(College.id == kyc_data.college_id).first()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        profile.college_id = kyc_data.college_id
        
    course = db.query(StandardCourse).filter(StandardCourse.id == kyc_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    profile.course_id = kyc_data.course_id
    if kyc_data.language:
        profile.language = kyc_data.language
    
    db.commit()
    return {"message": "KYC updated successfully"}
