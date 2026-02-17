from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.course import Course, CourseLevel

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_courses():
    db = SessionLocal()
    try:
        print("Seeding bilingual courses...")
        
        # Clear existing courses for a clean state
        db.query(Course).delete()
        db.commit()

        courses_data = [
            # Class 6 - English (ID: 8)
            {
                "course_id": 8,
                "title": "Class 6 - Mathematics (English)",
                "description": "JNVST Class 6 Math syllabus in English. Covers Number System, Fractions, etc.",
                "price": 0.0,
                "level": CourseLevel.BEGINNER,
                "language": "English",
                "is_published": True,
                "cover_image": "https://img.freepik.com/free-vector/math-concept-illustration_114360-3914.jpg" 
            },
            {
                "course_id": 8,
                "title": "Class 6 - Mental Ability (English)",
                "description": "Master MAT for JNVST Class 6 in English medium.",
                "price": 0.0,
                "level": CourseLevel.BEGINNER,
                "language": "English",
                "is_published": True,
                "cover_image": "https://img.freepik.com/free-vector/logic-mind-concept-illustration_114360-9111.jpg"
            },
            # Class 6 - Hindi (ID: 8)
            {
                "course_id": 8,
                "title": "कक्षा 6 - गणित (हिंदी)",
                "description": "JNVST कक्षा 6 गणित पाठ्यक्रम हिंदी में। संख्या प्रणाली, भिन्न, आदि।",
                "price": 0.0,
                "level": CourseLevel.BEGINNER,
                "language": "Hindi",
                "is_published": True,
                "cover_image": "https://img.freepik.com/free-vector/math-concept-illustration_114360-3914.jpg" 
            },
            {
                "course_id": 8,
                "title": "कक्षा 6 - मानसिक क्षमता (हिंदी)",
                "description": "हिंदी माध्यम में JNVST कक्षा 6 के लिए MAT मास्टर करें।",
                "price": 0.0,
                "level": CourseLevel.BEGINNER,
                "language": "Hindi",
                "is_published": True,
                "cover_image": "https://img.freepik.com/free-vector/logic-mind-concept-illustration_114360-9111.jpg"
            },
            # Class 9 - English (ID: 9)
            {
                "course_id": 9,
                "title": "Class 9 - General Science (English)",
                "description": "JNVST Class 9 Science in English. Detailed Biology, Chemistry, and Physics.",
                "price": 0.0,
                "level": CourseLevel.INTERMEDIATE,
                "language": "English",
                "is_published": True,
                "cover_image": "https://img.freepik.com/free-vector/science-concept-illustration_114360-5714.jpg"
            },
            # Class 9 - Hindi (ID: 9)
            {
                "course_id": 9,
                "title": "कक्षा 9 - सामान्य विज्ञान (हिंदी)",
                "description": "हिंदी में JNVST कक्षा 9 विज्ञान। विस्तृत जीव विज्ञान, रसायन विज्ञान और भौतिकी।",
                "price": 0.0,
                "level": CourseLevel.INTERMEDIATE,
                "language": "Hindi",
                "is_published": True,
                "cover_image": "https://img.freepik.com/free-vector/science-concept-illustration_114360-5714.jpg"
            }
        ]

        for c_data in courses_data:
            course = Course(**c_data)
            db.add(course)
        
        db.commit()
        print("Successfully seeded bilingual courses.")
        
    except Exception as e:
        print(f"Error seeding courses: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_courses()
