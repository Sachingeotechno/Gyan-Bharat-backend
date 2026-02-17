from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)  # 'A', 'B', 'C', or 'D'
    explanation = Column(Text)
    difficulty = Column(String, default='medium')  # 'easy', 'medium', 'hard'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    module = relationship("Module", back_populates="questions")
    attempts = relationship("UserTestAttempt", back_populates="question", cascade="all, delete-orphan")
