from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(100), index=True, nullable=False)
    city = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<College {self.name}>"

class StandardCourse(Base):
    __tablename__ = "courses_kyc" # Renamed to avoid confusion with the content 'Course' model

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)

    # Relationships to content models
    subjects = relationship("Subject", back_populates="standard_course")
    tests = relationship("Test", back_populates="standard_course")
    daily_mcqs = relationship("DailyMCQ", back_populates="standard_course")
    video_courses = relationship("Course", back_populates="standard_course")

    def __repr__(self):
        return f"<StandardCourse {self.name}>"
