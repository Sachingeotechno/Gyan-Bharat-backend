"""
Seed script to populate Tests with sample data
- Creates Grand Tests, Mini Tests, and Subject Tests
- Sets up test questions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.test import Test, TestQuestion, TestType, TestStatus
from app.models.question import Question
from app.models.subject import Subject
from datetime import datetime, timedelta
import random

# Sample test data
TESTS_DATA = [
    {
        "title": "Grand Test 1 - INICET Pattern",
        "description": "Comprehensive test covering all subjects based on INICET pattern",
        "test_type": TestType.GRAND,
        "duration_minutes": 180,
        "total_questions": 200,
        "is_pro": True,
        "is_mock": False,
        "scheduled_date": datetime(2025, 9, 1, 10, 0),
        "end_date": datetime(2025, 9, 8, 23, 59),
        "status": TestStatus.ENDED
    },
    {
        "title": "Grand Test 2 - NEET Pattern",
        "description": "NEET PG pattern grand test with all subjects",
        "test_type": TestType.GRAND,
        "duration_minutes": 210,
        "total_questions": 200,
        "is_pro": True,
        "is_mock": False,
        "scheduled_date": datetime(2025, 9, 15, 10, 0),
        "end_date": datetime(2025, 9, 22, 23, 59),
        "status": TestStatus.ENDED
    },
    {
        "title": "NEET Recall 2025",
        "description": "Recall test based on NEET PG 2025 pattern",
        "test_type": TestType.GRAND,
        "duration_minutes": 210,
        "total_questions": 200,
        "is_pro": True,
        "is_mock": False,
        "scheduled_date": datetime(2025, 9, 25, 10, 0),
        "end_date": datetime(2025, 9, 29, 23, 59),
        "status": TestStatus.ENDED
    },
    {
        "title": "Grand Test 3 - INICET Pattern",
        "description": "Advanced level grand test for INICET preparation",
        "test_type": TestType.GRAND,
        "duration_minutes": 180,
        "total_questions": 200,
        "is_pro": True,
        "is_mock": False,
        "scheduled_date": datetime(2025, 10, 1, 10, 0),
        "end_date": datetime(2025, 10, 6, 23, 59),
        "status": TestStatus.ENDED
    },
    {
        "title": "National INI-CET Mock 2025 Nov Session",
        "description": "Full-length mock test simulating actual INI-CET exam",
        "test_type": TestType.GRAND,
        "duration_minutes": 180,
        "total_questions": 200,
        "is_pro": False,
        "is_mock": True,
        "scheduled_date": datetime(2025, 10, 15, 10, 0),
        "end_date": datetime(2025, 10, 22, 23, 59),
        "status": TestStatus.ENDED
    },
    {
        "title": "Mini Test 1 - Anatomy",
        "description": "Quick test on Anatomy fundamentals",
        "test_type": TestType.MINI,
        "duration_minutes": 30,
        "total_questions": 25,
        "is_pro": False,
        "is_mock": False,
        "scheduled_date": datetime(2025, 11, 1, 10, 0),
        "end_date": datetime(2025, 11, 7, 23, 59),
        "status": TestStatus.ONGOING
    },
    {
        "title": "Mini Test 2 - Physiology",
        "description": "Rapid fire questions on Physiology",
        "test_type": TestType.MINI,
        "duration_minutes": 30,
        "total_questions": 25,
        "is_pro": False,
        "is_mock": False,
        "scheduled_date": datetime(2025, 11, 10, 10, 0),
        "end_date": datetime(2025, 11, 17, 23, 59),
        "status": TestStatus.ONGOING
    },
    {
        "title": "Physics Subject Test",
        "description": "Comprehensive test on Physics concepts",
        "test_type": TestType.SUBJECT,
        "duration_minutes": 60,
        "total_questions": 50,
        "is_pro": False,
        "is_mock": False,
        "scheduled_date": datetime(2025, 11, 20, 10, 0),
        "end_date": datetime(2025, 11, 27, 23, 59),
        "status": TestStatus.UPCOMING
    },
    {
        "title": "Chemistry Subject Test",
        "description": "Test covering all Chemistry topics",
        "test_type": TestType.SUBJECT,
        "duration_minutes": 60,
        "total_questions": 50,
        "is_pro": False,
        "is_mock": False,
        "scheduled_date": datetime(2025, 12, 1, 10, 0),
        "end_date": datetime(2025, 12, 7, 23, 59),
        "status": TestStatus.UPCOMING
    }
]


def seed_tests():
    """Seed the database with sample tests"""
    db = SessionLocal()
    
    try:
        print("Starting Tests data seeding...")
        print("=" * 60)
        
        # Get all available questions
        all_questions = db.query(Question).all()
        
        if not all_questions:
            print("⚠️  No questions found in database. Please run seed_qbank.py first.")
            return
        
        total_tests = 0
        total_test_questions = 0
        
        for test_data in TESTS_DATA:
            # Check if test already exists
            existing_test = db.query(Test).filter(Test.title == test_data["title"]).first()
            
            if existing_test:
                print(f"✓ Test '{test_data['title']}' already exists")
                continue
            
            # Get subject_id if it's a subject test
            subject_id = None
            if test_data["test_type"] == TestType.SUBJECT:
                # Try to find matching subject
                subject_name = test_data["title"].split(" Subject Test")[0]
                subject = db.query(Subject).filter(Subject.name.ilike(f"%{subject_name}%")).first()
                if subject:
                    subject_id = subject.id
            
            # Create test
            new_test = Test(
                title=test_data["title"],
                description=test_data["description"],
                test_type=test_data["test_type"],
                subject_id=subject_id,
                duration_minutes=test_data["duration_minutes"],
                total_questions=test_data["total_questions"],
                is_pro=test_data["is_pro"],
                is_mock=test_data["is_mock"],
                scheduled_date=test_data["scheduled_date"],
                end_date=test_data["end_date"],
                status=test_data["status"],
                created_at=datetime.utcnow()
            )
            
            db.add(new_test)
            db.commit()
            db.refresh(new_test)
            total_tests += 1
            
            print(f"✓ Created test: {new_test.title} ({new_test.test_type})")
            
            # Add random questions to the test
            num_questions = min(test_data["total_questions"], len(all_questions))
            selected_questions = random.sample(all_questions, num_questions)
            
            for idx, question in enumerate(selected_questions):
                test_question = TestQuestion(
                    test_id=new_test.id,
                    question_id=question.id,
                    order=idx + 1,
                    marks=1
                )
                db.add(test_question)
                total_test_questions += 1
            
            db.commit()
            print(f"  ✓ Added {num_questions} questions to test")
        
        print("\n" + "=" * 60)
        print("✅ Tests seeding completed successfully!")
        print(f"\nSummary:")
        print(f"  • New Tests created: {total_tests}")
        print(f"  • Total Test Questions linked: {total_test_questions}")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_tests()
