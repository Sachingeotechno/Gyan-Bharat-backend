from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses_kyc.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)  # Icon name for UI
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    standard_course = relationship("StandardCourse", back_populates="subjects")
    modules = relationship("Module", back_populates="subject", cascade="all, delete-orphan")
