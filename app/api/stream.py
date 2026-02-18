from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import StreamingResponse
import os
from pathlib import Path
from app.config import settings

router = APIRouter(prefix="/stream", tags=["Streaming"])

CHUNK_SIZE = 1024 * 1024  # 1MB chunks

@router.get("/video/{filename}")
async def stream_video(filename: str, request: Request, range: str = Header(None)):
    """
    Stream video file with support for Range requests (seeking).
    Now with efficient chunks and optimized generator.
    """
    safe_filename = os.path.basename(filename)
    # Search in multiple locations
    possible_paths = [
        Path("static") / "videos" / safe_filename,
        Path("static") / safe_filename,
    ]
    
    video_path = None
    for path in possible_paths:
        if path.exists():
            video_path = path
            break
            
    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = video_path.stat().st_size
    
    # Defaults
    start = 0
    end = file_size - 1
    
    # Larger chunk size for smoother playback (less HTTP overhead)
    # 3MB is a good balance for mobile
    MAX_CHUNK_SIZE = 3 * 1024 * 1024 

    if range:
        try:
            # Parse Range: bytes=0-   or bytes=0-1000
            parts = range.replace("bytes=", "").split("-")
            start = int(parts[0]) if parts[0] else 0
            
            # If end is specified, use it, otherwise default to full file (capped later)
            if len(parts) > 1 and parts[1]:
                end = int(parts[1])
            else:
                end = file_size - 1
                
            # Logic: If the client asked for a huge range (or open ended),
            # we restrict it to MAX_CHUNK_SIZE to enforce streaming/buffering
            if end - start >= MAX_CHUNK_SIZE:
                 end = start + MAX_CHUNK_SIZE - 1
            
            # Additional safety clamp
            end = min(end, file_size - 1)
            
        except ValueError:
             pass 

    content_length = end - start + 1

    # Efficient Generator: don't load 3MB into RAM at once
    def iterfile():
        with open(video_path, "rb") as f:
            f.seek(start)
            remaining = content_length
            while remaining > 0:
                # Read in small 64KB blocks to keep memory low
                read_size = min(64 * 1024, remaining)
                data = f.read(read_size)
                if not data:
                    break
                yield data
                remaining -= len(data)

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": "video/mp4",
    }

    return StreamingResponse(
        iterfile(),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers,
        media_type="video/mp4",
    )
