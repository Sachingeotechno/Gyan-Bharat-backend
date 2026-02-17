from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class UserTestAttempt(Base):
    __tablename__ = "user_test_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    selected_answer = Column(String)  # 'A', 'B', 'C', or 'D'
    is_correct = Column(Boolean)
    time_taken = Column(Integer)  # seconds
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question", back_populates="attempts")
    module = relationship("Module")
