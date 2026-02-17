from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
import shutil
import os
import uuid
from typing import Dict
from app.config import settings
from app.models.user import User, UserRole
from app.dependencies import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=Dict[str, str])
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file (Admin only).
    Returns file URL.
    """
    # Verify admin role
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload files"
        )

    # Validate file size (basic check, Nginx/Reverse proxy usually handles limit too)
    # This reads into memory, for large files better to stream, but for now simple write
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
        
    # Construct URL
    # Assuming backend is served at base URL, we serve uploads at /static/
    # In production, this should be an S3 URL or similar
    
    # If using local static files:
    base_url = f"http://{settings.HOST}:{settings.PORT}" 
    # Or rely on client to prepend base URL if returning relative path
    # Let's return full URL for simplicity
    
    # Correction: "http://0.0.0.0:8000" might be accessible inside container/local but 
    # for physical device it needs LAN IP.
    # Better to return relative path "/static/{unique_filename}" and let frontend prepend base URL
    
    return {"url": f"/static/{unique_filename}"}
