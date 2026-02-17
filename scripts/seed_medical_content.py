import sys
import os
import random

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.database import Base, engine, SessionLocal
from app.models.models_kyc import StandardCourse
from app.models.subject import Subject
from app.models.module import Module
from app.models.question import Question
from app.models.test import Test, TestQuestion, UserTestSession, UserTestAnswer
from app.models.daily_mcq import DailyMCQ
from app.models.user_test_attempt import UserTestAttempt
from app.models.course import Course, CourseLevel
from app.models.enrollment import Enrollment
from app.models.lesson_progress import LessonProgress

# Setup DB connection
db = SessionLocal()

def seed_medical_content():
    print("WARNING: This script will delete ALL data from Content tables (Subjects, Tests, Questions, etc.)")
    print("This includes all student progress and enrollments related to these.")
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborting.")
        return

    print("--- Starting Seeding Process ---")

    try:
        # 1. Clear existing content in dependency order (Leaf -> Root)
        print("Deleting student progress (LessonProgress, Enrollments, Attempts)...")
        db.query(LessonProgress).delete()
        db.query(Enrollment).delete()
        db.query(UserTestAnswer).delete()
        db.query(UserTestSession).delete()
        db.query(UserTestAttempt).delete() # Practice attempts
        
        print("Deleting content structure (DailyMCQs, TestQuestions, Tests)...")
        db.query(DailyMCQ).delete()
        db.query(TestQuestion).delete()
        db.query(Test).delete()
        
        print("Deleting Question Bank (Questions, Modules)...")
        db.query(Question).delete()
        db.query(Module).delete()
        
        print("Deleting Video Courses...")
        db.query(Course).delete()
        
        print("Deleting Subjects...")
        db.query(Subject).delete()
        
        db.commit()
        print("Tables cleared.")

        # 2. Get all Standard Courses (KYC)
        standard_courses = db.query(StandardCourse).all()
        if not standard_courses:
            print("No Standard Courses found in 'courses_kyc'. Please seed them first.")
            return

        print(f"Found {len(standard_courses)} Standard Courses. Seeding content for each...")

        # 3. Define Medical Data
        medical_subjects = [
            {"name": "Anatomy", "desc": "Study of the structure of organisms and their parts.", "icon": "body"},
            {"name": "Physiology", "desc": "Study of normal function within living creatures.", "icon": "pulse"},
            {"name": "Biochemistry", "desc": "Study of chemical processes within and relating to living organisms.", "icon": "flask"},
            {"name": "Pathology", "desc": "Study of the causes and effects of disease or injury.", "icon": "medkit"},
            {"name": "Pharmacology", "desc": "Study of drug action and how medicines interact with biological systems.", "icon": "fitness"}, # Fixed icon
            {"name": "Microbiology", "desc": "Study of microscopic organisms.", "icon": "bug"},
            {"name": "Forensic Medicine", "desc": "Application of medical knowledge to the investigation of crime.", "icon": "finger-print"},
            {"name": "Community Medicine", "desc": "Branch of medicine concerned with the health of populations.", "icon": "people"}
        ]

        video_course_templates = [
            {"title": "Complete ${subject} Review", "price": 4999, "level": CourseLevel.ADVANCED},
            {"title": "Basics of ${subject}", "price": 999, "level": CourseLevel.BEGINNER},
            {"title": "${subject} Rapid Revision", "price": 1999, "level": CourseLevel.INTERMEDIATE}
        ]

        # 4. Loop and Seed
        for course_kyc in standard_courses:
            print(f"  -> Seeding for: {course_kyc.name}")
            
            selected_subject_data = medical_subjects[:5] 
            
            for i, subj_data in enumerate(selected_subject_data):
                # Create Subject
                subject = Subject(
                    course_id=course_kyc.id,
                    name=subj_data["name"],
                    description=subj_data["desc"],
                    icon=subj_data["icon"],
                    order=i
                )
                db.add(subject)
                db.flush() 

                # Create 1 Video Course
                template = video_course_templates[i % len(video_course_templates)]
                video_course = Course(
                    course_id=course_kyc.id,
                    title=template["title"].replace("${subject}", subj_data["name"]),
                    description=f"Comprehensive course on {subj_data['name']}.",
                    price=template["price"],
                    level=template["level"],
                    is_published=True,
                    cover_image="https://placehold.co/600x400/png" 
                )
                db.add(video_course)
                
                # Create 2 Modules per Subject
                for m in range(2):
                    module = Module(
                        subject_id=subject.id,
                        name=f"{subj_data['name']} - Module {m+1}",
                        description=f"Detailed study of {subj_data['name']} part {m+1}",
                        order=m
                    )
                    db.add(module)
                    db.flush()
                    
                    # Create 5 Questions per Module
                    for q in range(5):
                        question = Question(
                            module_id=module.id,
                            question_text=f"Question {q+1} for {module.name}?",
                            option_a="Option A",
                            option_b="Option B",
                            option_c="Option C",
                            option_d="Option D",
                            correct_answer=random.choice(['A', 'B', 'C', 'D']),
                            explanation="This is the correct explanation.",
                            difficulty=random.choice(['easy', 'medium', 'hard'])
                        )
                        db.add(question)
        
        db.flush()
        
        # 5. Schedule Daily MCQs for each Course
        print("Scheduling Daily MCQs...")
        from datetime import date, timedelta
        
        today = date.today()
        # Schedule for next 30 days
        days_to_schedule = 30
        
        for course_kyc in standard_courses:
            # Get all questions for this course
            course_questions = db.query(Question).join(Module).join(Subject).filter(Subject.course_id == course_kyc.id).all()
            
            if len(course_questions) < days_to_schedule:
                print(f"  Warning: Not enough questions to schedule {days_to_schedule} days for {course_kyc.name}. Scheduling {len(course_questions)} days.")
                questions_to_use = course_questions
            else:
                questions_to_use = random.sample(course_questions, days_to_schedule)
                
            for i, question in enumerate(questions_to_use):
                target_date = today + timedelta(days=i)
                daily_mcq = DailyMCQ(
                    question_id=question.id,
                    course_id=course_kyc.id,
                    date=target_date,
                    created_at=today
                )
                db.add(daily_mcq)
                
            print(f"  -> Scheduled Daily MCQs for: {course_kyc.name}")

        db.commit()
        print("--- Seeding Completed Successfully ---")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_medical_content()
