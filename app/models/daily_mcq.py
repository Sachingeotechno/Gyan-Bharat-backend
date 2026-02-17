from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class DailyMCQ(Base):
    __tablename__ = "daily_mcqs"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses_kyc.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('course_id', 'date', name='uq_daily_mcq_course_date'),
    )

    # Relationships
    standard_course = relationship("StandardCourse", back_populates="daily_mcqs")
    question = relationship("Question")
