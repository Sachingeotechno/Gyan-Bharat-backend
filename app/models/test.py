from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TestType(str, enum.Enum):
    GRAND = "grand"
    MINI = "mini"
    SUBJECT = "subject"


class TestStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    ENDED = "ended"


class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses_kyc.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    test_type = Column(Enum(TestType), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    is_pro = Column(Boolean, default=False)
    is_mock = Column(Boolean, default=False)
    scheduled_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(TestStatus), default=TestStatus.UPCOMING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    standard_course = relationship("StandardCourse", back_populates="tests")
    subject = relationship("Subject", backref="tests")
    sessions = relationship("UserTestSession", back_populates="test", cascade="all, delete-orphan")
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Test {self.title}>"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class UserTestSession(Base):
    __tablename__ = "user_test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)  # Percentage
    total_questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    time_taken_minutes = Column(Integer, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.IN_PROGRESS)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="test_sessions")
    test = relationship("Test", back_populates="sessions")
    answers = relationship("UserTestAnswer", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserTestSession {self.id} - User {self.user_id}>"


class TestQuestion(Base):
    __tablename__ = "test_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    order = Column(Integer, default=0)
    marks = Column(Integer, default=1)
    
    # Relationships
    test = relationship("Test", back_populates="questions")
    question = relationship("Question")

    def __repr__(self):
        return f"<TestQuestion {self.id}>"


class UserTestAnswer(Base):
    __tablename__ = "user_test_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("user_test_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(String)  # 'A', 'B', 'C', 'D'
    is_correct = Column(Boolean)
    time_taken_seconds = Column(Integer, nullable=True)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("UserTestSession", back_populates="answers")
    question = relationship("Question")

    def __repr__(self):
        return f"<UserTestAnswer {self.id}>"
