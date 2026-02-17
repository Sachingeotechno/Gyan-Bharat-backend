"""
Migration script to update video URLs from /uploads/ to /static/
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.course import Lesson

def migrate_video_urls():
    """Update all lesson video URLs from /uploads/ to /static/"""
    db = SessionLocal()
    try:
        # Get all lessons with video URLs
        lessons = db.query(Lesson).filter(Lesson.video_url.isnot(None)).all()
        
        updated_count = 0
        for lesson in lessons:
            if lesson.video_url and '/uploads/' in lesson.video_url:
                old_url = lesson.video_url
                lesson.video_url = lesson.video_url.replace('/uploads/', '/static/')
                print(f"Updated lesson {lesson.id}: {old_url} -> {lesson.video_url}")
                updated_count += 1
        
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} lesson video URLs")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting video URL migration...")
    migrate_video_urls()
    print("Migration complete!")
