from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CourseLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(Base):
    """Course model."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses_kyc.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    subtitle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    price = Column(Float, default=0.0)
    discount_price = Column(Float, default=0.0)
    offer_price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=False)
    validity_type = Column(String(50), default="lifetime") # lifetime, limited_days, fixed_date
    validity_days = Column(Integer, nullable=True) # For limited_days
    validity_date = Column(DateTime, nullable=True) # For fixed_date
    cover_image = Column(String(500), nullable=True)
    banner_image = Column(String(500), nullable=True)
    video_intro_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    level = Column(SQLEnum(CourseLevel), default=CourseLevel.BEGINNER)
    language = Column(String(50), default="English")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    standard_course = relationship("StandardCourse", back_populates="video_courses")
    instructor = relationship("User", backref="courses_taught")
    subjects = relationship("CourseSubject", back_populates="course", cascade="all, delete-orphan", order_by="CourseSubject.order")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan", order_by="Lesson.order")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.title}>"


class CourseSubject(Base):
    """Subject/Module within a video course."""
    __tablename__ = "course_subjects"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="subjects")
    lessons = relationship("Lesson", back_populates="subject", cascade="all, delete-orphan", order_by="Lesson.order")

    def __repr__(self):
        return f"<CourseSubject {self.title}>"


class Lesson(Base):
    """Lesson model."""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("course_subjects.id", ondelete="CASCADE"), nullable=True) # Linked to subject
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_url = Column(String(500), nullable=True)  # For documents/resources
    video_url = Column(String(500), nullable=True)
    duration = Column(Integer, default=0)  # In seconds
    order = Column(Integer, default=0)
    is_preview = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="lessons")
    subject = relationship("CourseSubject", back_populates="lessons")

    def __repr__(self):
        return f"<Lesson {self.title}>"
