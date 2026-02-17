from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class LessonBookmark(Base):
    """Model for storing user bookmarks in lessons."""
    __tablename__ = "lesson_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(Integer, nullable=False)  # Time in seconds
    note = Column(String(255), nullable=True)  # Optional note
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="bookmarks")
    lesson = relationship("Lesson", backref="bookmarks")

    def __repr__(self):
        return f"<LessonBookmark user={self.user_id} lesson={self.lesson_id} time={self.timestamp}>"
