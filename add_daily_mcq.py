from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Question, DailyMCQ

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def add_daily_mcq():
    db = SessionLocal()
    try:
        # Check if today's MCQ already exists
        today = datetime.now().date()
        existing = db.query(DailyMCQ).filter(DailyMCQ.date == today).first()
        
        if existing:
            print(f"✅ Daily MCQ already exists for {today}")
            print(f"Question ID: {existing.question_id}")
            return
        
        # Get a random question that hasn't been used recently
        question = db.query(Question).filter(
            Question.id.notin_(
                db.query(DailyMCQ.question_id).filter(
                    DailyMCQ.date >= datetime.now().date()
                )
            )
        ).first()
        
        if not question:
            print("❌ No available questions found")
            return
        
        # Create new Daily MCQ entry
        daily_mcq = DailyMCQ(
            question_id=question.id,
            date=today
        )
        
        db.add(daily_mcq)
        db.commit()
        db.refresh(daily_mcq)
        
        print(f"✅ Daily MCQ created successfully!")
        print(f"Date: {daily_mcq.date}")
        print(f"Question ID: {daily_mcq.question_id}")
        print(f"Question: {question.question_text[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding Daily MCQ for today...")
    add_daily_mcq()
