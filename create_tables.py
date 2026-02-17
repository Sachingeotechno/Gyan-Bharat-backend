from app.database import engine, Base
# Import all models to ensure they are registered with Base.metadata
from app.models.user import User, UserProfile
from app.models.course import Course, Lesson
from app.models.enrollment import Enrollment
from app.models.models_kyc import College, StandardCourse

def create_tables():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
